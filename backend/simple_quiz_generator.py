"""
Simple Quiz Generator that creates sample questions without requiring AI API.
Useful for testing when API key is not available.
"""

import random
from typing import Dict, List, Any

class SimpleQuizGenerator:
    """Simple quiz generator that creates sample questions based on topic."""
    
    def __init__(self):
        self.question_templates = {
            "python": [
                {
                    "template": "What is the primary purpose of {concept} in Python?",
                    "concepts": ["variables", "functions", "classes", "modules", "loops", "conditionals"],
                    "options": [
                        "To store data",
                        "To perform calculations", 
                        "To organize code",
                        "To handle errors"
                    ],
                    "correct": 0
                },
                {
                    "template": "Which Python data type is used for {purpose}?",
                    "concepts": ["storing text", "storing numbers", "storing multiple items", "storing key-value pairs"],
                    "options": [
                        "string",
                        "integer", 
                        "list",
                        "dictionary"
                    ],
                    "correct": 0
                }
            ],
            "programming": [
                {
                    "template": "What is the time complexity of {algorithm}?",
                    "concepts": ["bubble sort", "binary search", "linear search", "quick sort"],
                    "options": [
                        "O(n)",
                        "O(log n)",
                        "O(n²)",
                        "O(1)"
                    ],
                    "correct": 1
                }
            ],
            "general": [
                {
                    "template": "What is the main characteristic of {concept}?",
                    "concepts": ["object-oriented programming", "functional programming", "procedural programming"],
                    "options": [
                        "Uses objects and classes",
                        "Focuses on functions",
                        "Uses step-by-step procedures",
                        "All of the above"
                    ],
                    "correct": 0
                }
            ]
        }
    
    def generate_quiz(self, topic: str, difficulty: str, total_questions: int) -> Dict[str, Any]:
        """Generate a quiz with sample questions."""
        try:
            questions = []
            
            # Determine question templates based on topic
            topic_lower = topic.lower()
            if "python" in topic_lower:
                templates = self.question_templates["python"]
            elif "programming" in topic_lower or "code" in topic_lower:
                templates = self.question_templates["programming"]
            else:
                templates = self.question_templates["general"]
            
            # Generate questions
            for i in range(total_questions):
                template = random.choice(templates)
                concept = random.choice(template["concepts"])
                
                question_text = template["template"].format(
                    concept=concept,
                    purpose=concept,
                    algorithm=concept
                )
                
                # Adjust options based on difficulty
                options = template["options"].copy()
                if difficulty == "hard":
                    # Make options more similar for harder difficulty
                    options = [f"Advanced {opt}" for opt in options]
                elif difficulty == "easy":
                    # Make options more distinct for easier difficulty
                    options = [f"Simple {opt}" for opt in options]
                
                # Shuffle options but keep track of correct answer
                correct_index = template["correct"]
                correct_answer = options[correct_index]
                
                # Shuffle options
                random.shuffle(options)
                new_correct_index = options.index(correct_answer)
                
                question = {
                    "question_text": question_text,
                    "question_type": "multiple_choice",
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": f"This question tests understanding of {concept} in {topic}",
                    "difficulty": difficulty,
                    "points": self._get_points_for_difficulty(difficulty)
                }
                
                questions.append(question)
            
            return {
                "questions": questions,
                "validation": {
                    "is_valid": True,
                    "quality_score": 85,
                    "generator": "simple"
                },
                "status": "generated"
            }
            
        except Exception as e:
            return {
                "questions": [],
                "validation": {
                    "is_valid": False,
                    "quality_score": 0,
                    "issues": [str(e)]
                },
                "status": "failed"
            }
    
    def _get_points_for_difficulty(self, difficulty: str) -> int:
        """Get points based on difficulty level."""
        points_map = {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
        return points_map.get(difficulty, 2)

# Test the simple generator
if __name__ == "__main__":
    generator = SimpleQuizGenerator()
    
    print("Testing Simple Quiz Generator")
    print("=" * 40)
    
    result = generator.generate_quiz("Python Programming", "medium", 3)
    
    if result["questions"]:
        print(f"✅ Generated {len(result['questions'])} questions")
        for i, q in enumerate(result["questions"], 1):
            print(f"\nQuestion {i}: {q['question_text']}")
            print(f"Options: {q['options']}")
            print(f"Correct: {q['correct_answer']}")
    else:
        print("❌ Failed to generate questions")
