#!/usr/bin/env python3
"""
School-Enabled Production Backend for AI-Powered Quiz System
Multi-tenant system with school isolation and realistic features
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
import uvicorn

# Import our modules
from ai_models import ai_quiz_generator
from env_config import DEFAULT_AI_MODEL, print_ai_status
from security import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    verify_token, get_current_user, require_roles, validate_password_strength,
    validate_quiz_data, sanitize_input, add_security_headers
)
from rate_limiter import (
    limiter, create_rate_limit_decorator, check_ai_usage_limit, 
    get_usage_stats, track_ai_usage
)
from monitoring import (
    MonitoringMiddleware, AnalyticsTracker, PerformanceMonitor,
    UserAction, collect_metrics_periodically
)
from school_system import (
    SchoolSystem, SchoolRegistration, SchoolAdminRegistration, TeacherRegistration,
    StudentRegistration, SchoolType, UserRole, EnrollmentStatus, school_system
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Quiz System - School Edition",
    description="Multi-tenant quiz system with school isolation and management",
    version="3.0.0",
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if os.getenv("DEBUG", "False").lower() == "true" else ["yourdomain.com", "*.yourdomain.com"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(429, lambda request, exc: JSONResponse(
    status_code=429,
    content={"error": "Rate limit exceeded", "retry_after": exc.retry_after}
))

# Global instances
analytics_tracker = AnalyticsTracker()
performance_monitor = PerformanceMonitor()

# In-memory storage (replace with PostgreSQL in production)
users_db = {}
sessions_db = {}

# Enhanced Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class QuizGenerationRequest(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: str
    num_questions: int
    time_limit: int = 60
    is_public: bool = True
    topic: Optional[str] = None
    grade_level: Optional[str] = None
    class_section: Optional[str] = None
    due_date: Optional[str] = None
    max_attempts: int = 3

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user_info: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "features": {
            "multi_tenant": True,
            "school_isolation": True,
            "ai_models": {
                "gemini": "available" if os.getenv("GEMINI_API_KEY") else "unavailable",
                "huggingface": "available",
                "free": "available"
            }
        }
    }

# ==================== SCHOOL MANAGEMENT ENDPOINTS ====================

@app.post("/api/schools/register")
@limiter.limit("3/hour")  # Limit school registrations
async def register_school(request: Request, school_data: SchoolRegistration, admin_data: SchoolAdminRegistration):
    """Register a new school with admin"""
    start_time = time.time()
    
    try:
        # Hash admin password
        admin_data.password = get_password_hash(admin_data.password)
        
        # Create school
        result = school_system.create_school(school_data, admin_data)
        
        # Track school registration
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=result["admin"]["id"],
            action="school_registration",
            timestamp=datetime.utcnow(),
            details={
                "school_id": result["school"]["id"],
                "school_name": result["school"]["name"],
                "school_type": result["school"]["type"]
            },
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return {
            "message": "School registered successfully",
            "school": result["school"],
            "admin": {
                "id": result["admin"]["id"],
                "name": result["admin"]["name"],
                "email": result["admin"]["email"],
                "role": result["admin"]["role"]
            }
        }
        
    except Exception as e:
        user_action = UserAction(
            user_id=0,
            action="school_registration_failed",
            timestamp=datetime.utcnow(),
            details={"error": str(e)},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            response_time=time.time() - start_time
        )
        analytics_tracker.track_user_action(user_action)
        
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schools/search")
async def search_schools(
    q: str,
    school_type: Optional[SchoolType] = None,
    limit: int = 20
):
    """Search for schools"""
    try:
        results = school_system.search_schools(q, school_type)
        return {
            "schools": results[:limit],
            "total": len(results),
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schools/{school_id}")
async def get_school_info(school_id: str):
    """Get school information"""
    try:
        school_info = school_system.get_school_info(school_id)
        return {"school": school_info}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/schools/{school_id}/teachers/register")
@limiter.limit("10/hour")
async def register_teacher(
    request: Request,
    school_id: str,
    teacher_data: TeacherRegistration
):
    """Register a teacher for a school"""
    start_time = time.time()
    
    try:
        # Hash password
        teacher_data.password = get_password_hash(teacher_data.password)
        
        # Add teacher to school
        result = school_system.add_teacher_to_school(teacher_data, school_id)
        
        # Track teacher registration
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=result["teacher"]["id"],
            action="teacher_registration",
            timestamp=datetime.utcnow(),
            details={
                "school_id": school_id,
                "subject_specialization": teacher_data.subject_specialization
            },
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return {
            "message": "Teacher registered successfully",
            "teacher": result["teacher"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/schools/{school_id}/students/register")
@limiter.limit("20/hour")
async def register_student(
    request: Request,
    school_id: str,
    student_data: StudentRegistration
):
    """Register a student for a school"""
    start_time = time.time()
    
    try:
        # Hash password
        student_data.password = get_password_hash(student_data.password)
        
        # Enroll student
        result = school_system.enroll_student(student_data, school_id)
        
        # Track student registration
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=result["student"]["id"],
            action="student_registration",
            timestamp=datetime.utcnow(),
            details={
                "school_id": school_id,
                "grade_level": student_data.grade_level
            },
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return {
            "message": "Student enrolled successfully",
            "student": result["student"],
            "enrollment": result["enrollment"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/login", response_model=TokenResponse)
@limiter.limit("10/hour")
async def login(request: Request, login_data: UserLogin):
    """User login with school context"""
    start_time = time.time()
    
    try:
        # Find user in school system
        user = None
        for u in school_system.users.values():
            if u["email"] == login_data.email:
                user = u
                break
        
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create tokens
        access_token = create_access_token(
            data={
                "sub": str(user["id"]), 
                "email": user["email"], 
                "role": user["role"], 
                "username": user["name"],
                "school_id": user.get("school_id")
            }
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user["id"]), "email": user["email"]}
        )
        
        # Track login
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=user["id"],
            action="login",
            timestamp=datetime.utcnow(),
            details={
                "role": user["role"],
                "school_id": user.get("school_id")
            },
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,
            user_info={
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "school_id": user.get("school_id"),
                "school_name": school_system.schools.get(user.get("school_id", ""), {}).get("name", "N/A")
            }
        )
        
    except Exception as e:
        user_action = UserAction(
            user_id=0,
            action="login_failed",
            timestamp=datetime.utcnow(),
            details={"error": str(e)},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            response_time=time.time() - start_time
        )
        analytics_tracker.track_user_action(user_action)
        
        raise HTTPException(status_code=401, detail=str(e))

# ==================== QUIZ ENDPOINTS ====================

@app.get("/api/schools/{school_id}/quizzes")
async def get_school_quizzes(
    school_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get quizzes for a specific school"""
    try:
        quizzes = school_system.get_school_quizzes(
            school_id, 
            current_user["role"], 
            current_user["user_id"]
        )
        
        # Track quiz viewing
        user_action = UserAction(
            user_id=current_user["user_id"],
            action="view_school_quizzes",
            timestamp=datetime.utcnow(),
            details={
                "school_id": school_id,
                "quiz_count": len(quizzes)
            },
            ip_address="unknown",
            user_agent="unknown",
            success=True,
            response_time=0.0
        )
        analytics_tracker.track_user_action(user_action)
        
        return {
            "quizzes": quizzes,
            "total": len(quizzes),
            "school_id": school_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/schools/{school_id}/quizzes/auto-generate")
@limiter.limit("5/hour")  # Rate limit for AI generation
async def generate_school_quiz(
    request: Request,
    school_id: str,
    quiz_data: QuizGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate quiz for specific school using AI"""
    start_time = time.time()
    
    try:
        # Check AI usage limits
        if not check_ai_usage_limit(current_user["user_id"], current_user["role"]):
            usage_stats = get_usage_stats(current_user["user_id"], current_user["role"])
            raise HTTPException(
                status_code=429,
                detail=f"AI usage limit exceeded. You have used {usage_stats['ai_usage']}/{usage_stats['limit']} requests. Reset in {usage_stats['reset_in']} seconds."
            )
        
        # Validate quiz data
        validation = validate_quiz_data(quiz_data.dict())
        if not validation["is_valid"]:
            raise HTTPException(status_code=400, detail=f"Validation failed: {', '.join(validation['errors'])}")
        
        sanitized_data = validation["sanitized_data"]
        
        # Generate quiz using AI
        print(f"Generating school quiz using {DEFAULT_AI_MODEL} AI model...")
        questions = ai_quiz_generator.generate_quiz_questions(
            subject=sanitized_data["subject"],
            difficulty=sanitized_data["difficulty"],
            num_questions=sanitized_data["num_questions"],
            topic=sanitized_data.get("topic")
        )
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate quiz questions")
        
        # Create school quiz
        quiz_dict = {
            "title": sanitized_data["title"],
            "description": sanitized_data["description"],
            "subject": sanitized_data["subject"],
            "difficulty": sanitized_data["difficulty"],
            "questions": questions,
            "time_limit": quiz_data.time_limit,
            "is_public": quiz_data.is_public,
            "num_questions": len(questions),
            "grade_level": quiz_data.grade_level,
            "class_section": quiz_data.class_section,
            "due_date": quiz_data.due_date,
            "max_attempts": quiz_data.max_attempts
        }
        
        result = school_system.create_school_quiz(quiz_dict, school_id, current_user["user_id"])
        
        # Track AI usage
        analytics_tracker.track_ai_usage(
            user_id=current_user["user_id"],
            model=DEFAULT_AI_MODEL,
            subject=sanitized_data["subject"],
            num_questions=len(questions),
            success=True
        )
        
        # Track quiz creation
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=current_user["user_id"],
            action="create_school_quiz",
            timestamp=datetime.utcnow(),
            details={
                "school_id": school_id,
                "quiz_id": result["quiz"]["id"],
                "subject": sanitized_data["subject"],
                "difficulty": sanitized_data["difficulty"],
                "num_questions": len(questions),
                "model": DEFAULT_AI_MODEL
            },
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return {
            "message": "School quiz created successfully",
            "quiz": result["quiz"]
        }
        
    except Exception as e:
        # Track failed AI usage
        analytics_tracker.track_ai_usage(
            user_id=current_user["user_id"],
            model=DEFAULT_AI_MODEL,
            subject=quiz_data.subject,
            num_questions=quiz_data.num_questions,
            success=False
        )
        
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/schools/{school_id}/analytics")
async def get_school_analytics(
    school_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get analytics for a specific school"""
    try:
        analytics = school_system.get_school_analytics(school_id, current_user["user_id"])
        return {"analytics": analytics, "school_id": school_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/api/public/schools")
async def get_public_schools(limit: int = 50):
    """Get public school information for discovery"""
    try:
        public_schools = []
        for school in school_system.schools.values():
            if school.get("is_active", True):
                public_schools.append({
                    "id": school["id"],
                    "name": school["name"],
                    "type": school["type"],
                    "city": school["city"],
                    "state": school["state"],
                    "country": school["country"],
                    "established_year": school["established_year"]
                })
        
        return {
            "schools": public_schools[:limit],
            "total": len(public_schools)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== AI MODEL ENDPOINTS ====================

@app.get("/api/ai/status")
async def get_ai_status():
    """Get AI model status"""
    return {
        "models": {
            "gemini": "available" if os.getenv("GEMINI_API_KEY") else "unavailable",
            "huggingface": "available",
            "free": "available",
            "grok": "available" if os.getenv("GROK_API_KEY") else "unavailable"
        },
        "default_model": DEFAULT_AI_MODEL,
        "status": "operational",
        "features": {
            "multi_tenant": True,
            "school_isolation": True,
            "grade_level_support": True
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("🏫 AI-Powered Quiz System - School Edition")
    print("=" * 50)
    print_ai_status()
    print("✅ Multi-tenant school system started")
    print("🔒 School isolation enabled")
    print("📊 School analytics ready")
    print("👨‍🏫 Teacher management ready")
    print("🎓 Student enrollment ready")
    print("📚 School-specific quizzes ready")
    
    # Start background tasks
    asyncio.create_task(collect_metrics_periodically())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("🛑 School backend shutting down...")

if __name__ == "__main__":
    # Production server configuration
    uvicorn.run(
        "school_backend:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 1)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
