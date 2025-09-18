"""
Working AI Quiz Backend - Simple version that works immediately
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime
import random

app = FastAPI(title="AI Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
users_db = []
quizzes_db = []

# Pydantic models
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class AutoQuizCreate(BaseModel):
    title: str
    description: str
    topic: str
    difficulty: str
    total_questions: int
    time_limit: int
    is_public: bool
    user_id: int

# Simple Quiz Generator
class SimpleQuizGenerator:
    def generate_quiz(self, topic: str, difficulty: str, total_questions: int):
        questions = []
        
        # Sample question templates
        templates = [
            {
                "question_text": f"What is the primary purpose of {topic}?",
                "options": [
                    "To solve complex problems",
                    "To store data efficiently", 
                    "To improve performance",
                    "To enhance user experience"
                ],
                "correct_answer": "To solve complex problems"
            },
            {
                "question_text": f"Which of the following best describes {topic}?",
                "options": [
                    "A fundamental concept",
                    "An advanced technique",
                    "A basic principle",
                    "A complex methodology"
                ],
                "correct_answer": "A fundamental concept"
            },
            {
                "question_text": f"What are the key benefits of {topic}?",
                "options": [
                    "Improved efficiency and accuracy",
                    "Reduced complexity and cost",
                    "Enhanced security and reliability",
                    "Better performance and scalability"
                ],
                "correct_answer": "Improved efficiency and accuracy"
            }
        ]
        
        # Generate questions
        for i in range(total_questions):
            template = templates[i % len(templates)]
            question = {
                "question_text": template["question_text"],
                "question_type": "multiple_choice",
                "options": template["options"],
                "correct_answer": template["correct_answer"],
                "explanation": f"This question tests understanding of {topic}",
                "difficulty": difficulty,
                "points": 2
            }
            questions.append(question)
        
        return {"questions": questions}

# Initialize generator
quiz_generator = SimpleQuizGenerator()

# Root endpoint
@app.get("/")
def root():
    return {"message": "AI Quiz System API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# User endpoints
@app.post("/api/register")
def register_user(user: UserRegistration):
    # Check if user already exists
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = {
        "id": len(users_db) + 1,
        "email": user.email,
        "password": user.password,  # In real app, hash this
        "full_name": user.full_name,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user["id"]}

@app.post("/api/login")
def login_user(user: UserLogin):
    # Find user
    for db_user in users_db:
        if db_user["email"] == user.email and db_user["password"] == user.password:
            return {
                "message": "Login successful",
                "user": {
                    "id": db_user["id"],
                    "email": db_user["email"],
                    "full_name": db_user["full_name"]
                }
            }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

# Quiz endpoints
@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(quiz: AutoQuizCreate):
    try:
        print(f"Generating quiz for topic: {quiz.topic}, difficulty: {quiz.difficulty}, questions: {quiz.total_questions}")
        
        # Generate questions
        generated_data = quiz_generator.generate_quiz(
            quiz.topic,
            quiz.difficulty,
            quiz.total_questions
        )
        
        # Create quiz
        quiz_id = str(uuid.uuid4())
        new_quiz = {
            "id": quiz_id,
            "title": quiz.title,
            "description": quiz.description,
            "questions": generated_data["questions"],
            "time_limit": quiz.time_limit,
            "is_public": quiz.is_public,
            "created_by": quiz.user_id,
            "created_at": datetime.now().isoformat(),
            "total_questions": len(generated_data["questions"]),
            "total_points": len(generated_data["questions"]) * 2,
            "creation_type": "ai_generated",
            "topic": quiz.topic,
            "difficulty": quiz.difficulty
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
        print(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.get("/api/quizzes")
def get_quizzes(user_id: Optional[int] = None):
    if user_id:
        user_quizzes = [q for q in quizzes_db if q["created_by"] == user_id or q["is_public"]]
        return {"quizzes": user_quizzes}
    else:
        return {"quizzes": quizzes_db}

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Remove correct answers for security
    quiz_copy = quiz.copy()
    for question in quiz_copy["questions"]:
        if "correct_answer" in question:
            del question["correct_answer"]
    
    return {"quiz": quiz_copy}

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Quiz Backend on http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)
