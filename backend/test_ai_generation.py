#!/usr/bin/env python3
"""
Test AI Quiz Generation
"""
from ai_quiz_generator import AIQuizGenerator
from registration_backend import EnhancedQuizGenerator

def test_ai_generation():
    """Test AI quiz generation"""
    print("🤖 Testing AI Quiz Generation")
    print("=" * 50)
    
    # Test AI Generator
    print("\n🧪 Testing AI Generator...")
    ai_generator = AIQuizGenerator()
    
    questions = ai_generator.generate_quiz_with_ai(
        "Python Programming", "medium", 2, "huggingface"
    )
    
    if questions:
        print(f"✅ AI Generator: {len(questions)} questions generated")
        for i, q in enumerate(questions):
            print(f"Q{i+1}: {q.question_text}")
            print(f"Options: {q.options}")
            print(f"Correct: {q.correct_answer}")
            print(f"Explanation: {q.explanation}")
            print("-" * 50)
    else:
        print("❌ AI Generator failed")
    
    # Test Enhanced Generator
    print("\n🧪 Testing Enhanced Generator...")
    enhanced_generator = EnhancedQuizGenerator()
    
    template_questions = enhanced_generator.generate_questions(
        "Python Programming", "medium", 2
    )
    
    if template_questions:
        print(f"✅ Enhanced Generator: {len(template_questions)} questions generated")
        for i, q in enumerate(template_questions):
            print(f"Q{i+1}: {q['question_text']}")
            print(f"Options: {q['options']}")
            print(f"Correct: {q['correct_answer']}")
            print(f"Explanation: {q['explanation']}")
            print("-" * 50)
    else:
        print("❌ Enhanced Generator failed")

if __name__ == "__main__":
    test_ai_generation()
