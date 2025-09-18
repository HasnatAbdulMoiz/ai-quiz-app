#!/usr/bin/env python3
"""
Google Gemini AI Setup and Test Script
This script helps you set up and test Google Gemini AI for quiz generation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_gemini_api_key():
    """Setup Gemini API key"""
    print("🔧 Setting up Google Gemini AI...")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('GEMINI_API_KEY')
    if current_key and current_key != 'your_gemini_api_key_here':
        print(f"✅ Gemini API key is already configured: {current_key[:10]}...")
        return True
    
    print("📝 To use Google Gemini AI, you need to:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Copy the API key")
    print()
    
    api_key = input("🔑 Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⏭️  Skipping Gemini setup. You can set it up later.")
        return False
    
    # Update .env file
    env_file = '.env'
    if os.path.exists(env_file):
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update or add GEMINI_API_KEY
        if 'GEMINI_API_KEY=' in content:
            content = content.replace('GEMINI_API_KEY=your_gemini_api_key_here', f'GEMINI_API_KEY={api_key}')
            content = content.replace('GEMINI_API_KEY=', f'GEMINI_API_KEY={api_key}')
        else:
            content += f'\nGEMINI_API_KEY={api_key}\n'
        
        # Write back
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Gemini API key saved to {env_file}")
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print(f"✅ Created {env_file} with Gemini API key")
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = api_key
    return True

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n🧪 Testing Gemini API connection...")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ No Gemini API key found. Please set it up first.")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        test_prompt = "Generate 1 simple math question with 4 multiple choice options."
        print(f"📤 Sending test prompt: {test_prompt}")
        
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("✅ Gemini API connection successful!")
            print(f"📥 Response: {response.text[:200]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except ImportError:
        print("❌ Google Generative AI library not installed.")
        print("💡 Install it with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        return False

def test_quiz_generation():
    """Test quiz generation using Gemini"""
    print("\n🎯 Testing quiz generation with Gemini...")
    print("=" * 50)
    
    try:
        # Import the AI models
        from ai_models import AIQuizGenerator
        
        # Create generator
        generator = AIQuizGenerator()
        
        # Test quiz generation
        print("📝 Generating a test quiz...")
        questions = generator.generate_quiz_questions(
            subject="Mathematics",
            difficulty="easy",
            num_questions=2,
            topic="Basic Arithmetic",
            preferred_model="gemini"
        )
        
        if questions:
            print(f"✅ Successfully generated {len(questions)} questions using Gemini!")
            for i, q in enumerate(questions, 1):
                print(f"\n📋 Question {i}:")
                print(f"   Q: {q.get('question_text', 'N/A')}")
                print(f"   A: {q.get('correct_answer', 'N/A')}")
                print(f"   Options: {q.get('options', [])}")
            return True
        else:
            print("❌ Failed to generate quiz questions")
            return False
            
    except Exception as e:
        print(f"❌ Quiz generation test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Gemini AI Setup for Quiz Generation")
    print("=" * 60)
    
    # Step 1: Setup API key
    if not setup_gemini_api_key():
        print("\n⚠️  Gemini setup incomplete. You can run this script again later.")
        return
    
    # Step 2: Test connection
    if not test_gemini_connection():
        print("\n❌ Gemini connection test failed. Please check your API key.")
        return
    
    # Step 3: Test quiz generation
    if test_quiz_generation():
        print("\n🎉 Gemini AI setup completed successfully!")
        print("✅ You can now use Gemini for AI quiz generation in your application.")
    else:
        print("\n⚠️  Gemini setup completed but quiz generation test failed.")
        print("💡 Check the error messages above for troubleshooting.")

if __name__ == "__main__":
    main()
