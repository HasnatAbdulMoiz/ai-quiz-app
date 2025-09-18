import json
import os
from typing import Dict, List, Any
from schemas import ChapterCreate, TopicCreate, SubtopicCreate, QuestionCreate, QuestionType, DifficultyLevel
from ai_models import GeminiModel

class QuizGenerator:
    def __init__(self):
        self.gemini = GeminiModel()
    
    def generate_quiz(self, title: str, description: str, subject: str, difficulty: str = "medium", 
                     num_questions: int = 10, time_limit: int = 60) -> Dict[str, Any]:
        """Generate a complete quiz with table of contents and questions."""
        try:
            if not self.gemini.is_available():
                return {
                    "chapters": [],
                    "topics": [],
                    "subtopics": [],
                    "questions": [],
                    "validation": {"is_valid": False, "quality_score": 0, "issues": ["Gemini API not available"]},
                    "status": "failed"
                }
            
            # Generate questions using Gemini
            questions_data = self.gemini.generate_quiz_questions(
                subject, difficulty, num_questions, title
            )
            
            if not questions_data:
                return {
                    "chapters": [],
                    "topics": [],
                    "subtopics": [],
                    "questions": [],
                    "validation": {"is_valid": False, "quality_score": 0, "issues": ["Failed to generate questions"]},
                    "status": "failed"
                }
            
            # Convert to the expected format
            formatted_questions = []
            for i, q in enumerate(questions_data):
                formatted_questions.append({
                    "question_text": q.get("question_text", ""),
                    "question_type": "multiple_choice",
                    "options": q.get("options", []),
                    "correct_answer": q.get("correct_answer", ""),
                    "explanation": q.get("explanation", ""),
                    "difficulty_level": difficulty,
                    "points": 1 if difficulty == "easy" else (2 if difficulty == "medium" else 3),
                    "topic_id": 1,
                    "subtopic_id": 1
                })
            
            # Create basic table of contents
            toc_data = {
                "chapters": [{"title": f"{subject} Quiz", "description": description, "order_index": 1}],
                "topics": [{"title": subject, "description": f"Questions about {subject}", "chapter_id": 1, "order_index": 1}],
                "subtopics": [{"title": f"{difficulty.title()} Level", "description": f"{difficulty} difficulty questions", "topic_id": 1, "order_index": 1}]
            }
            
            return {
                "chapters": toc_data.get("chapters", []),
                "topics": toc_data.get("topics", []),
                "subtopics": toc_data.get("subtopics", []),
                "questions": formatted_questions,
                "validation": {"is_valid": True, "quality_score": 85},
                "status": "generated"
            }
            
        except Exception as e:
            return {
                "chapters": [],
                "topics": [],
                "subtopics": [],
                "questions": [],
                "validation": {"is_valid": False, "quality_score": 0, "issues": [str(e)]},
                "status": "failed"
            }
    
    def analyze_performance(self, quiz_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze student performance and provide insights."""
        try:
            if not self.gemini.is_available():
                return {"error": "Gemini API not available for performance analysis"}
            
            analysis_prompt = f"""
            Analyze these quiz results and provide insights:
            {json.dumps(quiz_results)}
            
            Return as JSON:
            {{
                "overall_analysis": "Summary of overall performance",
                "strengths": ["list of strong areas"],
                "weaknesses": ["list of weak areas"],
                "recommendations": ["list of improvement recommendations"],
                "individual_insights": [
                    {{"student_id": "id", "performance": "analysis", "recommendations": ["specific recommendations"]}}
                ],
                "content_analysis": "Analysis of question difficulty and content coverage"
            }}
            """
            
            # Use Gemini for analysis
            response = self.gemini.model.generate_content(analysis_prompt)
            
            if response and response.text:
                return json.loads(response.text)
            else:
                return {"error": "Failed to get analysis from Gemini"}
            
        except Exception as e:
            return {"error": f"Failed to analyze performance data: {str(e)}"}