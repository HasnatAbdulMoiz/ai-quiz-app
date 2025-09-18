#!/usr/bin/env python3
"""
Monitoring and Logging System for AI-Powered Quiz System
Tracks performance, errors, and user analytics
"""

import os
import json
import time
import logging
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from dataclasses import dataclass, asdict
import asyncio

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@dataclass
class UserAction:
    """User action tracking"""
    user_id: int
    action: str
    timestamp: datetime
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    success: bool
    response_time: float

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    requests_per_minute: int
    error_rate: float
    ai_requests_count: int
    database_queries_count: int

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring HTTP requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Initialize Redis for metrics storage
        try:
            self.redis_client = redis.Redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis connected for monitoring")
        except:
            self.redis_client = None
            logger.warning("Redis not available for monitoring, using in-memory storage")
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request info
        user_id = getattr(request.state, 'user_id', None)
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Process request
        try:
            response = await call_next(request)
            success = response.status_code < 400
            self.request_count += 1
            
            if not success:
                self.error_count += 1
                
        except Exception as e:
            success = False
            self.error_count += 1
            logger.error("Request processing error", error=str(e), path=request.url.path)
            raise
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log request
        await self.log_request(
            user_id=user_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code if 'response' in locals() else 500,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        
        # Add monitoring headers
        if 'response' in locals():
            response.headers["X-Response-Time"] = str(response_time)
            response.headers["X-Request-ID"] = self.generate_request_id()
        
        return response
    
    async def log_request(self, **kwargs):
        """Log request details"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "http_request",
            **kwargs
        }
        
        logger.info("HTTP Request", **log_data)
        
        # Store in Redis for analytics
        if self.redis_client:
            try:
                key = f"request_log:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
                self.redis_client.lpush(key, json.dumps(log_data))
                self.redis_client.expire(key, 86400)  # Keep for 24 hours
            except Exception as e:
                logger.error("Failed to store request log in Redis", error=str(e))
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time() * 1000)}_{os.urandom(4).hex()}"

class AnalyticsTracker:
    """Analytics tracking for user behavior and system performance"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379/2'),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Analytics tracker initialized with Redis")
        except:
            self.redis_client = None
            logger.warning("Analytics tracker initialized without Redis")
    
    def track_user_action(self, user_action: UserAction):
        """Track user action"""
        try:
            # Log action
            logger.info("User Action", **asdict(user_action))
            
            # Store in Redis for analytics
            if self.redis_client:
                key = f"user_action:{user_action.user_id}:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.lpush(key, json.dumps(asdict(user_action)))
                self.redis_client.expire(key, 2592000)  # Keep for 30 days
                
                # Update daily stats
                stats_key = f"daily_stats:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.hincrby(stats_key, f"action_{user_action.action}", 1)
                self.redis_client.hincrby(stats_key, "total_actions", 1)
                self.redis_client.expire(stats_key, 2592000)  # Keep for 30 days
                
        except Exception as e:
            logger.error("Failed to track user action", error=str(e))
    
    def track_ai_usage(self, user_id: int, model: str, subject: str, num_questions: int, success: bool):
        """Track AI model usage"""
        try:
            usage_data = {
                "user_id": user_id,
                "model": model,
                "subject": subject,
                "num_questions": num_questions,
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("AI Usage", **usage_data)
            
            if self.redis_client:
                # Store usage record
                key = f"ai_usage:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.lpush(key, json.dumps(usage_data))
                self.redis_client.expire(key, 2592000)  # Keep for 30 days
                
                # Update model usage stats
                model_key = f"model_stats:{model}:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.hincrby(model_key, "requests", 1)
                self.redis_client.hincrby(model_key, "questions_generated", num_questions)
                if success:
                    self.redis_client.hincrby(model_key, "successful_requests", 1)
                else:
                    self.redis_client.hincrby(model_key, "failed_requests", 1)
                self.redis_client.expire(model_key, 2592000)  # Keep for 30 days
                
        except Exception as e:
            logger.error("Failed to track AI usage", error=str(e))
    
    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """Get daily statistics"""
        if not date:
            date = datetime.utcnow().strftime('%Y%m%d')
        
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            stats_key = f"daily_stats:{date}"
            stats = self.redis_client.hgetall(stats_key)
            
            # Convert string values to integers
            for key, value in stats.items():
                try:
                    stats[key] = int(value)
                except ValueError:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get daily stats", error=str(e))
            return {"error": str(e)}
    
    def get_model_performance(self, model: str, days: int = 7) -> Dict[str, Any]:
        """Get AI model performance over time"""
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            performance_data = {}
            
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y%m%d')
                model_key = f"model_stats:{model}:{date}"
                stats = self.redis_client.hgetall(model_key)
                
                if stats:
                    performance_data[date] = {
                        "requests": int(stats.get("requests", 0)),
                        "questions_generated": int(stats.get("questions_generated", 0)),
                        "successful_requests": int(stats.get("successful_requests", 0)),
                        "failed_requests": int(stats.get("failed_requests", 0)),
                        "success_rate": 0
                    }
                    
                    total_requests = performance_data[date]["requests"]
                    if total_requests > 0:
                        performance_data[date]["success_rate"] = (
                            performance_data[date]["successful_requests"] / total_requests
                        ) * 100
            
            return performance_data
            
        except Exception as e:
            logger.error("Failed to get model performance", error=str(e))
            return {"error": str(e)}

class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 metrics
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            import psutil
            
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Application metrics (simplified)
            active_connections = len(psutil.net_connections())
            
            # Calculate requests per minute (simplified)
            current_time = time.time()
            requests_per_minute = 0  # This would be calculated from actual request logs
            
            # Error rate (simplified)
            error_rate = 0.0  # This would be calculated from actual error logs
            
            # AI and database metrics (simplified)
            ai_requests_count = 0
            database_queries_count = 0
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                active_connections=active_connections,
                requests_per_minute=requests_per_minute,
                error_rate=error_rate,
                ai_requests_count=ai_requests_count,
                database_queries_count=database_queries_count
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
            
            return metrics
            
        except ImportError:
            logger.warning("psutil not available for system metrics")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=0.0,
                memory_usage=0.0,
                active_connections=0,
                requests_per_minute=0,
                error_rate=0.0,
                ai_requests_count=0,
                database_queries_count=0
            )
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=0.0,
                memory_usage=0.0,
                active_connections=0,
                requests_per_minute=0,
                error_rate=0.0,
                ai_requests_count=0,
                database_queries_count=0
            )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        return {
            "current": asdict(recent_metrics[-1]) if recent_metrics else {},
            "average": {
                "cpu_usage": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                "memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                "active_connections": sum(m.active_connections for m in recent_metrics) / len(recent_metrics),
            },
            "history_count": len(self.metrics_history)
        }

# Global instances
analytics_tracker = AnalyticsTracker()
performance_monitor = PerformanceMonitor()

# Background task for collecting metrics
async def collect_metrics_periodically():
    """Background task to collect metrics every minute"""
    while True:
        try:
            metrics = performance_monitor.collect_metrics()
            logger.info("System Metrics", **asdict(metrics))
            await asyncio.sleep(60)  # Collect every minute
        except Exception as e:
            logger.error("Failed to collect metrics", error=str(e))
            await asyncio.sleep(60)

if __name__ == "__main__":
    print("📊 Monitoring System")
    print("=" * 25)
    print("✅ Monitoring middleware ready")
    print("📈 Analytics tracker ready")
    print("⚡ Performance monitor ready")
    print("🔍 Structured logging configured")
