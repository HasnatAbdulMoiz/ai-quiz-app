# Vercel-compatible complete_backend.py
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

# Add CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "https://*.vercel.app",
        "https://ai-quiz-agent.vercel.app"
    ],
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
    school_type: str
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

# In-memory storage (will be reset on each serverless invocation)
users_db = []
quizzes_db = []
quiz_results_db = []
schools_db = []
school_quizzes_db = {}

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

# Initialize data on startup
def initialize_data():
    """Initialize data for serverless environment"""
    global users_db, quizzes_db, quiz_results_db, schools_db, school_quizzes_db
    
    # Reset all data
    users_db.clear()
    quizzes_db.clear()
    quiz_results_db.clear()
    schools_db.clear()
    school_quizzes_db.clear()
    
    # Create super admin
    create_super_admin()
    
    # Add sample data
    add_sample_quiz_results()
    add_sample_quizzes()

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

def add_sample_quiz_results():
    """Add sample quiz results for testing analytics"""
    if not quiz_results_db:
        sample_results = [
            {
                "id": "sample_result_1",
                "quiz_id": "sample_quiz_1",
                "quiz_title": "Math Quiz",
                "user_id": 3,
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
            }
        ]
        
        for result in sample_results:
            quiz_results_db.append(result)

def add_sample_quizzes():
    """Add sample quizzes"""
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
        }
    ]

    for quiz in sample_quizzes:
        quizzes_db.append(quiz)

# Initialize data when module loads
initialize_data()

# Routes
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

@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate):
    """Create a manual quiz"""
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
        "created_by_admin": is_admin
    }
    quizzes_db.append(new_quiz)
    return {"message": "Quiz created successfully", "quiz": new_quiz}

@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(request: QuizGenerationRequest):
    """Generate quiz using Gemini AI"""
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
            topic=request.title
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
            "created_by_admin": is_admin
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

# Additional endpoints would go here...
# For brevity, I'm including the core functionality

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)