"""
Test script for the AI Quiz Generator.
Run this to test the AI generation functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_quiz_backend import AIQuizGenerator

def test_ai_generator():
    """Test the AI Quiz Generator with sample data."""
    print("Testing AI Quiz Generator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your-deepseek-api-key":
        print("❌ DEEPSEEK_API_KEY not set in environment variables")
        print("Please set your API key in the .env file")
        return
    
    # Initialize the generator
    generator = AIQuizGenerator()
    
    # Test parameters
    test_cases = [
        {
            "topic": "Python Programming",
            "difficulty": "easy",
            "total_questions": 3
        },
        {
            "topic": "Machine Learning",
            "difficulty": "medium", 
            "total_questions": 2
        },
        {
            "topic": "Data Structures",
            "difficulty": "hard",
            "total_questions": 2
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['topic']} ({test_case['difficulty']})")
        print("-" * 30)
        
        try:
            result = generator.generate_quiz(
                test_case["topic"],
                test_case["difficulty"],
                test_case["total_questions"]
            )
            
            if result and 'questions' in result:
                questions = result['questions']
                print(f"✅ Generated {len(questions)} questions")
                
                for j, question in enumerate(questions, 1):
                    print(f"\n  Question {j}:")
                    print(f"    Text: {question.get('question_text', 'N/A')}")
                    print(f"    Type: {question.get('question_type', 'N/A')}")
                    print(f"    Options: {question.get('options', [])}")
                    print(f"    Correct: {question.get('correct_answer', 'N/A')}")
                    print(f"    Points: {question.get('points', 'N/A')}")
            else:
                print("❌ No questions generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_ai_generator()
