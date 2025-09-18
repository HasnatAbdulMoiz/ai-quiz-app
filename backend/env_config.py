#!/usr/bin/env python3
"""
Environment Configuration for AI Models - Gemini Only
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Model API Keys (Only Gemini)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Default AI Model (Only Gemini is supported)
DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'gemini')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://quiz_user:quiz_password@localhost:5432/quiz_system')

# CORS Origins
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

def get_ai_model_config():
    """Get AI model configuration"""
    return {
        'gemini': {
            'api_key': GEMINI_API_KEY,
            'available': bool(GEMINI_API_KEY)
        }
    }

def print_ai_status():
    """Print the status of AI models"""
    config = get_ai_model_config()
    print("🤖 AI Model Status:")
    print("=" * 40)
    
    for model_name, model_config in config.items():
        status = "✅ Available" if model_config['available'] else "❌ Not configured"
        print(f"{model_name.upper()}: {status}")
    
    print(f"\nDefault Model: {DEFAULT_AI_MODEL}")
    print("\nTo configure Gemini AI:")
    print("1. Get API key from: https://makersuite.google.com/app/apikey")
    print("2. Set environment variable:")
    print("   - GEMINI_API_KEY=your_key_here")
    print("3. Restart the backend server")
    print("\nNote: Only Google Gemini AI is supported for quiz generation.")

if __name__ == "__main__":
    print_ai_status()
