#!/usr/bin/env python3
"""
AI Setup Script for Quiz System
Helps users configure AI API keys and test AI models
"""

import os
import sys
from ai_models import ai_quiz_generator
from env_config import print_ai_status

def setup_environment():
    """Setup environment variables for AI models"""
    print("🤖 AI Model Setup for Quiz System")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# AI Model API Keys\n")
            f.write("# Get your API key from:\n")
            f.write("# Grok AI (xAI): https://console.x.ai/\n\n")
            f.write("GROK_API_KEY=your_grok_api_key_here\n")
            f.write("DEFAULT_AI_MODEL=grok\n")
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    print("\n📋 Current AI Model Status:")
    print_ai_status()
    
    print("\n🔧 Setup Instructions:")
    print("1. Get API key from Grok AI:")
    print("   - Grok AI: https://console.x.ai/")
    print("\n2. Edit the .env file and replace the placeholder value:")
    print("   - GROK_API_KEY=your_actual_key_here")
    print("\n3. Restart the backend server to apply changes")

def test_ai_models():
    """Test AI models if API keys are configured"""
    print("\n🧪 Testing AI Models...")
    print("=" * 30)
    
    available_models = ai_quiz_generator.get_available_models()
    
    if not available_models:
        print("❌ No AI models are configured")
        print("Please set up API keys in the .env file first")
        return
    
    for model_name in available_models:
        print(f"\n🔍 Testing {model_name.upper()}...")
        try:
            is_working = ai_quiz_generator.test_model(model_name)
            if is_working:
                print(f"✅ {model_name.upper()} is working correctly")
            else:
                print(f"❌ {model_name.upper()} is not working")
        except Exception as e:
            print(f"❌ Error testing {model_name.upper()}: {str(e)}")

def generate_sample_quiz():
    """Generate a sample quiz to test AI functionality"""
    print("\n🎯 Generating Sample Quiz...")
    print("=" * 30)
    
    try:
        questions = ai_quiz_generator.generate_quiz_questions(
            subject="python",
            difficulty="easy",
            num_questions=3,
            topic="Python Basics"
        )
        
        if questions:
            print(f"✅ Successfully generated {len(questions)} questions")
            print("\n📝 Sample Questions:")
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. {q['question_text']}")
                for j, option in enumerate(q['options'], 1):
                    marker = "✓" if option == q['correct_answer'] else " "
                    print(f"   {chr(64+j)}) {option} {marker}")
                print(f"   Explanation: {q['explanation']}")
        else:
            print("❌ Failed to generate questions")
            print("Please check your API keys and try again")
            
    except Exception as e:
        print(f"❌ Error generating sample quiz: {str(e)}")

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_environment()
        elif command == "test":
            test_ai_models()
        elif command == "sample":
            generate_sample_quiz()
        elif command == "status":
            print_ai_status()
        else:
            print("❌ Unknown command. Available commands:")
            print("  setup  - Setup environment and .env file")
            print("  test   - Test AI models")
            print("  sample - Generate sample quiz")
            print("  status - Show AI model status")
    else:
        print("🤖 AI Setup Script for Quiz System")
        print("=" * 40)
        print("Available commands:")
        print("  python setup_ai.py setup  - Setup environment")
        print("  python setup_ai.py test   - Test AI models")
        print("  python setup_ai.py sample - Generate sample quiz")
        print("  python setup_ai.py status - Show status")
        print("\nExample usage:")
        print("  python setup_ai.py setup")
        print("  python setup_ai.py test")

if __name__ == "__main__":
    main()