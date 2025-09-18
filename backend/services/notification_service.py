import os
import logging
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from sqlalchemy.orm import Session
from models import User, Notification, QuizResult, Quiz
from schemas import NotificationCreate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sendgrid_client = None
        self.twilio_client = None
        
        # Initialize SendGrid
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_key:
            self.sendgrid_client = SendGridAPIClient(api_key=sendgrid_key)
        
        # Initialize Twilio
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        if twilio_sid and twilio_token:
            self.twilio_client = Client(twilio_sid, twilio_token)
    
    def send_email(self, to_email: str, subject: str, content: str, html_content: str = None) -> bool:
        """Send email notification using SendGrid."""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured, skipping email notification")
            return False
        
        try:
            from_email = os.getenv("FROM_EMAIL", "noreply@quizsystem.com")
            
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=content,
                html_content=html_content
            )
            
            response = self.sendgrid_client.send(message)
            logger.info(f"Email sent successfully to {to_email}, status: {response.status_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification using Twilio."""
        if not self.twilio_client:
            logger.warning("Twilio not configured, skipping SMS notification")
            return False
        
        try:
            twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
            if not twilio_phone:
                logger.error("TWILIO_PHONE_NUMBER not configured")
                return False
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=twilio_phone,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully to {to_phone}, SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False
    
    def create_notification(self, db: Session, user_id: int, title: str, message: str, notification_type: str) -> Notification:
        """Create a notification record in the database."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    def notify_quiz_completed(self, db: Session, quiz_result: QuizResult) -> None:
        """Send notification when a quiz is completed."""
        try:
            # Get student information
            student = db.query(User).filter(User.id == quiz_result.student_id).first()
            if not student:
                return
            
            # Create notification record
            title = "Quiz Completed"
            message = f"You have completed the quiz with a score of {quiz_result.percentage:.1f}%"
            
            self.create_notification(
                db=db,
                user_id=student.id,
                title=title,
                message=message,
                notification_type="quiz_completed"
            )
            
            # Send email notification
            email_subject = f"Quiz Completed - {quiz_result.quiz.title}"
            email_content = f"""
            Hello {student.full_name},
            
            You have successfully completed the quiz: {quiz_result.quiz.title}
            
            Your Results:
            - Score: {quiz_result.total_score}/{quiz_result.max_score}
            - Percentage: {quiz_result.percentage:.1f}%
            - Time Taken: {quiz_result.time_taken // 60} minutes
            
            Thank you for taking the quiz!
            """
            
            html_content = f"""
            <html>
            <body>
                <h2>Quiz Completed Successfully!</h2>
                <p>Hello {student.full_name},</p>
                <p>You have successfully completed the quiz: <strong>{quiz_result.quiz.title}</strong></p>
                
                <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Your Results:</h3>
                    <ul>
                        <li><strong>Score:</strong> {quiz_result.total_score}/{quiz_result.max_score}</li>
                        <li><strong>Percentage:</strong> {quiz_result.percentage:.1f}%</li>
                        <li><strong>Time Taken:</strong> {quiz_result.time_taken // 60} minutes</li>
                    </ul>
                </div>
                
                <p>Thank you for taking the quiz!</p>
            </body>
            </html>
            """
            
            self.send_email(student.email, email_subject, email_content, html_content)
            
            logger.info(f"Quiz completion notification sent to student {student.id}")
            
        except Exception as e:
            logger.error(f"Failed to send quiz completion notification: {str(e)}")
    
    def notify_quiz_assigned(self, db: Session, quiz_id: int, student_ids: List[int]) -> None:
        """Send notification when a quiz is assigned to students."""
        try:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if not quiz:
                return
            
            for student_id in student_ids:
                student = db.query(User).filter(User.id == student_id).first()
                if not student:
                    continue
                
                # Create notification record
                title = "New Quiz Assigned"
                message = f"A new quiz '{quiz.title}' has been assigned to you"
                
                self.create_notification(
                    db=db,
                    user_id=student.id,
                    title=title,
                    message=message,
                    notification_type="quiz_assigned"
                )
                
                # Send email notification
                email_subject = f"New Quiz Assigned - {quiz.title}"
                email_content = f"""
                Hello {student.full_name},
                
                A new quiz has been assigned to you:
                
                Quiz: {quiz.title}
                Description: {quiz.description or 'No description available'}
                Time Limit: {quiz.time_limit} minutes
                Questions: {quiz.total_questions}
                
                Please log in to your account to take the quiz.
                """
                
                html_content = f"""
                <html>
                <body>
                    <h2>New Quiz Assigned!</h2>
                    <p>Hello {student.full_name},</p>
                    <p>A new quiz has been assigned to you:</p>
                    
                    <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>{quiz.title}</h3>
                        <p><strong>Description:</strong> {quiz.description or 'No description available'}</p>
                        <p><strong>Time Limit:</strong> {quiz.time_limit} minutes</p>
                        <p><strong>Questions:</strong> {quiz.total_questions}</p>
                    </div>
                    
                    <p>Please log in to your account to take the quiz.</p>
                </body>
                </html>
                """
                
                self.send_email(student.email, email_subject, email_content, html_content)
            
            logger.info(f"Quiz assignment notifications sent to {len(student_ids)} students")
            
        except Exception as e:
            logger.error(f"Failed to send quiz assignment notifications: {str(e)}")
    
    def notify_quiz_approved(self, db: Session, quiz_id: int, teacher_id: int) -> None:
        """Send notification when a quiz is approved."""
        try:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
            teacher = db.query(User).filter(User.id == teacher_id).first()
            
            if not quiz or not teacher:
                return
            
            # Create notification record
            title = "Quiz Approved"
            message = f"Your quiz '{quiz.title}' has been approved and is now available to students"
            
            self.create_notification(
                db=db,
                user_id=teacher.id,
                title=title,
                message=message,
                notification_type="quiz_approved"
            )
            
            # Send email notification
            email_subject = f"Quiz Approved - {quiz.title}"
            email_content = f"""
            Hello {teacher.full_name},
            
            Your quiz has been approved and is now available to students:
            
            Quiz: {quiz.title}
            Description: {quiz.description or 'No description available'}
            Questions: {quiz.total_questions}
            
            Students can now access and take this quiz.
            """
            
            html_content = f"""
            <html>
            <body>
                <h2>Quiz Approved!</h2>
                <p>Hello {teacher.full_name},</p>
                <p>Your quiz has been approved and is now available to students:</p>
                
                <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>{quiz.title}</h3>
                    <p><strong>Description:</strong> {quiz.description or 'No description available'}</p>
                    <p><strong>Questions:</strong> {quiz.total_questions}</p>
                </div>
                
                <p>Students can now access and take this quiz.</p>
            </body>
            </html>
            """
            
            self.send_email(teacher.email, email_subject, email_content, html_content)
            
            logger.info(f"Quiz approval notification sent to teacher {teacher.id}")
            
        except Exception as e:
            logger.error(f"Failed to send quiz approval notification: {str(e)}")
    
    def get_user_notifications(self, db: Session, user_id: int, limit: int = 50) -> List[Notification]:
        """Get notifications for a user."""
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_notification_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        
        return False
    
    def mark_all_notifications_read(self, db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        updated_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        return updated_count

# Global notification service instance
notification_service = NotificationService()
