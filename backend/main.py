from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base
from schemas import *
from auth import *
from ai_agent.quiz_generator import QuizGenerator
from services.notification_service import notification_service
from error_handlers import (
    create_quiz_not_found_error, 
    create_notification_not_found_error,
    custom_404_handler,
    custom_500_handler,
    custom_validation_handler
)
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Quiz System Agent",
    description="A comprehensive quiz management system with AI-powered content generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 error handler with user-friendly messages."""
    return await custom_404_handler(request, exc)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 error handler."""
    return await custom_500_handler(request, exc)

@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: Exception):
    """Custom validation error handler."""
    return await custom_validation_handler(request, exc)

# Initialize AI agent
quiz_generator = QuizGenerator()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI-Powered Quiz System Agent API", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/auth/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User management endpoints
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@app.put("/users/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# Quiz management endpoints
@app.post("/quizzes", response_model=Quiz)
async def create_quiz(
    quiz: QuizCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """Create a new quiz."""
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        creator_id=current_user.id,
        time_limit=quiz.time_limit
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@app.get("/quizzes", response_model=List[Quiz])
async def list_quizzes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List quizzes accessible to the current user."""
    if current_user.role in ["admin", "teacher"]:
        quizzes = db.query(Quiz).offset(skip).limit(limit).all()
    else:
        # Students can only see approved/active quizzes
        quizzes = db.query(Quiz).filter(
            Quiz.status.in_(["approved", "active"])
        ).offset(skip).limit(limit).all()
    
    return quizzes

@app.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific quiz by ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    # Check permissions
    if current_user.role == "student" and quiz.status not in ["approved", "active"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this quiz")
    
    return quiz

# AI-powered quiz generation endpoints
@app.post("/quizzes/generate")
async def generate_quiz_content(
    request: QuizGenerationRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """Generate quiz content using AI agent."""
    try:
        # Generate content using AI agent
        generated_content = quiz_generator.generate_quiz(
            title=request.title,
            description=request.description,
            subject=request.subject,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            time_limit=request.time_limit or 60
        )
        
        return {
            "status": "success",
            "generated_content": generated_content,
            "message": "Quiz content generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz content: {str(e)}"
        )

@app.post("/quizzes/{quiz_id}/approve")
async def approve_quiz(
    quiz_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """Approve a quiz for student access."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    if quiz.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to approve this quiz")
    
    quiz.status = "approved"
    db.commit()
    
    # Send notification to teacher
    notification_service.notify_quiz_approved(db, quiz_id, quiz.creator_id)
    
    return {"message": "Quiz approved successfully"}

# Question management endpoints
@app.get("/quizzes/{quiz_id}/questions", response_model=List[Question])
async def get_quiz_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all questions for a specific quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    return questions

# Quiz taking endpoints
@app.post("/quizzes/{quiz_id}/start")
async def start_quiz(
    quiz_id: int,
    current_user: User = Depends(require_role([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """Start taking a quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    if quiz.status != "active":
        raise HTTPException(status_code=400, detail="Quiz is not available for taking")
    
    # Check if student has already taken this quiz
    existing_result = db.query(QuizResult).filter(
        QuizResult.quiz_id == quiz_id,
        QuizResult.student_id == current_user.id
    ).first()
    
    if existing_result:
        raise HTTPException(status_code=400, detail="Quiz already completed")
    
    return {
        "quiz_id": quiz_id,
        "time_limit": quiz.time_limit,
        "total_questions": quiz.total_questions,
        "message": "Quiz started successfully"
    }

@app.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    answers: List[AnswerCreate],
    current_user: User = Depends(require_role([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and calculate results."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    # Calculate scores
    total_score = 0
    max_score = 0
    chapter_scores = {}
    topic_scores = {}
    subtopic_scores = {}
    
    for answer_data in answers:
        question = db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not question:
            continue
        
        max_score += question.points
        
        # Check if answer is correct
        is_correct = answer_data.answer_text.lower().strip() == question.correct_answer.lower().strip()
        if is_correct:
            total_score += question.points
        
        # Store answer
        answer = Answer(
            question_id=answer_data.question_id,
            student_id=current_user.id,
            answer_text=answer_data.answer_text,
            is_correct=is_correct,
            time_taken=answer_data.time_taken
        )
        db.add(answer)
        
        # Update chapter/topic/subtopic scores
        chapter_id = str(question.topic.chapter_id)
        topic_id = str(question.topic_id)
        subtopic_id = str(question.subtopic_id) if question.subtopic_id else None
        
        if chapter_id not in chapter_scores:
            chapter_scores[chapter_id] = {"score": 0, "max_score": 0}
        if topic_id not in topic_scores:
            topic_scores[topic_id] = {"score": 0, "max_score": 0}
        if subtopic_id and subtopic_id not in subtopic_scores:
            subtopic_scores[subtopic_id] = {"score": 0, "max_score": 0}
        
        chapter_scores[chapter_id]["max_score"] += question.points
        topic_scores[topic_id]["max_score"] += question.points
        if subtopic_id:
            subtopic_scores[subtopic_id]["max_score"] += question.points
        
        if is_correct:
            chapter_scores[chapter_id]["score"] += question.points
            topic_scores[topic_id]["score"] += question.points
            if subtopic_id:
                subtopic_scores[subtopic_id]["score"] += question.points
    
    # Calculate percentages
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    for chapter_id in chapter_scores:
        chapter_scores[chapter_id]["percentage"] = (
            chapter_scores[chapter_id]["score"] / chapter_scores[chapter_id]["max_score"] * 100
            if chapter_scores[chapter_id]["max_score"] > 0 else 0
        )
    
    for topic_id in topic_scores:
        topic_scores[topic_id]["percentage"] = (
            topic_scores[topic_id]["score"] / topic_scores[topic_id]["max_score"] * 100
            if topic_scores[topic_id]["max_score"] > 0 else 0
        )
    
    for subtopic_id in subtopic_scores:
        subtopic_scores[subtopic_id]["percentage"] = (
            subtopic_scores[subtopic_id]["score"] / subtopic_scores[subtopic_id]["max_score"] * 100
            if subtopic_scores[subtopic_id]["max_score"] > 0 else 0
        )
    
    # Create quiz result
    quiz_result = QuizResult(
        quiz_id=quiz_id,
        student_id=current_user.id,
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        time_taken=sum(answer.time_taken or 0 for answer in answers),
        chapter_scores=chapter_scores,
        topic_scores=topic_scores,
        subtopic_scores=subtopic_scores
    )
    db.add(quiz_result)
    db.commit()
    
    # Send notification to student
    notification_service.notify_quiz_completed(db, quiz_result)
    
    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "chapter_scores": chapter_scores,
        "topic_scores": topic_scores,
        "subtopic_scores": subtopic_scores,
        "message": "Quiz submitted successfully"
    }

# Analytics endpoints
@app.get("/quizzes/{quiz_id}/analytics")
async def get_quiz_analytics(
    quiz_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    results = db.query(QuizResult).filter(QuizResult.quiz_id == quiz_id).all()
    
    if not results:
        return {"message": "No results available for this quiz"}
    
    # Calculate analytics
    total_students = len(results)
    average_score = sum(result.percentage for result in results) / total_students
    
    # Chapter analytics
    chapter_analytics = {}
    for result in results:
        if result.chapter_scores:
            for chapter_id, scores in result.chapter_scores.items():
                if chapter_id not in chapter_analytics:
                    chapter_analytics[chapter_id] = {"scores": [], "max_scores": []}
                chapter_analytics[chapter_id]["scores"].append(scores["score"])
                chapter_analytics[chapter_id]["max_scores"].append(scores["max_score"])
    
    # Calculate averages for each chapter
    for chapter_id in chapter_analytics:
        scores = chapter_analytics[chapter_id]["scores"]
        max_scores = chapter_analytics[chapter_id]["max_scores"]
        chapter_analytics[chapter_id]["average_score"] = sum(scores) / len(scores)
        chapter_analytics[chapter_id]["average_max_score"] = sum(max_scores) / len(max_scores)
        chapter_analytics[chapter_id]["average_percentage"] = (
            chapter_analytics[chapter_id]["average_score"] / 
            chapter_analytics[chapter_id]["average_max_score"] * 100
            if chapter_analytics[chapter_id]["average_max_score"] > 0 else 0
        )
    
    return {
        "quiz_id": quiz_id,
        "total_students": total_students,
        "average_score": average_score,
        "chapter_analytics": chapter_analytics,
        "results": [
            {
                "student_id": result.student_id,
                "percentage": result.percentage,
                "total_score": result.total_score,
                "max_score": result.max_score,
                "completed_at": result.completed_at
            }
            for result in results
        ]
    }

# Notification endpoints
@app.get("/notifications", response_model=List[Notification])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get notifications for the current user."""
    notifications = notification_service.get_user_notifications(db, current_user.id, limit)
    return notifications

@app.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    success = notification_service.mark_notification_read(db, notification_id, current_user.id)
    if not success:
        raise create_notification_not_found_error(notification_id)
    return {"message": "Notification marked as read"}

@app.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    count = notification_service.mark_all_notifications_read(db, current_user.id)
    return {"message": f"{count} notifications marked as read"}

@app.post("/quizzes/{quiz_id}/assign")
async def assign_quiz_to_students(
    quiz_id: int,
    student_ids: List[int],
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEACHER])),
    db: Session = Depends(get_db)
):
    """Assign a quiz to specific students."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise create_quiz_not_found_error(quiz_id)
    
    if quiz.status != "approved":
        raise HTTPException(status_code=400, detail="Quiz must be approved before assigning")
    
    # Send notifications to students
    notification_service.notify_quiz_assigned(db, quiz_id, student_ids)
    
    return {"message": f"Quiz assigned to {len(student_ids)} students"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
