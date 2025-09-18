"""
AI-Powered Quiz Generator - Gemini Only
Uses only Google Gemini AI for dynamic quiz generation
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ai_models import GeminiModel

@dataclass
class QuizQuestion:
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str
    points: int

class AIQuizGenerator:
    """AI Quiz Generator - Gemini Only"""
    
    def __init__(self):
        self.gemini = GeminiModel()
    
    def generate_quiz_with_ai(self, 
                            subject: str, 
                            difficulty: str, 
                            num_questions: int,
                            model: str = 'gemini') -> List[QuizQuestion]:
        """
        Generate quiz questions using Gemini AI
        """
        try:
            if self.gemini.is_available():
                questions_data = self.gemini.generate_quiz_questions(
                    subject, difficulty, num_questions
                )
                
                if questions_data:
                    # Convert to QuizQuestion objects
                    quiz_questions = []
                    for q_data in questions_data:
                        points = 1 if difficulty == 'easy' else (2 if difficulty == 'medium' else 3)
                        
                        question = QuizQuestion(
                            question_text=q_data.get('question_text', ''),
                            options=q_data.get('options', []),
                            correct_answer=q_data.get('correct_answer', ''),
                            explanation=q_data.get('explanation', ''),
                            difficulty=difficulty,
                            points=points
                        )
                        quiz_questions.append(question)
                    
                    return quiz_questions
            
            # If Gemini fails, return empty list (no fallback)
            print("❌ Gemini AI not available. No questions generated.")
            return []
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return []

# Create a global instance
ai_quiz_generator = AIQuizGenerator()

# Default AI model
DEFAULT_AI_MODEL = "gemini"

def setup_ai_quiz_generator():
    """Setup AI quiz generator with environment variables"""
    
    # Create .env file template
    env_template = """
# Google Gemini API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Default model preference
DEFAULT_AI_MODEL=gemini
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("Created .env file template. Please add your Gemini API key.")
    
    return AIQuizGenerator()

# Test function
def test_ai_generation():
    """Test AI quiz generation"""
    generator = setup_ai_quiz_generator()
    
    # Test with different subjects
    subjects = ["Python Programming", "Mathematics", "Science", "History"]
    
    for subject in subjects:
        print(f"\n=== Testing {subject} ===")
        questions = generator.generate_quiz_with_ai(subject, "medium", 2)
        
        if questions:
            print(f"Generated {len(questions)} questions")
            for i, q in enumerate(questions):
                print(f"Q{i+1}: {q.question_text}")
                print(f"Options: {q.options}")
                print(f"Correct: {q.correct_answer}")
                print(f"Explanation: {q.explanation}")
                print("-" * 50)
        else:
            print("No questions generated - Gemini AI not available")

if __name__ == "__main__":
    test_ai_generation()
