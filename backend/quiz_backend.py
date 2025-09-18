# backend/quiz_backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime

app = FastAPI(title="Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str  # "multiple_choice", "true_false", "short_answer"
    options: List[str]  # For multiple choice
    correct_answer: str
    difficulty: str  # "easy", "medium", "hard"
    points: int

class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[QuestionCreate]
    time_limit: int  # in minutes
    is_public: bool

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[str]  # User's answers

# In-memory storage
users_db = []
quizzes_db = []
quiz_submissions_db = []

@app.get("/")
def read_root():
    return {"message": "AI-Powered Quiz System Agent API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# User endpoints
@app.post("/api/register")
def register_user(user: UserRegistration):
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": len(users_db) + 1,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "created_at": datetime.now().isoformat()
    }
    
    users_db.append(new_user)
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"]
        }
    }

@app.post("/api/login")
def login_user(user: UserLogin):
    for existing_user in users_db:
        if existing_user["email"] == user.email and existing_user["password"] == user.password:
            return {
                "message": "Login successful",
                "user": {
                    "id": existing_user["id"],
                    "name": existing_user["name"],
                    "email": existing_user["email"],
                    "role": existing_user["role"]
                }
            }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

# Quiz endpoints
@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate, user_id: int):
    quiz_id = str(uuid.uuid4())
    new_quiz = {
        "id": quiz_id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": [q.dict() for q in quiz.questions],
        "time_limit": quiz.time_limit,
        "is_public": quiz.is_public,
        "created_by": user_id,
        "created_at": datetime.now().isoformat(),
        "total_questions": len(quiz.questions),
        "total_points": sum(q.points for q in quiz.questions)
    }
    
    quizzes_db.append(new_quiz)
    
    return {
        "message": "Quiz created successfully",
        "quiz": {
            "id": new_quiz["id"],
            "title": new_quiz["title"],
            "description": new_quiz["description"],
            "total_questions": new_quiz["total_questions"],
            "total_points": new_quiz["total_points"],
            "time_limit": new_quiz["time_limit"]
        }
    }

@app.get("/api/quizzes")
def get_quizzes(user_id: Optional[int] = None):
    if user_id:
        # Return quizzes created by user or public quizzes
        user_quizzes = [q for q in quizzes_db if q["created_by"] == user_id or q["is_public"]]
        return {"quizzes": user_quizzes}
    else:
        # Return all public quizzes
        public_quizzes = [q for q in quizzes_db if q["is_public"]]
        return {"quizzes": public_quizzes}

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Sorry, the quiz you're looking for doesn't exist or has been removed")
    
    # Remove correct answers for security
    quiz_copy = quiz.copy()
    for question in quiz_copy["questions"]:
        if "correct_answer" in question:
            del question["correct_answer"]
    
    return {"quiz": quiz_copy}

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission: QuizSubmission, user_id: int):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Sorry, the quiz you're looking for doesn't exist or has been removed")
    
    # Calculate score
    score = 0
    total_points = quiz["total_points"]
    
    for i, question in enumerate(quiz["questions"]):
        if i < len(submission.answers):
            if question["correct_answer"].lower() == submission.answers[i].lower():
                score += question["points"]
    
    percentage = (score / total_points) * 100 if total_points > 0 else 0
    
    # Save submission
    submission_record = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz_id,
        "user_id": user_id,
        "answers": submission.answers,
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "submitted_at": datetime.now().isoformat()
    }
    
    quiz_submissions_db.append(submission_record)
    
    return {
        "message": "Quiz submitted successfully",
        "result": {
            "score": score,
            "total_points": total_points,
            "percentage": round(percentage, 2)
        }
    }

@app.get("/api/users/{user_id}/submissions")
def get_user_submissions(user_id: int):
    user_submissions = [s for s in quiz_submissions_db if s["user_id"] == user_id]
    return {"submissions": user_submissions}

if __name__ == "__main__":
    import uvicorn
    print("Starting quiz backend on http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)