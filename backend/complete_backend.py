# complete_backend.py - Complete working backend with quiz submission
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Complete Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Models
class UserLogin(BaseModel):
    email: str
    password: str

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: list
    user_id: int

class QuizCreate(BaseModel):
    title: str
    description: str
    time_limit: int
    is_public: bool = True
    questions: list = []
    user_id: int = 1
    user_role: str = None

class QuizGenerationRequest(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: str
    num_questions: int
    time_limit: int = 60
    is_public: bool = True
    user_id: int = 1
    user_role: str = None

class SchoolRegistration(BaseModel):
    school_name: str
    school_type: str  # elementary, middle, high, university
    address: str
    city: str
    state: str
    country: str
    phone: str
    email: str
    principal_name: str
    established_year: Optional[str] = ""
    max_students: Optional[str] = ""
    max_teachers: Optional[str] = ""

class SchoolTeacherRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: str

class StudentCreationRequest(BaseModel):
    name: str
    email: str
    password: str
    school_id: str
    teacher_id: int

# In-memory storage
users_db = []
quizzes_db = []
quiz_results_db = []
schools_db = []
school_quizzes_db = {}  # school_id -> quizzes

# Security Functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, stored_hash = hashed_password.split(':')
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash
    except ValueError:
        return False

# Initialize super admin
def create_super_admin():
    """Create the super admin user if it doesn't exist"""
    super_admin_email = os.getenv('SUPER_ADMIN_EMAIL', 'hasanatk007@gmail.com')
    super_admin_password = os.getenv('SUPER_ADMIN_PASSWORD', 'Reshun@786')
    
    super_admin_exists = any(user.get('email') == super_admin_email for user in users_db)
    if not super_admin_exists:
        hashed_password = hash_password(super_admin_password)
        
        super_admin = {
            "id": 1,
            "name": "Super Admin",
            "email": super_admin_email,
            "password": hashed_password,
            "role": "super_admin",
            "created_at": datetime.now().isoformat()
        }
        users_db.insert(0, super_admin)
        print(f"Super Admin created: {super_admin_email}")

# Create super admin on startup
create_super_admin()

# Add sample quiz results for testing
def add_sample_quiz_results():
    """Add sample quiz results for testing analytics"""
    if not quiz_results_db:  # Only add if no results exist
        sample_results = [
            {
                "id": "sample_result_1",
                "quiz_id": "sample_quiz_1",
                "quiz_title": "Math Quiz",
                "user_id": 3,  # Student
                "score": 2,
                "max_score": 3,
                "percentage": 66.67,
                "grade": 1.0,
                "grade_letter": "D",
                "passed": True,
                "status": "PASSED",
                "question_results": [
                    {
                        "question_id": "q_1",
                        "question_text": "What is 2 + 2?",
                        "user_answer": "4",
                        "correct_answer": "4",
                        "is_correct": True,
                        "points_earned": 1,
                        "max_points": 1
                    },
                    {
                        "question_id": "q_2", 
                        "question_text": "What is 5 - 3?",
                        "user_answer": "2",
                        "correct_answer": "2",
                        "is_correct": True,
                        "points_earned": 1,
                        "max_points": 1
                    },
                    {
                        "question_id": "q_3",
                        "question_text": "What is 3 * 4?",
                        "user_answer": "10",
                        "correct_answer": "12",
                        "is_correct": False,
                        "points_earned": 0,
                        "max_points": 1
                    }
                ],
                "submitted_at": datetime.now().isoformat(),
                "message": "Quiz submitted successfully! You scored 66.67% and PASSED with grade D"
            },
            {
                "id": "sample_result_2",
                "quiz_id": "sample_quiz_2",
                "quiz_title": "General Knowledge",
                "user_id": 3,  # Student
                "score": 2,
                "max_score": 2,
                "percentage": 100.0,
                "grade": 4.0,
                "grade_letter": "A+",
                "passed": True,
                "status": "PASSED",
                "question_results": [
                    {
                        "question_id": "q_1",
                        "question_text": "What is the capital of France?",
                        "user_answer": "Paris",
                        "correct_answer": "Paris",
                        "is_correct": True,
                        "points_earned": 1,
                        "max_points": 1
                    },
                    {
                        "question_id": "q_2",
                        "question_text": "What is 2 + 2?",
                        "user_answer": "4",
                        "correct_answer": "4",
                        "is_correct": True,
                        "points_earned": 1,
                        "max_points": 1
                    }
                ],
                "submitted_at": datetime.now().isoformat(),
                "message": "Quiz submitted successfully! You scored 100.0% and PASSED with grade A+"
            }
        ]
        
        for result in sample_results:
            quiz_results_db.append(result)
        
        print("✅ Sample quiz results added for testing")

# Add sample quiz results on startup
add_sample_quiz_results()

# Add sample quizzes
sample_quizzes = [
    {
        "id": "sample_quiz_1",
        "title": "Math Quiz",
        "description": "Basic math questions",
        "time_limit": 30,
        "is_public": True,
        "created_by": 1,
        "created_at": datetime.utcnow().isoformat(),
        "total_questions": 3,
        "total_points": 3,
        "created_by_admin": True,
        "questions": [
            {
                "id": "q_1",
                "question_text": "What is 2 + 2?",
                "question_type": "multiple_choice",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "explanation": "2 + 2 = 4",
                "difficulty": "easy",
                "points": 1
            },
            {
                "id": "q_2",
                "question_text": "What is 5 × 3?",
                "question_type": "multiple_choice",
                "options": ["12", "15", "18", "20"],
                "correct_answer": "15",
                "explanation": "5 × 3 = 15",
                "difficulty": "easy",
                "points": 1
            },
            {
                "id": "q_3",
                "question_text": "What is 10 ÷ 2?",
                "question_type": "multiple_choice",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "5",
                "explanation": "10 ÷ 2 = 5",
                "difficulty": "easy",
                "points": 1
            }
        ]
    },
    {
        "id": "sample_quiz_2",
        "title": "General Knowledge",
        "description": "General knowledge questions",
        "time_limit": 45,
        "is_public": True,
        "created_by": 1,
        "created_at": datetime.utcnow().isoformat(),
        "total_questions": 2,
        "total_points": 2,
        "created_by_admin": True,
        "questions": [
            {
                "id": "q_1",
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "Paris",
                "explanation": "Paris is the capital of France",
                "difficulty": "easy",
                "points": 1
            },
            {
                "id": "q_2",
                "question_text": "What is the largest planet in our solar system?",
                "question_type": "multiple_choice",
                "options": ["Earth", "Jupiter", "Saturn", "Neptune"],
                "correct_answer": "Jupiter",
                "explanation": "Jupiter is the largest planet in our solar system",
                "difficulty": "medium",
                "points": 1
            }
        ]
    }
]

for quiz in sample_quizzes:
    quizzes_db.append(quiz)

@app.get("/")
def read_root():
    return {"message": "Complete Quiz System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/api/login")
def login_user(user: UserLogin):
    # Find user
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            stored_password = existing_user["password"]
            
            # Check if password is hashed or plain text
            if ':' in stored_password:
                if verify_password(user.password, stored_password):
                    return {
                        "message": "Login successful",
                        "user": {
                            "id": existing_user["id"],
                            "name": existing_user["name"],
                            "email": existing_user["email"],
                            "role": existing_user["role"],
                            "school_id": existing_user.get("school_id")
                        }
                    }
            else:
                if stored_password == user.password:
                    existing_user["password"] = hash_password(user.password)
                    return {
                        "message": "Login successful",
                        "user": {
                            "id": existing_user["id"],
                            "name": existing_user["name"],
                            "email": existing_user["email"],
                            "role": existing_user["role"],
                            "school_id": existing_user.get("school_id")
                        }
                    }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/api/quizzes")
def get_quizzes(user_id: int = None):
    return {"quizzes": quizzes_db, "total": len(quizzes_db)}

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"quiz": quiz}

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission_data: QuizSubmission):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    total_score = 0
    max_score = 0
    answers = submission_data.answers
    user_id = submission_data.user_id
    
    # Track correct/incorrect answers for detailed results
    question_results = []
    
    for i, answer in enumerate(answers):
        question_id = f"q_{i+1}"
        user_answer = answer if isinstance(answer, str) else str(answer)
        
        # Find question - handle both cases: with ID and without ID
        question = None
        if i < len(quiz["questions"]):
            # Use question by index for manual quizzes (which don't have IDs)
            question = quiz["questions"][i]
            # Try to find by ID first for AI-generated quizzes
            question_by_id = next((q for q in quiz["questions"] if q.get("id") == question_id), None)
            if question_by_id:
                question = question_by_id
        if question:
            points = question.get("points", 1)
            max_score += points
            is_correct = user_answer == question.get("correct_answer")
            
            if is_correct:
                total_score += points
            
            question_results.append({
                "question_id": question.get("id", question_id),
                "question_text": question.get("question_text", ""),
                "user_answer": user_answer,
                "correct_answer": question.get("correct_answer", ""),
                "is_correct": is_correct,
                "points_earned": points if is_correct else 0,
                "max_points": points
            })
    
    percentage = round((total_score / max_score * 100), 2) if max_score > 0 else 0
    
    # Determine grade and pass/fail
    grade, grade_letter = calculate_grade(percentage)
    passed = percentage >= 60
    
    # Create detailed result
    import uuid
    result = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz_id,
        "quiz_title": quiz["title"],
        "user_id": user_id,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "grade": grade,
        "grade_letter": grade_letter,
        "passed": passed,
        "status": "PASSED" if passed else "FAILED",
        "question_results": question_results,
        "submitted_at": datetime.now().isoformat(),
        "message": f"Quiz submitted successfully! You scored {percentage}% and {'PASSED' if passed else 'FAILED'} with grade {grade_letter}"
    }
    
    # Store result in database
    quiz_results_db.append(result)
    
    return {"result": result}

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 97:
        return 4.0, "A+"
    elif percentage >= 93:
        return 4.0, "A"
    elif percentage >= 90:
        return 3.7, "A-"
    elif percentage >= 87:
        return 3.3, "B+"
    elif percentage >= 83:
        return 3.0, "B"
    elif percentage >= 80:
        return 2.7, "B-"
    elif percentage >= 77:
        return 2.3, "C+"
    elif percentage >= 73:
        return 2.0, "C"
    elif percentage >= 70:
        return 1.7, "C-"
    elif percentage >= 67:
        return 1.3, "D+"
    elif percentage >= 63:
        return 1.0, "D"
    elif percentage >= 60:
        return 0.7, "D-"
    else:
        return 0.0, "F"

@app.get("/api/quiz-results")
def get_quiz_results(user_id: int = None):
    """Get quiz results for a specific user or all results"""
    if user_id:
        user_results = [r for r in quiz_results_db if r.get("user_id") == user_id]
        return {"results": user_results, "total": len(user_results)}
    return {"results": quiz_results_db, "total": len(quiz_results_db)}

@app.delete("/api/quizzes/{quiz_id}")
def delete_quiz(quiz_id: str, user_id: int, user_role: str):
    """Delete a quiz - teachers can delete their own, super admins can delete any"""
    # Find the quiz
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check permissions
    if user_role == "super_admin":
        # Super admin can delete any quiz
        pass
    elif user_role == "teacher" or user_role == "admin":
        # Teachers and admins can only delete their own quizzes
        if quiz.get("created_by") != user_id and quiz.get("user_id") != user_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only delete quizzes you created"
            )
    else:
        # Students and guests cannot delete quizzes
        raise HTTPException(
            status_code=403, 
            detail="You don't have permission to delete quizzes"
        )
    
    # Remove quiz from database
    quizzes_db[:] = [q for q in quizzes_db if q["id"] != quiz_id]
    
    # Also remove any quiz results for this quiz
    quiz_results_db[:] = [r for r in quiz_results_db if r.get("quiz_id") != quiz_id]
    
    return {
        "message": "Quiz deleted successfully",
        "deleted_quiz_id": quiz_id,
        "deleted_by": user_id,
        "deleted_by_role": user_role
    }

@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate):
    """Create a manual quiz"""
    # Allow all users including guests to create quizzes
    if quiz.user_role not in ["teacher", "admin", "super_admin", "student", "guest"]:
        raise HTTPException(status_code=403, detail="Invalid user role for quiz creation")
    
    import uuid
    from datetime import datetime
    
    quiz_id = str(uuid.uuid4())
    
    # Get creator information to determine if they're an admin
    creator = next((u for u in users_db if u["id"] == quiz.user_id), None)
    is_admin = creator and creator.get("role") in ["admin", "super_admin"]
    
    # If creator is an admin, make quiz public and visible to everyone
    is_public = quiz.is_public or is_admin
    
    new_quiz = {
        "id": quiz_id,
        "title": quiz.title,
        "description": quiz.description,
        "time_limit": quiz.time_limit,
        "is_public": is_public,
        "created_by": quiz.user_id,
        "created_at": datetime.now().isoformat(),
        "total_questions": len(quiz.questions),
        "total_points": sum(q.get("points", 1) for q in quiz.questions),
        "questions": quiz.questions,
        "creation_type": "manual",
        "created_by_admin": is_admin  # Flag to identify admin-created quizzes
    }
    quizzes_db.append(new_quiz)
    return {"message": "Quiz created successfully", "quiz": new_quiz}

@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(request: QuizGenerationRequest):
    """Generate quiz using Gemini AI"""
    # Allow all users including guests to create quizzes
    if request.user_role not in ["teacher", "admin", "super_admin", "student", "guest"]:
        raise HTTPException(status_code=403, detail="Invalid user role for quiz creation")
    
    import uuid
    from datetime import datetime
    
    try:
        # Use Gemini AI for quiz generation
        from ai_models import ai_quiz_generator
        
        print(f"🤖 Generating quiz using Gemini AI: {request.subject} - {request.difficulty}")
        
        # Generate questions using Gemini AI
        ai_questions = ai_quiz_generator.generate_quiz_questions(
            subject=request.subject,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            topic=request.title  # Use title as topic
        )
        
        if ai_questions:
            # Convert AI questions to the expected format
            questions = []
            for i, q in enumerate(ai_questions):
                # Calculate points based on difficulty
                if request.difficulty == "easy":
                    points = 1
                elif request.difficulty == "medium":
                    points = 2
                else:  # hard
                    points = 3
                
                question = {
                    "id": f"q_{i+1}",
                    "question_text": q["question_text"],
                    "question_type": "multiple_choice",
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "difficulty": request.difficulty,
                    "points": points
                }
                questions.append(question)
        else:
            # No fallback - return error if Gemini AI fails
            print("❌ Gemini AI failed to generate questions")
            raise HTTPException(
                status_code=500, 
                detail="AI quiz generation failed. Please check your Gemini API key and try again."
            )
        
        # Create quiz
        quiz_id = str(uuid.uuid4())
        
        # Get creator information to determine if they're an admin
        creator = next((u for u in users_db if u["id"] == request.user_id), None)
        is_admin = creator and creator.get("role") in ["admin", "super_admin"]
        
        # If creator is an admin, make quiz public and visible to everyone
        is_public = request.is_public or is_admin
        
        new_quiz = {
            "id": quiz_id,
            "title": request.title,
            "description": request.description,
            "questions": questions,
            "time_limit": request.time_limit,
            "is_public": is_public,
            "created_by": request.user_id,
            "created_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "total_points": sum(q.get("points", 1) for q in questions),
            "creation_type": "ai_generated",
            "topic": request.subject,
            "difficulty": request.difficulty,
            "created_by_admin": is_admin  # Flag to identify admin-created quizzes
        }
        
        quizzes_db.append(new_quiz)
        
        return {
            "message": "AI-generated quiz created successfully",
            "quiz": {
                "id": new_quiz["id"],
                "title": new_quiz["title"],
                "description": new_quiz["description"],
                "total_questions": new_quiz["total_questions"],
                "total_points": new_quiz["total_points"],
                "time_limit": new_quiz["time_limit"],
                "topic": new_quiz["topic"],
                "difficulty": new_quiz["difficulty"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

# User Registration Endpoint
@app.post("/api/register")
def register_user(user_data: dict):
    """Register a new user"""
    try:
        # Validate required fields
        required_fields = ["name", "email", "password", "role"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        # Check if email already exists
        if any(user.get('email') == user_data['email'] for user in users_db):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Prevent admin registration (only super admin can be admin)
        if user_data['role'] == "admin":
            raise HTTPException(status_code=403, detail="Admin registration is not allowed. Only super admin can access admin features.")
        
        # Hash password
        hashed_password = hash_password(user_data['password'])
        
        # Create new user
        new_user = {
            "id": len(users_db) + 1,
            "name": user_data['name'],
            "email": user_data['email'],
            "password": hashed_password,
            "role": user_data['role'],
            "created_at": datetime.now().isoformat()
        }
        
        users_db.append(new_user)
        
        # Return user without password
        user_response = {k: v for k, v in new_user.items() if k != 'password'}
        return {"message": "User registered successfully", "user": user_response}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Admin Dashboard Endpoint
@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin_id: int):
    """Get admin dashboard data"""
    try:
        # Verify admin user
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Get dashboard statistics
        total_users = len(users_db)
        total_quizzes = len(quizzes_db)
        total_results = len(quiz_results_db)
        
        # Get recent users (last 10)
        recent_users = sorted(users_db, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        # Get recent quizzes (last 10)
        recent_quizzes = sorted(quizzes_db, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        # Calculate user statistics
        teachers = [u for u in users_db if u.get('role') == 'teacher']
        students = [u for u in users_db if u.get('role') == 'student']
        admins = [u for u in users_db if u.get('role') in ['admin', 'super_admin']]
        
        # Calculate quiz statistics
        total_attempts = len(quiz_results_db)
        
        # Calculate average scores
        if quiz_results_db:
            avg_score = sum(r.get("percentage", 0) for r in quiz_results_db) / len(quiz_results_db)
            pass_rate = len([r for r in quiz_results_db if r.get("percentage", 0) >= 60]) / len(quiz_results_db) * 100
        else:
            avg_score = 0
            pass_rate = 0

        dashboard_data = {
            "overview": {
                "total_users": total_users,
                "total_teachers": len(teachers),
                "total_students": len(students),
                "total_admins": len(admins),
                "total_quizzes": total_quizzes,
                "total_attempts": total_attempts,
                "average_score": round(avg_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "users": users_db,
            "teachers": teachers,
            "students": students,
            "admins": admins,
            "recent_users": recent_users,
            "recent_quizzes": recent_quizzes,
            "admin_info": {
                "id": admin_user['id'],
                "name": admin_user['name'],
                "email": admin_user['email'],
                "role": admin_user['role']
            }
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

# Delete User Endpoint
@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, admin_id: int):
    """Delete a user (admin only)"""
    try:
        # Verify admin user
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Find user to delete
        user_to_delete = next((user for user in users_db if user['id'] == user_id), None)
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting super admin
        if user_to_delete['role'] == 'super_admin':
            raise HTTPException(status_code=403, detail="Cannot delete super admin")
        
        # Remove user
        users_db.remove(user_to_delete)
        
        return {"message": f"User {user_to_delete['name']} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# Super Admin All Credentials Endpoint
@app.get("/api/super-admin/all-credentials")
def get_all_credentials(admin_id: int):
    """Get all user credentials (super admin only)"""
    try:
        # Verify super admin user
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] != 'super_admin':
            raise HTTPException(status_code=403, detail="Access denied. Super admin privileges required.")
        
        # Return all users with their credentials (excluding super admin's own password)
        credentials = []
        for user in users_db:
            if user['id'] != admin_id:  # Don't include super admin's own credentials
                credentials.append({
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "password": user['password'],  # This will be the hashed password
                    "role": user['role'],
                    "created_at": user.get('created_at', ''),
                    "school_id": user.get('school_id', ''),
                    "created_by_teacher": user.get('created_by_teacher', '')
                })
        
        return {"users": credentials}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch credentials: {str(e)}")

# School registration endpoint
@app.post("/api/schools/register")
def register_school(school_data: SchoolRegistration, teacher_data: SchoolTeacherRegistration):
    """Register a new school with teacher"""
    try:
        # Create school
        school_id = f"school_{len(schools_db) + 1}"
        school = {
            "id": school_id,
            "name": school_data.school_name,
            "type": school_data.school_type,
            "address": school_data.address,
            "city": school_data.city,
            "state": school_data.state,
            "country": school_data.country,
            "phone": school_data.phone,
            "email": school_data.email,
            "principal_name": school_data.principal_name,
            "established_year": school_data.established_year or "",
            "max_students": school_data.max_students or "",
            "max_teachers": school_data.max_teachers or "",
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        schools_db.append(school)
        
        # Create school teacher with hashed password
        teacher_id = len(users_db) + 1
        hashed_teacher_password = hash_password(teacher_data.password)
        teacher = {
            "id": teacher_id,
            "name": teacher_data.name,
            "email": teacher_data.email,
            "password": hashed_teacher_password,  # Now securely hashed
            "phone": teacher_data.phone,
            "role": "teacher",
            "school_id": school_id,
            "created_at": datetime.now().isoformat()
        }
        
        users_db.append(teacher)
        
        # Initialize school quizzes
        school_quizzes_db[school_id] = []
        
        return {
            "message": "School registered successfully",
            "school": school,
            "teacher": {
                "id": teacher["id"],
                "name": teacher["name"],
                "email": teacher["email"],
                "role": teacher["role"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create school: {str(e)}")

# Student management endpoints
@app.post("/api/teachers/create-student")
def create_student_account(student_data: StudentCreationRequest):
    """Allow teachers to create student accounts for their school"""
    try:
        print(f"Creating student with data: {student_data}")
        print(f"Student data school_id: {student_data.school_id}")
        print(f"Student data teacher_id: {student_data.teacher_id}")
        
        # Verify the teacher exists and has the right school
        teacher = next((u for u in users_db if u["id"] == student_data.teacher_id), None)
        if not teacher:
            print(f"Teacher not found with ID: {student_data.teacher_id}")
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        print(f"Found teacher: {teacher}")
        print(f"Teacher school_id: {teacher.get('school_id')}")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can create student accounts")
        
        if teacher.get("school_id") != student_data.school_id:
            print(f"School ID mismatch: teacher has {teacher.get('school_id')}, student data has {student_data.school_id}")
            raise HTTPException(status_code=403, detail="Teacher can only create students for their own school")
        
        # Check if student email already exists
        for existing_user in users_db:
            if existing_user["email"] == student_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new student with hashed password
        student_id = len(users_db) + 1
        hashed_student_password = hash_password(student_data.password)
        student = {
            "id": student_id,
            "name": student_data.name,
            "email": student_data.email,
            "password": hashed_student_password,  # Now securely hashed
            "role": "student",
            "school_id": student_data.school_id,
            "created_by_teacher": student_data.teacher_id,
            "created_at": datetime.now().isoformat()
        }
        
        users_db.append(student)
        
        return {
            "message": "Student account created successfully",
            "student": {
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "password": student_data.password,  # Return plain password for display
                "role": student["role"],
                "school_id": student["school_id"],
                "created_at": student["created_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create student account: {str(e)}")

@app.get("/api/teachers/{teacher_id}/students")
def get_teacher_students(teacher_id: int):
    """Get all students created by a specific teacher"""
    try:
        # Verify the teacher exists
        teacher = next((u for u in users_db if u["id"] == teacher_id), None)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can view their students")
        
        # Get all students created by this teacher
        teacher_students = [
            {
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "password": student["password"],  # This will be the hashed password
                "role": student["role"],
                "school_id": student["school_id"],
                "created_at": student["created_at"]
            }
            for student in users_db
            if student.get("created_by_teacher") == teacher_id and student["role"] == "student"
        ]
        
        return {
            "students": teacher_students,
            "total": len(teacher_students)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {str(e)}")

# School management endpoints
@app.get("/api/schools")
def get_all_schools():
    """Get all schools"""
    try:
        return {
            "schools": schools_db,
            "total": len(schools_db)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schools: {str(e)}")

@app.get("/api/schools/{school_id}")
def get_school(school_id: str):
    """Get a specific school by ID"""
    try:
        school = next((s for s in schools_db if s["id"] == school_id), None)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        return {"school": school}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch school: {str(e)}")

@app.get("/api/schools/{school_id}/quizzes")
def get_school_quizzes(school_id: str):
    """Get all quizzes for a specific school"""
    try:
        # Verify school exists
        school = next((s for s in schools_db if s["id"] == school_id), None)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Get quizzes for this school
        school_quizzes = school_quizzes_db.get(school_id, [])
        
        return {
            "quizzes": school_quizzes,
            "total": len(school_quizzes),
            "school_id": school_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch school quizzes: {str(e)}")

@app.get("/api/schools/{school_id}/analytics")
def get_school_analytics(school_id: str):
    """Get analytics for a specific school"""
    try:
        # Verify school exists
        school = next((s for s in schools_db if s["id"] == school_id), None)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Get school users
        school_users = [u for u in users_db if u.get("school_id") == school_id]
        school_teachers = [u for u in school_users if u["role"] == "teacher"]
        school_students = [u for u in school_users if u["role"] == "student"]
        
        # Get school quizzes
        school_quizzes = school_quizzes_db.get(school_id, [])
        
        # Get quiz results for school students
        school_student_ids = [s["id"] for s in school_students]
        school_quiz_results = [r for r in quiz_results_db if r.get("user_id") in school_student_ids]
        
        # Calculate analytics
        total_attempts = len(school_quiz_results)
        if school_quiz_results:
            avg_score = sum(r.get("percentage", 0) for r in school_quiz_results) / len(school_quiz_results)
            pass_rate = len([r for r in school_quiz_results if r.get("percentage", 0) >= 60]) / len(school_quiz_results) * 100
        else:
            avg_score = 0
            pass_rate = 0
        
        analytics = {
            "school_info": {
                "id": school["id"],
                "name": school["name"],
                "type": school["type"]
            },
            "users": {
                "total": len(school_users),
                "teachers": len(school_teachers),
                "students": len(school_students)
            },
            "quizzes": {
                "total": len(school_quizzes),
                "attempts": total_attempts
            },
            "performance": {
                "average_score": round(avg_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "recent_activity": school_quiz_results[-10:] if school_quiz_results else []
        }
        
        return {"analytics": analytics}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch school analytics: {str(e)}")

# Analytics endpoints
@app.get("/api/analytics/overview")
def get_analytics_overview(teacher_id: int):
    """Get analytics overview for a teacher"""
    try:
        # Verify teacher exists
        teacher = next((u for u in users_db if u["id"] == teacher_id), None)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can access analytics")
        
        # Get teacher's students
        teacher_students = [u for u in users_db if u.get("created_by_teacher") == teacher_id and u["role"] == "student"]
        
        # Get teacher's quizzes (check both user_id and created_by fields)
        teacher_quizzes = [q for q in quizzes_db if q.get("user_id") == teacher_id or q.get("created_by") == teacher_id]
        
        # Get quiz results for teacher's students
        student_ids = [s["id"] for s in teacher_students]
        student_results = [r for r in quiz_results_db if r.get("user_id") in student_ids]
        
        # Calculate statistics
        total_attempts = len(student_results)
        if student_results:
            avg_score = sum(r.get("percentage", 0) for r in student_results) / len(student_results)
            pass_rate = len([r for r in student_results if r.get("percentage", 0) >= 60]) / len(student_results) * 100
            
            # Calculate grade distribution
            grade_distribution = {}
            for result in student_results:
                grade = result.get("grade_letter", "F")
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            
            # Calculate subject performance
            subject_performance = {}
            for result in student_results:
                # Get quiz to find subject
                quiz = next((q for q in teacher_quizzes if q["id"] == result.get("quiz_id")), None)
                if quiz:
                    subject = quiz.get("subject", "General")
                    if subject not in subject_performance:
                        subject_performance[subject] = {
                            "total_attempts": 0,
                            "total_score": 0,
                            "passed_attempts": 0
                        }
                    subject_performance[subject]["total_attempts"] += 1
                    subject_performance[subject]["total_score"] += result.get("percentage", 0)
                    if result.get("passed", False):
                        subject_performance[subject]["passed_attempts"] += 1
            
            # Calculate averages for subject performance
            for subject, data in subject_performance.items():
                data["average_score"] = round(data["total_score"] / data["total_attempts"], 2) if data["total_attempts"] > 0 else 0
                data["pass_rate"] = round((data["passed_attempts"] / data["total_attempts"]) * 100, 2) if data["total_attempts"] > 0 else 0
        else:
            avg_score = 0
            pass_rate = 0
            grade_distribution = {}
            subject_performance = {}
        
        overview = {
            "teacher_info": {
                "id": teacher["id"],
                "name": teacher["name"],
                "email": teacher["email"],
                "school_id": teacher.get("school_id")
            },
            "students": {
                "total": len(teacher_students),
                "active": len([s for s in teacher_students if s.get("is_active", True)])
            },
            "quizzes": {
                "total": len(teacher_quizzes),
                "published": len([q for q in teacher_quizzes if q.get("is_public", True)])
            },
            "performance": {
                "total_attempts": total_attempts,
                "average_score": round(avg_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "grade_distribution": grade_distribution,
            "subject_performance": subject_performance,
            "recent_activity": student_results[-10:] if student_results else []
        }
        
        return overview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics overview: {str(e)}")

@app.get("/api/analytics/students")
def get_student_analytics(teacher_id: int):
    """Get student analytics for a teacher"""
    try:
        # Verify teacher exists
        teacher = next((u for u in users_db if u["id"] == teacher_id), None)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can access student analytics")
        
        # Get teacher's students with their performance
        teacher_students = []
        for student in users_db:
            if student.get("created_by_teacher") == teacher_id and student["role"] == "student":
                # Get student's quiz results
                student_results = [r for r in quiz_results_db if r.get("user_id") == student["id"]]
                
                # Calculate student statistics
                total_attempts = len(student_results)
                if student_results:
                    avg_score = sum(r.get("percentage", 0) for r in student_results) / len(student_results)
                    best_score = max(r.get("percentage", 0) for r in student_results)
                    pass_rate = len([r for r in student_results if r.get("percentage", 0) >= 60]) / len(student_results) * 100
                else:
                    avg_score = 0
                    best_score = 0
                    pass_rate = 0
                
                teacher_students.append({
                    "id": student["id"],
                    "name": student["name"],
                    "email": student["email"],
                    "created_at": student["created_at"],
                    "performance": {
                        "total_attempts": total_attempts,
                        "average_score": round(avg_score, 2),
                        "best_score": round(best_score, 2),
                        "pass_rate": round(pass_rate, 2)
                    },
                    "recent_results": student_results[-5:] if student_results else []
                })
        
        return {
            "students": teacher_students,
            "total": len(teacher_students)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student analytics: {str(e)}")

@app.get("/api/analytics/quiz/{quiz_id}")
def get_quiz_analytics(quiz_id: str):
    """Get analytics for a specific quiz"""
    try:
        # Find the quiz
        quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get quiz results
        quiz_results = [r for r in quiz_results_db if r.get("quiz_id") == quiz_id]
        
        # Calculate statistics
        total_attempts = len(quiz_results)
        if quiz_results:
            avg_score = sum(r.get("percentage", 0) for r in quiz_results) / len(quiz_results)
            best_score = max(r.get("percentage", 0) for r in quiz_results)
            worst_score = min(r.get("percentage", 0) for r in quiz_results)
            pass_rate = len([r for r in quiz_results if r.get("percentage", 0) >= 60]) / len(quiz_results) * 100
            
            # Score distribution
            score_ranges = {
                "0-20": len([r for r in quiz_results if 0 <= r.get("percentage", 0) <= 20]),
                "21-40": len([r for r in quiz_results if 21 <= r.get("percentage", 0) <= 40]),
                "41-60": len([r for r in quiz_results if 41 <= r.get("percentage", 0) <= 60]),
                "61-80": len([r for r in quiz_results if 61 <= r.get("percentage", 0) <= 80]),
                "81-100": len([r for r in quiz_results if 81 <= r.get("percentage", 0) <= 100])
            }
        else:
            avg_score = 0
            best_score = 0
            worst_score = 0
            pass_rate = 0
            score_ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        
        analytics = {
            "quiz_info": {
                "id": quiz["id"],
                "title": quiz["title"],
                "description": quiz["description"],
                "subject": quiz.get("subject", ""),
                "difficulty": quiz.get("difficulty", ""),
                "created_at": quiz.get("created_at", "")
            },
            "performance": {
                "total_attempts": total_attempts,
                "average_score": round(avg_score, 2),
                "best_score": round(best_score, 2),
                "worst_score": round(worst_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "score_distribution": score_ranges,
            "recent_attempts": quiz_results[-10:] if quiz_results else []
        }
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz analytics: {str(e)}")

@app.get("/api/users/{user_id}/quiz-stats")
def get_user_quiz_stats(user_id: int):
    """Get quiz statistics for a specific user"""
    try:
        # Verify user exists
        user = next((u for u in users_db if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's quiz results
        user_results = [r for r in quiz_results_db if r.get("user_id") == user_id]
        
        # Calculate statistics
        total_attempts = len(user_results)
        if user_results:
            avg_score = sum(r.get("percentage", 0) for r in user_results) / len(user_results)
            best_score = max(r.get("percentage", 0) for r in user_results)
            pass_rate = len([r for r in user_results if r.get("percentage", 0) >= 60]) / len(user_results) * 100
            
            # Get unique quizzes attempted
            unique_quizzes = len(set(r.get("quiz_id") for r in user_results))
            
            # Recent performance (last 5 attempts)
            recent_attempts = user_results[-5:]
            recent_avg = sum(r.get("percentage", 0) for r in recent_attempts) / len(recent_attempts) if recent_attempts else 0
        else:
            avg_score = 0
            best_score = 0
            pass_rate = 0
            unique_quizzes = 0
            recent_avg = 0
            recent_attempts = []
        
        stats = {
            "user_info": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            },
            "overall_stats": {
                "total_attempts": total_attempts,
                "unique_quizzes": unique_quizzes,
                "average_score": round(avg_score, 2),
                "best_score": round(best_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "recent_performance": {
                "recent_attempts": len(recent_attempts),
                "recent_average": round(recent_avg, 2)
            },
            "recent_results": recent_attempts
        }
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user quiz stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting Complete Quiz System Backend")
    print("=" * 60)
    print("Server: http://127.0.0.1:8006")
    print("API Documentation: http://127.0.0.1:8006/docs")
    print("Frontend: http://localhost:3000")
    print("=" * 60)
    print("Backend is ready!")
    
    uvicorn.run(app, host="127.0.0.1", port=8006)
