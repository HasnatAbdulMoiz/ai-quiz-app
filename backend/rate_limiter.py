#!/usr/bin/env python3
"""
Rate Limiting System for AI-Powered Quiz System
Prevents abuse and controls API costs
"""

from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
import os
from typing import Dict, Optional

# Initialize Redis connection (fallback to in-memory if Redis not available)
try:
    redis_client = redis.Redis.from_url(
        os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        decode_responses=True
    )
    redis_client.ping()  # Test connection
    print("✅ Redis connected for rate limiting")
except:
    redis_client = None
    print("⚠️ Redis not available, using in-memory rate limiting")

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv('REDIS_URL', 'memory://') if redis_client else 'memory://',
    default_limits=["1000/hour"]  # Default limit
)

# Rate limit configurations
RATE_LIMITS = {
    # AI Quiz Generation (expensive operations)
    "ai_quiz_generation": {
        "free_user": "5/hour",      # 5 quizzes per hour for free users
        "premium_user": "50/hour",  # 50 quizzes per hour for premium users
        "teacher": "100/hour",      # 100 quizzes per hour for teachers
        "admin": "500/hour"         # 500 quizzes per hour for admins
    },
    
    # Regular API calls
    "api_calls": {
        "free_user": "1000/hour",   # 1000 API calls per hour
        "premium_user": "5000/hour", # 5000 API calls per hour
        "teacher": "10000/hour",    # 10000 API calls per hour
        "admin": "50000/hour"       # 50000 API calls per hour
    },
    
    # Authentication
    "auth": {
        "login": "10/hour",         # 10 login attempts per hour
        "register": "5/hour",       # 5 registration attempts per hour
        "password_reset": "3/hour"  # 3 password reset attempts per hour
    }
}

def get_user_rate_limit(user_role: str, limit_type: str) -> str:
    """Get rate limit for user based on role and operation type"""
    if user_role not in ["student", "teacher", "admin"]:
        user_role = "free_user"  # Default for unknown roles
    
    # Map roles to rate limit categories
    role_mapping = {
        "student": "free_user",
        "teacher": "teacher", 
        "admin": "admin"
    }
    
    mapped_role = role_mapping.get(user_role, "free_user")
    
    return RATE_LIMITS.get(limit_type, {}).get(mapped_role, "100/hour")

def create_rate_limit_decorator(limit_type: str, user_role: str = None):
    """Create a rate limit decorator for specific operations"""
    if user_role:
        limit = get_user_rate_limit(user_role, limit_type)
    else:
        limit = RATE_LIMITS.get(limit_type, {}).get("free_user", "100/hour")
    
    return limiter.limit(limit)

# Predefined decorators for common operations
ai_quiz_generation_limit = limiter.limit("5/hour")  # Default for AI generation
api_calls_limit = limiter.limit("1000/hour")       # Default for API calls
auth_limit = limiter.limit("10/hour")              # Default for auth

def check_ai_usage_limit(user_id: int, user_role: str) -> bool:
    """Check if user has exceeded AI usage limits"""
    if not redis_client:
        return True  # Allow if Redis not available
    
    key = f"ai_usage:{user_id}:{user_role}"
    current_usage = redis_client.get(key)
    
    if current_usage is None:
        redis_client.setex(key, 3600, 1)  # 1 hour expiry
        return True
    
    current_usage = int(current_usage)
    limit = int(get_user_rate_limit(user_role, "ai_quiz_generation").split('/')[0])
    
    if current_usage >= limit:
        return False
    
    redis_client.incr(key)
    return True

def get_usage_stats(user_id: int, user_role: str) -> Dict:
    """Get current usage statistics for user"""
    if not redis_client:
        return {"ai_usage": 0, "limit": 5, "reset_in": 3600}
    
    key = f"ai_usage:{user_id}:{user_role}"
    current_usage = redis_client.get(key)
    ttl = redis_client.ttl(key)
    
    limit = int(get_user_rate_limit(user_role, "ai_quiz_generation").split('/')[0])
    
    return {
        "ai_usage": int(current_usage) if current_usage else 0,
        "limit": limit,
        "reset_in": ttl if ttl > 0 else 3600,
        "remaining": max(0, limit - (int(current_usage) if current_usage else 0))
    }

# Rate limit exception handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    response = HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Try again in {exc.retry_after} seconds.",
            "retry_after": exc.retry_after,
            "limit": exc.detail
        }
    )
    return response

# Usage tracking for analytics
def track_ai_usage(user_id: int, user_role: str, operation: str):
    """Track AI usage for analytics and billing"""
    if not redis_client:
        return
    
    # Track daily usage
    daily_key = f"daily_ai_usage:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    redis_client.incr(daily_key)
    redis_client.expire(daily_key, 86400)  # 24 hours
    
    # Track operation type
    operation_key = f"ai_operation:{user_id}:{operation}:{datetime.now().strftime('%Y-%m-%d')}"
    redis_client.incr(operation_key)
    redis_client.expire(operation_key, 86400)  # 24 hours

if __name__ == "__main__":
    print("🚦 Rate Limiting System")
    print("=" * 30)
    print("✅ Rate limiter initialized")
    print("📊 Rate limits configured:")
    for limit_type, limits in RATE_LIMITS.items():
        print(f"  {limit_type}: {limits}")
