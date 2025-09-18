# security_setup.py - Security setup and key generation
import secrets
import os
from pathlib import Path

def generate_secure_credentials():
    """Generate secure credentials for the application"""
    
    print("🔐 Generating Secure Credentials...")
    print("=" * 50)
    
    # Generate secure secret key
    secret_key = secrets.token_urlsafe(32)
    print(f"🔑 Secret Key: {secret_key}")
    
    # Generate secure password
    secure_password = secrets.token_urlsafe(16)
    print(f"🔒 Secure Password: {secure_password}")
    
    # Generate API key
    api_key = secrets.token_urlsafe(32)
    print(f"🔑 API Key: {api_key}")
    
    print("\n" + "=" * 50)
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("=" * 50)
    print("1. NEVER commit these credentials to version control")
    print("2. Store them securely in environment variables")
    print("3. Use different credentials for production")
    print("4. Rotate credentials regularly")
    print("5. Use strong, unique passwords")
    
    return {
        'secret_key': secret_key,
        'secure_password': secure_password,
        'api_key': api_key
    }

def create_secure_env_file():
    """Create a secure .env file with generated credentials"""
    
    credentials = generate_secure_credentials()
    
    env_content = f"""# Secure Environment Variables
# Generated on {os.popen('date').read().strip()}

# ===========================================
# SECURITY CONFIGURATION
# ===========================================

# Super Admin Credentials
SUPER_ADMIN_EMAIL=admin@yourdomain.com
SUPER_ADMIN_PASSWORD={credentials['secure_password']}

# Secret Key for JWT Tokens
SECRET_KEY={credentials['secret_key']}

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/quiz_system

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ===========================================
# AI MODEL API KEYS
# ===========================================

# Grok AI (Optional)
GROK_API_KEY=your_grok_api_key_here

# Hugging Face (Optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Google Gemini (Optional)
GEMINI_API_KEY=your_gemini_api_key_here

# Default AI Model
DEFAULT_AI_MODEL=free

# ===========================================
# PRODUCTION SETTINGS
# ===========================================

# Environment
ENVIRONMENT=development

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# ===========================================
# MONITORING & LOGGING
# ===========================================

# Log Level
LOG_LEVEL=INFO

# Enable Debug Mode (set to false in production)
DEBUG=true
"""
    
    # Write to .env file
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Secure .env file created: {env_file.absolute()}")
    print("🔐 Your credentials are now secure!")
    
    return credentials

def check_security_status():
    """Check the current security status of the application"""
    
    print("🔍 Security Status Check")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if .env is in .gitignore
        gitignore_file = Path('.gitignore')
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                content = f.read()
                if '.env' in content:
                    print("✅ .env is in .gitignore")
                else:
                    print("⚠️  .env is NOT in .gitignore - ADD IT NOW!")
        else:
            print("⚠️  .gitignore file not found - CREATE IT!")
    else:
        print("❌ .env file not found - CREATE IT!")
    
    # Check for hardcoded credentials in code
    print("\n🔍 Checking for hardcoded credentials...")
    
    # Check registration_backend.py
    backend_file = Path('registration_backend.py')
    if backend_file.exists():
        with open(backend_file, 'r') as f:
            content = f.read()
            if 'SUPER_ADMIN_EMAIL' in content and '=' in content:
                print("⚠️  Hardcoded credentials found in registration_backend.py")
            else:
                print("✅ No hardcoded credentials found in registration_backend.py")
    
    print("\n" + "=" * 50)
    print("🔐 Security Recommendations:")
    print("=" * 50)
    print("1. Use environment variables for all sensitive data")
    print("2. Never commit .env files to version control")
    print("3. Use strong, unique passwords")
    print("4. Enable HTTPS in production")
    print("5. Implement rate limiting")
    print("6. Use JWT tokens for authentication")
    print("7. Hash all passwords")
    print("8. Implement input validation")
    print("9. Use CORS properly")
    print("10. Monitor and log security events")

if __name__ == "__main__":
    print("🔐 Security Setup for AI-Powered Quiz System")
    print("=" * 60)
    
    choice = input("\nChoose an option:\n1. Generate secure credentials\n2. Create secure .env file\n3. Check security status\n4. All of the above\n\nEnter choice (1-4): ")
    
    if choice == "1":
        generate_secure_credentials()
    elif choice == "2":
        create_secure_env_file()
    elif choice == "3":
        check_security_status()
    elif choice == "4":
        create_secure_env_file()
        check_security_status()
    else:
        print("Invalid choice. Please run the script again.")
