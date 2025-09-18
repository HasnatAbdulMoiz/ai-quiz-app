# simple_backend.py - Simple working backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import hashlib
import secrets
from datetime import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory databases
users_db = []
quizzes_db = []
quiz_results_db = []

# Password hashing functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

# Create super admin
def create_super_admin():
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
        users_db.append(super_admin)
        print(f"Super Admin created: {super_admin_email}")

# Create super admin on startup
create_super_admin()

@app.get("/")
def root():
    return {"message": "Simple Quiz System Backend"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/api/login")
def login_user(credentials: dict):
    """Login user"""
    email = credentials.get('email')
    password = credentials.get('password')
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Find user
    user = next((u for u in users_db if u['email'] == email), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Return user without password
    user_response = {k: v for k, v in user.items() if k != 'password'}
    return {"message": "Login successful", "user": user_response}

@app.post("/api/register")
def register_user(user_data: dict):
    """Register a new user"""
    try:
        required_fields = ["name", "email", "password", "role"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        if any(user.get('email') == user_data['email'] for user in users_db):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if user_data['role'] == "admin":
            raise HTTPException(status_code=403, detail="Admin registration is not allowed")
        
        hashed_password = hash_password(user_data['password'])
        new_user = {
            "id": len(users_db) + 1,
            "name": user_data['name'],
            "email": user_data['email'],
            "password": hashed_password,
            "role": user_data['role'],
            "created_at": datetime.now().isoformat()
        }
        users_db.append(new_user)
        
        user_response = {k: v for k, v in new_user.items() if k != 'password'}
        return {"message": "User registered successfully", "user": user_response}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin_id: int):
    """Get admin dashboard data"""
    try:
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        dashboard_data = {
            "total_users": len(users_db),
            "total_quizzes": len(quizzes_db),
            "total_results": len(quiz_results_db),
            "recent_users": users_db[-10:] if len(users_db) > 10 else users_db,
            "recent_quizzes": quizzes_db[-10:] if len(quizzes_db) > 10 else quizzes_db,
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

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, admin_id: int):
    """Delete a user (admin only)"""
    try:
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        user_to_delete = next((user for user in users_db if user['id'] == user_id), None)
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_to_delete['role'] == 'super_admin':
            raise HTTPException(status_code=403, detail="Cannot delete super admin")
        
        users_db.remove(user_to_delete)
        return {"message": f"User {user_to_delete['name']} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@app.get("/api/super-admin/all-credentials")
def get_all_credentials(admin_id: int):
    """Get all user credentials (super admin only)"""
    try:
        admin_user = next((user for user in users_db if user['id'] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user['role'] != 'super_admin':
            raise HTTPException(status_code=403, detail="Access denied")
        
        credentials = []
        for user in users_db:
            if user['id'] != admin_id:
                credentials.append({
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "password": user['password'],
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

@app.get("/api/quizzes")
def get_quizzes():
    """Get all quizzes"""
    return {"quizzes": quizzes_db, "total": len(quizzes_db)}

@app.post("/api/quizzes")
def create_quiz(quiz_data: dict):
    """Create a new quiz"""
    import uuid
    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": quiz_data.get("title", "Untitled Quiz"),
        "description": quiz_data.get("description", ""),
        "time_limit": quiz_data.get("time_limit", 30),
        "is_public": quiz_data.get("is_public", True),
        "created_by": quiz_data.get("user_id", 1),
        "created_at": datetime.now().isoformat(),
        "questions": quiz_data.get("questions", [])
    }
    quizzes_db.append(new_quiz)
    return {"message": "Quiz created successfully", "quiz": new_quiz}

@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(request: dict):
    """Generate quiz using AI (simulated)"""
    import uuid
    questions = [
        {
            "id": "q_1",
            "question_text": f"What is 5 + 3?",
            "question_type": "multiple_choice",
            "options": ["6", "7", "8", "9"],
            "correct_answer": "8",
            "explanation": "5 + 3 = 8",
            "difficulty": request.get("difficulty", "easy"),
            "points": 1
        }
    ]
    
    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": request.get("title", "AI Generated Quiz"),
        "description": request.get("description", "AI Generated Quiz"),
        "time_limit": request.get("time_limit", 30),
        "is_public": True,
        "created_by": request.get("user_id", 1),
        "created_at": datetime.now().isoformat(),
        "total_questions": len(questions),
        "total_points": sum(q.get("points", 1) for q in questions),
        "questions": questions
    }
    quizzes_db.append(new_quiz)
    return {"message": "AI-generated quiz created successfully", "quiz": new_quiz}

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    """Get a specific quiz by ID"""
    quiz = next((q for q in quizzes_db if q['id'] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission_data: dict):
    """Submit quiz answers"""
    import uuid
    
    # Find the quiz
    quiz = next((q for q in quizzes_db if q['id'] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    answers = submission_data.get('answers', [])
    questions = quiz.get('questions', [])
    
    correct_answers = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        if i < len(answers) and answers[i] == question.get('correct_answer'):
            correct_answers += 1
    
    score = correct_answers
    max_score = total_questions
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    # Create result
    result = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz_id,
        "quiz_title": quiz['title'],
        "user_id": submission_data.get('user_id', 1),
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "grade": percentage / 25,  # Simple grading: 100% = 4.0
        "grade_letter": "A+" if percentage >= 97 else "A" if percentage >= 90 else "B" if percentage >= 80 else "C" if percentage >= 70 else "D" if percentage >= 60 else "F",
        "passed": percentage >= 60,
        "status": "PASSED" if percentage >= 60 else "FAILED",
        "submitted_at": datetime.now().isoformat()
    }
    
    quiz_results_db.append(result)
    return {"result": result}

@app.get("/api/quiz-results")
def get_quiz_results(user_id: int = None):
    """Get quiz results"""
    if user_id:
        user_results = [r for r in quiz_results_db if r.get('user_id') == user_id]
        return {"results": user_results}
    return {"results": quiz_results_db}

if __name__ == "__main__":
    print("Starting Simple Quiz System Backend")
    print("Server: http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)