#!/usr/bin/env python3
"""
Production Backend for AI-Powered Quiz System
Optimized for Google Play Store deployment with proper security, monitoring, and scaling
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

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Quiz System API",
    description="Production-ready quiz system with AI-powered content generation",
    version="2.0.0",
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
quizzes_db = {}
sessions_db = {}

# Pydantic models
class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['is_valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v

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
    
    @validator('num_questions')
    def validate_num_questions(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Number of questions must be between 1 and 100')
        return v

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "ai_models": {
            "gemini": "available" if os.getenv("GEMINI_API_KEY") else "unavailable",
            "huggingface": "available",
            "free": "available"
        }
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
@limiter.limit("5/hour")
async def register(request: Request, user_data: UserRegistration):
    """User registration with rate limiting"""
    start_time = time.time()
    
    try:
        # Check if user already exists
        if user_data.email in users_db:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user_id = len(users_db) + 1
        hashed_password = get_password_hash(user_data.password)
        
        users_db[user_data.email] = {
            "id": user_id,
            "name": sanitize_input(user_data.name),
            "email": user_data.email,
            "hashed_password": hashed_password,
            "role": user_data.role,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user_id), "email": user_data.email, "role": user_data.role, "username": user_data.name}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user_id), "email": user_data.email}
        )
        
        # Track user action
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=user_id,
            action="register",
            timestamp=datetime.utcnow(),
            details={"role": user_data.role},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800
        )
        
    except Exception as e:
        # Track failed registration
        user_action = UserAction(
            user_id=0,
            action="register_failed",
            timestamp=datetime.utcnow(),
            details={"error": str(e)},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            response_time=time.time() - start_time
        )
        analytics_tracker.track_user_action(user_action)
        
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", response_model=TokenResponse)
@limiter.limit("10/hour")
async def login(request: Request, login_data: UserLogin):
    """User login with rate limiting"""
    start_time = time.time()
    
    try:
        # Find user
        user = users_db.get(login_data.email)
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user["is_active"]:
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user["id"]), "email": user["email"], "role": user["role"], "username": user["name"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user["id"]), "email": user["email"]}
        )
        
        # Track user action
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=user["id"],
            action="login",
            timestamp=datetime.utcnow(),
            details={"role": user["role"]},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True,
            response_time=response_time
        )
        analytics_tracker.track_user_action(user_action)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800
        )
        
    except Exception as e:
        # Track failed login
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

# Quiz endpoints
@app.get("/api/quizzes")
async def get_quizzes(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all public quizzes"""
    public_quizzes = [quiz for quiz in quizzes_db.values() if quiz.get("is_public", True)]
    
    # Track user action
    user_action = UserAction(
        user_id=current_user["user_id"],
        action="view_quizzes",
        timestamp=datetime.utcnow(),
        details={"count": len(public_quizzes)},
        ip_address="unknown",
        user_agent="unknown",
        success=True,
        response_time=0.0
    )
    analytics_tracker.track_user_action(user_action)
    
    return {"quizzes": public_quizzes, "total": len(public_quizzes)}

@app.post("/api/quizzes/auto-generate")
@limiter.limit("5/hour")  # Rate limit for AI generation
async def generate_quiz(
    request: Request,
    quiz_data: QuizGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate quiz using AI with rate limiting and usage tracking"""
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
        print(f"Generating quiz using {DEFAULT_AI_MODEL} AI model...")
        questions = ai_quiz_generator.generate_quiz_questions(
            subject=sanitized_data["subject"],
            difficulty=sanitized_data["difficulty"],
            num_questions=sanitized_data["num_questions"],
            topic=sanitized_data.get("topic")
        )
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate quiz questions")
        
        # Create quiz
        quiz_id = f"quiz_{int(time.time() * 1000)}"
        quiz = {
            "id": quiz_id,
            "title": sanitized_data["title"],
            "description": sanitized_data["description"],
            "questions": json.dumps(questions),
            "time_limit": quiz_data.time_limit,
            "is_public": quiz_data.is_public,
            "created_by": current_user["user_id"],
            "created_at": datetime.utcnow().isoformat(),
            "total_questions": len(questions),
            "total_points": len(questions) * 2,  # 2 points per question
            "creation_type": "ai_generated",
            "topic": sanitized_data["subject"],
            "difficulty": sanitized_data["difficulty"]
        }
        
        quizzes_db[quiz_id] = quiz
        
        # Track AI usage
        analytics_tracker.track_ai_usage(
            user_id=current_user["user_id"],
            model=DEFAULT_AI_MODEL,
            subject=sanitized_data["subject"],
            num_questions=len(questions),
            success=True
        )
        
        # Track user action
        response_time = time.time() - start_time
        user_action = UserAction(
            user_id=current_user["user_id"],
            action="generate_quiz",
            timestamp=datetime.utcnow(),
            details={
                "quiz_id": quiz_id,
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
            "message": "AI-generated quiz created successfully",
            "quiz": quiz
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
        
        # Track failed user action
        user_action = UserAction(
            user_id=current_user["user_id"],
            action="generate_quiz_failed",
            timestamp=datetime.utcnow(),
            details={"error": str(e)},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=False,
            response_time=time.time() - start_time
        )
        analytics_tracker.track_user_action(user_action)
        
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints (admin only)
@app.get("/api/analytics/daily-stats")
async def get_daily_stats(
    date: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "teacher"]))
):
    """Get daily statistics (admin/teacher only)"""
    stats = analytics_tracker.get_daily_stats(date)
    return {"date": date or datetime.utcnow().strftime('%Y%m%d'), "stats": stats}

@app.get("/api/analytics/model-performance")
async def get_model_performance(
    model: str,
    days: int = 7,
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "teacher"]))
):
    """Get AI model performance (admin/teacher only)"""
    performance = analytics_tracker.get_model_performance(model, days)
    return {"model": model, "days": days, "performance": performance}

@app.get("/api/analytics/system-metrics")
async def get_system_metrics(
    current_user: Dict[str, Any] = Depends(require_roles(["admin"]))
):
    """Get system performance metrics (admin only)"""
    metrics = performance_monitor.get_metrics_summary()
    return {"metrics": metrics}

# AI model status endpoint
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
        "status": "operational"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("🚀 AI-Powered Quiz System - Production Backend")
    print("=" * 50)
    print_ai_status()
    print("✅ Production backend started successfully")
    print("🔒 Security middleware enabled")
    print("📊 Monitoring system active")
    print("⚡ Rate limiting configured")
    
    # Start background tasks
    asyncio.create_task(collect_metrics_periodically())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("🛑 Production backend shutting down...")

if __name__ == "__main__":
    # Production server configuration
    uvicorn.run(
        "production_backend:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 1)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
