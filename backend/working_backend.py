# working_backend.py - Working backend with quiz submission
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

app = FastAPI(title="Quiz System API", version="1.0.0")

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

# In-memory storage
users_db = []
quizzes_db = []
quiz_results_db = []

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
            "created_at": datetime.utcnow().isoformat()
        }
        users_db.insert(0, super_admin)
        print(f"✅ Super Admin created: {super_admin_email}")

# Create super admin on startup
create_super_admin()

# Add some sample quizzes
sample_quiz = {
    "id": "sample_quiz_1",
    "title": "Sample Quiz",
    "description": "A sample quiz for testing",
    "time_limit": 30,
    "is_public": True,
    "created_by": 1,
    "created_at": datetime.utcnow().isoformat(),
    "total_questions": 2,
    "total_points": 2,
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
            "question_text": "What is the capital of France?",
            "question_type": "multiple_choice",
            "options": ["London", "Berlin", "Paris", "Madrid"],
            "correct_answer": "Paris",
            "explanation": "Paris is the capital of France",
            "difficulty": "easy",
            "points": 1
        }
    ]
}
quizzes_db.append(sample_quiz)

@app.get("/")
def read_root():
    return {"message": "AI-Powered Quiz System API", "version": "1.0.0"}

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
        
        # Find question
        question = next((q for q in quiz["questions"] if q["id"] == question_id), None)
        if question:
            points = question.get("points", 1)
            max_score += points
            is_correct = user_answer == question.get("correct_answer")
            
            if is_correct:
                total_score += points
            
            question_results.append({
                "question_id": question_id,
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Working Quiz System Backend")
    print("=" * 60)
    print("📍 Server: http://127.0.0.1:8002")
    print("🔗 API Documentation: http://127.0.0.1:8002/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 60)
    print("✨ Backend is ready!")
    
    uvicorn.run(app, host="127.0.0.1", port=8002)
