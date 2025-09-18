#!/usr/bin/env python3
"""
Quick test script for Gemini quiz generation
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_quiz():
    """Test Gemini quiz generation"""
    print("🧪 Testing Gemini Quiz Generation...")
    print("=" * 40)
    
    try:
        # Import the AI generator
        from ai_models import AIQuizGenerator
        
        # Create generator
        generator = AIQuizGenerator()
        
        # Test with different subjects and difficulties
        test_cases = [
            {"subject": "Mathematics", "difficulty": "easy", "topic": "Addition", "questions": 2},
            {"subject": "Science", "difficulty": "medium", "topic": "Physics", "questions": 1},
            {"subject": "History", "difficulty": "hard", "topic": "World War II", "questions": 1}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['subject']} - {test_case['difficulty']}")
            print("-" * 30)
            
            questions = generator.generate_quiz_questions(
                subject=test_case["subject"],
                difficulty=test_case["difficulty"],
                num_questions=test_case["questions"],
                topic=test_case["topic"],
                preferred_model="gemini"
            )
            
            if questions:
                print(f"✅ Generated {len(questions)} questions successfully!")
                for j, q in enumerate(questions, 1):
                    print(f"   Q{j}: {q.get('question_text', 'N/A')[:60]}...")
                    print(f"   Answer: {q.get('correct_answer', 'N/A')}")
            else:
                print("❌ Failed to generate questions")
        
        print(f"\n🎉 Gemini quiz generation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_quiz()
