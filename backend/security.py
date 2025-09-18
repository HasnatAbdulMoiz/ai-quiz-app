#!/usr/bin/env python3
"""
Security Module for AI-Powered Quiz System
Implements JWT authentication, input validation, and security best practices
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import re

# Security configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

class SecurityConfig:
    """Security configuration class"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Input validation
    MAX_STRING_LENGTH = 1000
    MAX_QUIZ_TITLE_LENGTH = 200
    MAX_QUIZ_DESCRIPTION_LENGTH = 1000
    MAX_QUESTIONS_PER_QUIZ = 100
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
    
    if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength": calculate_password_strength(password)
    }

def calculate_password_strength(password: str) -> str:
    """Calculate password strength"""
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character variety
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Common patterns (penalties)
    if re.search(r'(.)\1{2,}', password):  # Repeated characters
        score -= 1
    if re.search(r'(123|abc|qwe)', password.lower()):  # Common sequences
        score -= 1
    
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    else:
        return "strong"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
        "username": payload.get("username")
    }

def require_role(required_role: str):
    """Decorator to require specific user role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker

def require_roles(required_roles: list):
    """Decorator to require one of multiple user roles"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def sanitize_input(text: str, max_length: int = SecurityConfig.MAX_STRING_LENGTH) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def validate_quiz_data(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate quiz creation data"""
    errors = []
    
    # Title validation
    title = quiz_data.get("title", "")
    if not title or len(title.strip()) < 3:
        errors.append("Quiz title must be at least 3 characters long")
    elif len(title) > SecurityConfig.MAX_QUIZ_TITLE_LENGTH:
        errors.append(f"Quiz title must be less than {SecurityConfig.MAX_QUIZ_TITLE_LENGTH} characters")
    
    # Description validation
    description = quiz_data.get("description", "")
    if description and len(description) > SecurityConfig.MAX_QUIZ_DESCRIPTION_LENGTH:
        errors.append(f"Quiz description must be less than {SecurityConfig.MAX_QUIZ_DESCRIPTION_LENGTH} characters")
    
    # Number of questions validation
    num_questions = quiz_data.get("num_questions", 0)
    if not isinstance(num_questions, int) or num_questions < 1:
        errors.append("Number of questions must be a positive integer")
    elif num_questions > SecurityConfig.MAX_QUESTIONS_PER_QUIZ:
        errors.append(f"Number of questions cannot exceed {SecurityConfig.MAX_QUESTIONS_PER_QUIZ}")
    
    # Subject validation
    subject = quiz_data.get("subject", "")
    valid_subjects = ["python", "mathematics", "english", "science", "history", "geography", "physics", "chemistry", "biology"]
    if subject not in valid_subjects:
        errors.append(f"Subject must be one of: {', '.join(valid_subjects)}")
    
    # Difficulty validation
    difficulty = quiz_data.get("difficulty", "")
    valid_difficulties = ["easy", "medium", "hard"]
    if difficulty not in valid_difficulties:
        errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "sanitized_data": {
            "title": sanitize_input(title, SecurityConfig.MAX_QUIZ_TITLE_LENGTH),
            "description": sanitize_input(description, SecurityConfig.MAX_QUIZ_DESCRIPTION_LENGTH),
            "subject": subject.lower(),
            "difficulty": difficulty.lower(),
            "num_questions": min(max(num_questions, 1), SecurityConfig.MAX_QUESTIONS_PER_QUIZ)
        }
    }

def generate_secure_filename(original_filename: str) -> str:
    """Generate a secure filename"""
    # Remove path components
    filename = os.path.basename(original_filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Add timestamp and random string
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_string = secrets.token_hex(8)
    name, ext = os.path.splitext(filename)
    
    return f"{name}_{timestamp}_{random_string}{ext}"

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Security headers middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

if __name__ == "__main__":
    print("🔒 Security Module")
    print("=" * 20)
    print("✅ Security functions loaded")
    print("🔐 Password validation ready")
    print("🎫 JWT authentication ready")
    print("🛡️ Input sanitization ready")
