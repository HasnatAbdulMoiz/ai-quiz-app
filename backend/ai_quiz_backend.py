# backend/ai_quiz_backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime
import os
from simple_quiz_generator import SimpleQuizGenerator
from ai_models import ai_quiz_generator

app = FastAPI(title="AI Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str
    options: List[str]
    correct_answer: str
    difficulty: str
    points: int

class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[QuestionCreate]
    time_limit: int
    is_public: bool

class AutoQuizCreate(BaseModel):
    title: str
    description: str
    topic: str
    difficulty: str
    total_questions: int
    time_limit: int
    is_public: bool
    user_id: int  # Add user_id to the request body

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[str]

# In-memory storage
users_db = []
quizzes_db = []
quiz_submissions_db = []

# AI Quiz Generator
class AIQuizGenerator:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key"),
            base_url="https://api.deepseek.com/v1"
        )
    
    def generate_quiz(self, topic: str, difficulty: str, total_questions: int):
        try:
            prompt = f"""
            Generate a high-quality {difficulty} level quiz about "{topic}" with exactly {total_questions} questions.
            
            IMPORTANT REQUIREMENTS:
            1. Questions must be educationally valuable and relevant to the topic
            2. Each question should test different aspects of the topic
            3. For multiple choice questions: provide 4 plausible options where only one is clearly correct
            4. Avoid obvious or trivial questions
            5. Make questions progressively challenging but appropriate for {difficulty} level
            6. Ensure correct answers are factually accurate
            7. Make incorrect options believable but clearly wrong to someone who knows the topic
            
            For each question, provide:
            - question_text: Clear, well-written question
            - question_type: "multiple_choice" (preferred), "true_false", or "short_answer"
            - options: For multiple choice, provide exactly 4 options. For true_false, use ["True", "False"]
            - correct_answer: The correct answer (must match one of the options exactly)
            - explanation: Brief explanation of why the answer is correct
            - points: 1-5 based on difficulty (easy=1-2, medium=2-3, hard=3-5)
            
            Format as JSON:
            {{
                "questions": [
                    {{
                        "question_text": "What is the primary purpose of [topic concept]?",
                        "question_type": "multiple_choice",
                        "options": [
                            "Option A - Correct answer",
                            "Option B - Plausible but wrong",
                            "Option C - Partially correct but incomplete",
                            "Option D - Clearly incorrect"
                        ],
                        "correct_answer": "Option A - Correct answer",
                        "explanation": "Brief explanation of why this is correct",
                        "difficulty": "{difficulty}",
                        "points": 2
                    }}
                ]
            }}
            
            Focus on creating questions that test understanding, not just memorization.
            """
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"AI Response: {content[:500]}...")  # Debug log
            
            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("No valid JSON found in AI response")
                
            json_str = content[start:end]
            
            try:
                data = json.loads(json_str)
                # Validate the generated data
                validated_data = self._validate_generated_quiz(data, total_questions)
                return validated_data
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                # Fallback: try to extract questions manually
                return self._extract_questions_manually(content, total_questions)
            
        except Exception as e:
            print(f"AI Generation Error: {e}")
            # Fallback to sample questions
            return self.get_fallback_questions(topic, difficulty, total_questions)
    
    def _validate_generated_quiz(self, data: dict, expected_questions: int) -> dict:
        """Validate and clean the generated quiz data."""
        if not isinstance(data, dict) or 'questions' not in data:
            raise ValueError("Invalid quiz data structure")
        
        questions = data['questions']
        if not isinstance(questions, list):
            raise ValueError("Questions must be a list")
        
        validated_questions = []
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                continue
                
            # Validate required fields
            if not question.get('question_text'):
                continue
                
            # Ensure question type is valid
            question_type = question.get('question_type', 'multiple_choice')
            if question_type not in ['multiple_choice', 'true_false', 'short_answer']:
                question_type = 'multiple_choice'
            
            # Validate options for multiple choice
            options = question.get('options', [])
            if question_type == 'multiple_choice':
                if not isinstance(options, list) or len(options) != 4:
                    # Generate default options if invalid
                    options = ["Option A", "Option B", "Option C", "Option D"]
            elif question_type == 'true_false':
                options = ["True", "False"]
            
            # Ensure correct answer exists and is valid
            correct_answer = question.get('correct_answer', '')
            if not correct_answer and options:
                correct_answer = options[0]  # Default to first option
            
            # Validate points
            points = question.get('points', 1)
            if not isinstance(points, int) or points < 1 or points > 5:
                points = 2  # Default points
            
            validated_question = {
                "question_text": question['question_text'],
                "question_type": question_type,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": question.get('explanation', 'No explanation provided'),
                "difficulty": question.get('difficulty', 'medium'),
                "points": points
            }
            
            validated_questions.append(validated_question)
        
        # Ensure we have the expected number of questions
        if len(validated_questions) < expected_questions:
            # Fill with additional questions if needed
            while len(validated_questions) < expected_questions:
                validated_questions.append(self._create_sample_question(topic, difficulty))
        
        return {"questions": validated_questions[:expected_questions]}
    
    def _create_sample_question(self, topic: str, difficulty: str) -> dict:
        """Create a sample question as fallback."""
        return {
            "question_text": f"Which of the following best describes {topic}?",
            "question_type": "multiple_choice",
            "options": [
                "A comprehensive understanding",
                "A basic overview", 
                "A detailed analysis",
                "A simple explanation"
            ],
            "correct_answer": "A comprehensive understanding",
            "explanation": f"This question tests understanding of {topic}",
            "difficulty": difficulty,
            "points": 2
        }
    
    def _extract_questions_manually(self, content: str, total_questions: int) -> dict:
        """Manually extract questions from AI response as fallback."""
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            if '?' in line and len(line.strip()) > 10:
                questions.append(self._create_sample_question("the topic", "medium"))
                if len(questions) >= total_questions:
                    break
        
        # Fill remaining questions if needed
        while len(questions) < total_questions:
            questions.append(self._create_sample_question("the topic", "medium"))
        
        return {"questions": questions[:total_questions]}

    def get_fallback_questions(self, topic: str, difficulty: str, total_questions: int):
        sample_questions = [
            {
                "question_text": f"What is the main concept of {topic}?",
                "question_type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "difficulty": difficulty,
                "points": 2
            },
            {
                "question_text": f"True or False: {topic} is an important topic in education.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "True",
                "difficulty": difficulty,
                "points": 1
            }
        ]
        return {"questions": sample_questions[:total_questions]}

ai_generator = AIQuizGenerator()
simple_generator = SimpleQuizGenerator()

# Root endpoint
@app.get("/")
def root():
    return {"message": "AI Quiz System API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# User endpoints
@app.post("/api/register")
def register_user(user: UserRegistration):
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": len(users_db) + 1,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "created_at": datetime.now().isoformat()
    }
    
    users_db.append(new_user)
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"]
        }
    }

@app.post("/api/login")
def login_user(user: UserLogin):
    for existing_user in users_db:
        if existing_user["email"] == user.email and existing_user["password"] == user.password:
            return {
                "message": "Login successful",
                "user": {
                    "id": existing_user["id"],
                    "name": existing_user["name"],
                    "email": existing_user["email"],
                    "role": existing_user["role"]
                }
            }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

# Quiz endpoints
@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate, user_id: int):
    quiz_id = str(uuid.uuid4())
    new_quiz = {
        "id": quiz_id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": [q.dict() for q in quiz.questions],
        "time_limit": quiz.time_limit,
        "is_public": quiz.is_public,
        "created_by": user_id,
        "created_at": datetime.now().isoformat(),
        "total_questions": len(quiz.questions),
        "total_points": sum(q.points for q in quiz.questions),
        "creation_type": "manual"
    }
    
    quizzes_db.append(new_quiz)
    
    return {
        "message": "Quiz created successfully",
        "quiz": {
            "id": new_quiz["id"],
            "title": new_quiz["title"],
            "description": new_quiz["description"],
            "total_questions": new_quiz["total_questions"],
            "total_points": new_quiz["total_points"],
            "time_limit": new_quiz["time_limit"]
        }
    }

@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(quiz: AutoQuizCreate):
    try:
        print(f"Generating quiz for topic: {quiz.topic}, difficulty: {quiz.difficulty}, questions: {quiz.total_questions}")
        
        # Try AI generation first, fallback to simple generator
        try:
            generated_data = ai_generator.generate_quiz(
                quiz.topic, 
                quiz.difficulty, 
                quiz.total_questions
            )
        except Exception as e:
            print(f"AI generation failed, using simple generator: {e}")
            generated_data = simple_generator.generate_quiz(
                quiz.topic,
                quiz.difficulty,
                quiz.total_questions
            )
        
        # Validate generated data
        if not generated_data or 'questions' not in generated_data:
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "AI Generation Failed",
                    "message": "AI failed to generate valid questions. Please try again with a different topic or check your API key.",
                    "suggestion": "Ensure your DEEPSEEK_API_KEY is set correctly in the environment variables."
                }
            )
        
        questions = generated_data['questions']
        if not isinstance(questions, list) or len(questions) == 0:
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "No Questions Generated",
                    "message": "No questions were generated by the AI. Please try again with a different topic.",
                    "suggestion": "Try using a more specific topic or different difficulty level."
                }
            )
        
        # Additional validation
        valid_questions = []
        for q in questions:
            if (isinstance(q, dict) and 
                q.get('question_text') and 
                q.get('options') and 
                q.get('correct_answer')):
                valid_questions.append(q)
        
        if len(valid_questions) == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Invalid Question Format",
                    "message": "Generated questions are not in the correct format.",
                    "suggestion": "Please try again or contact support if the issue persists."
                }
            )
        
        quiz_id = str(uuid.uuid4())
        new_quiz = {
            "id": quiz_id,
            "title": quiz.title,
            "description": quiz.description,
            "questions": valid_questions,
            "time_limit": quiz.time_limit,
            "is_public": quiz.is_public,
            "created_by": quiz.user_id,
            "created_at": datetime.now().isoformat(),
            "total_questions": len(valid_questions),
            "total_points": sum(q.get("points", 1) for q in valid_questions),
            "creation_type": "ai_generated",
            "topic": quiz.topic,
            "difficulty": quiz.difficulty
        }
        
        quizzes_db.append(new_quiz)
        
        return {
            "message": "AI-generated quiz created successfully",
            "quiz": {
                "id": new_quiz["id"],
                "title": new_quiz["title"],
                "description": new_quiz["description"],
                "total_questions": new_quiz["total_questions"],
                "total_points": new_quiz["total_points"],
                "time_limit": new_quiz["time_limit"],
                "topic": new_quiz["topic"],
                "difficulty": new_quiz["difficulty"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI Generation Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Server Error",
                "message": f"AI generation failed: {str(e)}",
                "suggestion": "Please check your API configuration and try again."
            }
        )

@app.get("/api/quizzes")
def get_quizzes(user_id: Optional[int] = None):
    if user_id:
        user_quizzes = [q for q in quizzes_db if q["created_by"] == user_id or q["is_public"]]
        return {"quizzes": user_quizzes}
    else:
        public_quizzes = [q for q in quizzes_db if q["is_public"]]
        return {"quizzes": public_quizzes}

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Sorry, the quiz you're looking for doesn't exist or has been removed")
    
    # Remove correct answers for security
    quiz_copy = quiz.copy()
    for question in quiz_copy["questions"]:
        if "correct_answer" in question:
            del question["correct_answer"]
    
    return {"quiz": quiz_copy}

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission: QuizSubmission, user_id: int):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Sorry, the quiz you're looking for doesn't exist or has been removed")
    
    # Calculate score
    score = 0
    total_points = quiz["total_points"]
    
    for i, question in enumerate(quiz["questions"]):
        if i < len(submission.answers):
            if question["correct_answer"].lower() == submission.answers[i].lower():
                score += question["points"]
    
    percentage = (score / total_points) * 100 if total_points > 0 else 0
    
    # Save submission
    submission_record = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz_id,
        "user_id": user_id,
        "answers": submission.answers,
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "submitted_at": datetime.now().isoformat()
    }
    
    quiz_submissions_db.append(submission_record)
    
    return {
        "message": "Quiz submitted successfully",
        "result": {
            "score": score,
            "total_points": total_points,
            "percentage": round(percentage, 2)
        }
    }

@app.get("/api/users/{user_id}/submissions")
def get_user_submissions(user_id: int):
    user_submissions = [s for s in quiz_submissions_db if s["user_id"] == user_id]
    return {"submissions": user_submissions}

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Quiz backend on http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)