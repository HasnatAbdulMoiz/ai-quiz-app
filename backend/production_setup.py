#!/usr/bin/env python3
"""
Production Setup Script for AI-Powered Quiz System
This script helps migrate from in-memory to PostgreSQL database
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_production_database():
    """Setup PostgreSQL database for production"""
    print("🚀 Setting up Production Database...")
    
    # Check if PostgreSQL is installed
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is installed")
        else:
            print("❌ PostgreSQL not found. Please install PostgreSQL first.")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not found. Please install PostgreSQL first.")
        return False
    
    # Create database
    print("📊 Creating database...")
    try:
        # Create database
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            'CREATE DATABASE quiz_system_production;'
        ], check=True)
        print("✅ Database created successfully")
        
        # Create user
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            "CREATE USER quiz_user WITH PASSWORD 'secure_quiz_password_2024';"
        ], check=True)
        print("✅ User created successfully")
        
        # Grant permissions
        subprocess.run([
            'psql', '-U', 'postgres', '-c', 
            'GRANT ALL PRIVILEGES ON DATABASE quiz_system_production TO quiz_user;'
        ], check=True)
        print("✅ Permissions granted")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_production_env():
    """Create production environment file"""
    print("🔧 Creating production environment...")
    
    env_content = """# Production Environment Variables
# Database Configuration
DATABASE_URL=postgresql://quiz_user:secure_quiz_password_2024@localhost:5432/quiz_system_production

# AI Model API Keys
GEMINI_API_KEY=AIzaSyDS4nFa0lVKGYTytGP3N76aYyBkCC2RykA
HUGGINGFACE_API_KEY=your_huggingface_key_here
GROK_API_KEY=your_grok_key_here

# Default AI Model (Gemini is best for production)
DEFAULT_AI_MODEL=gemini

# Security
JWT_SECRET_KEY=your_super_secure_jwt_secret_key_here_2024
SECRET_KEY=your_super_secure_secret_key_here_2024

# CORS Origins (Update with your production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production Settings
DEBUG=False
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Redis Cache (Optional but recommended)
REDIS_URL=redis://localhost:6379/0

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("✅ Production environment file created: .env.production")

def install_production_dependencies():
    """Install production dependencies"""
    print("📦 Installing production dependencies...")
    
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
google-generativeai==0.8.5
requests==2.31.0
slowapi==0.1.9
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0
"""
    
    with open('requirements.production.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Production requirements file created: requirements.production.txt")

if __name__ == "__main__":
    print("🏭 AI-Powered Quiz System - Production Setup")
    print("=" * 50)
    
    # Setup database
    if setup_production_database():
        print("✅ Database setup completed")
    else:
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Create production environment
    create_production_env()
    
    # Install dependencies
    install_production_dependencies()
    
    print("\n🎉 Production setup completed!")
    print("\n📋 Next steps:")
    print("1. Update .env.production with your actual values")
    print("2. Run: pip install -r requirements.production.txt")
    print("3. Run: python production_migrate.py")
    print("4. Test with: python production_backend.py")
