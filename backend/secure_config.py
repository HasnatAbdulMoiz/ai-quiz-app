# secure_config.py - Secure configuration management
import os
from dotenv import load_dotenv
import secrets
import hashlib
from typing import Optional

# Load environment variables
load_dotenv()

class SecureConfig:
    """Secure configuration management for the quiz system"""
    
    def __init__(self):
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'SUPER_ADMIN_EMAIL',
            'SUPER_ADMIN_PASSWORD',
            'SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @property
    def super_admin_email(self) -> str:
        """Get super admin email from environment"""
        return os.getenv('SUPER_ADMIN_EMAIL')
    
    @property
    def super_admin_password(self) -> str:
        """Get super admin password from environment"""
        return os.getenv('SUPER_ADMIN_PASSWORD')
    
    @property
    def secret_key(self) -> str:
        """Get secret key for JWT tokens"""
        return os.getenv('SECRET_KEY')
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return os.getenv('DATABASE_URL')
    
    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm"""
        return os.getenv('JWT_ALGORITHM', 'HS256')
    
    @property
    def jwt_expiration_hours(self) -> int:
        """Get JWT expiration time in hours"""
        return int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        except ValueError:
            return False
    
    @staticmethod
    def generate_secret_key() -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

# Global config instance
config = SecureConfig()
