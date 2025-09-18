#!/usr/bin/env python3
"""
AI Models Integration - Gemini Only
Only uses Google Gemini AI for quiz generation
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiModel:
    """Google Gemini AI model integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = "gemini-1.5-flash"
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return bool(self.api_key)
    
    def generate_quiz_questions(self, subject: str, difficulty: str, num_questions: int, topic: str = None) -> List[Dict[str, Any]]:
        """Generate quiz questions using Google Gemini AI"""
        if not self.is_available():
            print("❌ Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
            return []
        
        try:
            print(f"🤖 Using Google Gemini AI for {subject} quiz generation...")
            
            # Try to import and use Gemini
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
            except ImportError:
                print("❌ Google Generative AI library not installed. Install with: pip install google-generativeai")
                return []
            
            # Create a comprehensive prompt for quiz generation
            prompt = self._create_quiz_prompt(subject, difficulty, num_questions, topic)
            
            # Generate content using Gemini
            response = model.generate_content(prompt)
            
            if response and response.text:
                return self._parse_quiz_response(response.text, num_questions)
            else:
                print("❌ Gemini API returned empty response")
                return []
                
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            return []
    
    def _create_quiz_prompt(self, subject: str, difficulty: str, num_questions: int, topic: str = None) -> str:
        """Create a detailed prompt for quiz generation"""
        topic_text = f" on the topic: {topic}" if topic else ""
        
        prompt = f"""
Generate {num_questions} high-quality multiple-choice quiz questions for {subject} at {difficulty} level{topic_text}.

Requirements:
1. Each question should be clear, accurate, and educational
2. Provide 4 options (A, B, C, D) with only one correct answer
3. Include a detailed explanation for the correct answer
4. Ensure questions are appropriate for {difficulty} level
5. Make questions practical and relevant

Format your response as a JSON array with this structure:
[
    {{
        "question_text": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct_answer": "Paris",
        "explanation": "Paris is the capital and largest city of France."
    }}
]

Generate exactly {num_questions} questions. Make sure the JSON is valid and properly formatted.
"""
        return prompt
    
    def _parse_quiz_response(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse the quiz response from Gemini"""
        try:
            # Clean the response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            questions = json.loads(content)
            
            if not isinstance(questions, list):
                print("❌ Response is not a list of questions")
                return []
            
            # Validate and clean questions
            valid_questions = []
            for i, q in enumerate(questions):
                if self._validate_question(q):
                    valid_questions.append(q)
                else:
                    print(f"⚠️ Skipping invalid question {i+1}")
            
            print(f"✅ Generated {len(valid_questions)} valid questions using Gemini")
            return valid_questions
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {str(e)}")
            print(f"📝 Raw response: {content[:200]}...")
            return []
        except Exception as e:
            print(f"❌ Error parsing Gemini response: {str(e)}")
            return []
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate a single question"""
        required_fields = ['question_text', 'options', 'correct_answer', 'explanation']
        
        for field in required_fields:
            if field not in question:
                print(f"❌ Missing required field: {field}")
                return False
        
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            print("❌ Options must be a list of exactly 4 items")
            return False
        
        if question['correct_answer'] not in question['options']:
            print("❌ Correct answer must be one of the options")
            return False
        
        return True


class AIQuizGenerator:
    """AI Quiz Generator - Gemini Only"""
    
    def __init__(self):
        self.gemini = GeminiModel()
    
    def generate_quiz_questions(self, subject: str, difficulty: str, num_questions: int, 
                              topic: str = None, preferred_model: str = None) -> List[Dict[str, Any]]:
        """Generate quiz questions using Gemini AI"""
        
        if self.gemini.is_available():
            questions = self.gemini.generate_quiz_questions(
                subject, difficulty, num_questions, topic
            )
            if questions:
                return questions
        
        # If Gemini fails, return empty list (no fallback)
        print("❌ Gemini AI not available. No questions generated.")
        return []


# Create a global instance
ai_quiz_generator = AIQuizGenerator()

# Default AI model
DEFAULT_AI_MODEL = "gemini"

def print_ai_status():
    """Print the status of AI models"""
    print("\n🤖 AI Models Status:")
    print("=" * 30)
    
    gemini = GeminiModel()
    if gemini.is_available():
        print("✅ Gemini AI: Available")
    else:
        print("❌ Gemini AI: Not available (API key missing)")
    
    print(f"🎯 Default Model: {DEFAULT_AI_MODEL}")
    print("📝 Note: Only Gemini AI is configured for quiz generation")

if __name__ == "__main__":
    print_ai_status()
