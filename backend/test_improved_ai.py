#!/usr/bin/env python3
"""
Test Improved AI Question Generation
"""
from ai_quiz_generator import AIQuizGenerator

def test_improved_ai():
    """Test the improved AI question generation"""
    print("🚀 TESTING IMPROVED AI QUESTION GENERATION")
    print("=" * 60)
    
    generator = AIQuizGenerator()
    
    # Test different subjects and difficulties
    test_cases = [
        ("Python Programming", "easy", 2),
        ("Python Programming", "medium", 2),
        ("Python Programming", "hard", 2),
        ("JavaScript", "medium", 2),
        ("Mathematics", "hard", 2)
    ]
    
    for subject, difficulty, num_questions in test_cases:
        print(f"\n📚 {subject} - {difficulty.upper()} DIFFICULTY")
        print("-" * 50)
        
        questions = generator.generate_quiz_with_ai(
            subject, difficulty, num_questions, "huggingface"
        )
        
        if questions:
            for i, q in enumerate(questions, 1):
                print(f"\nQ{i}: {q.question_text}")
                print(f"Options: {q.options}")
                print(f"Correct: {q.correct_answer}")
                print(f"Explanation: {q.explanation}")
                print(f"Points: {q.points}")
        else:
            print("❌ No questions generated")

if __name__ == "__main__":
    test_improved_ai()
