# backend/registration_backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv
from ai_models import ai_quiz_generator
from env_config import DEFAULT_AI_MODEL, print_ai_status

# Load environment variables
load_dotenv()

# Security Functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, stored_hash = hashed_password.split(':')
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash
    except ValueError:
        return False

app = FastAPI(title="Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# User model
class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    role: str
    school_id: Optional[str] = None  # Add school_id for school users

class UserLogin(BaseModel):
    email: str
    password: str

# School models
class SchoolRegistration(BaseModel):
    school_name: str
    school_type: str  # elementary, middle, high, university
    address: str
    city: str
    state: str
    country: str
    phone: str
    email: str
    principal_name: str
    established_year: Optional[str] = ""  # Made optional, will be filled by teacher
    max_students: Optional[str] = ""  # Made optional, will be filled by teacher
    max_teachers: Optional[str] = ""  # Made optional, will be filled by teacher

class SchoolTeacherRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    school_id: str

class StudentCreationRequest(BaseModel):
    name: str
    email: str
    password: str
    school_id: str
    teacher_id: int


class QuizGenerationRequest(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: str
    num_questions: int
    time_limit: int = 60
    is_public: bool = True
    user_id: int = 1
    user_role: str = None
    
    class Config:
        extra = "ignore"  # Ignore extra fields

class QuizCreate(BaseModel):
    title: str
    description: str
    time_limit: int
    is_public: bool = True
    questions: list = []
    user_id: int = 1
    user_role: str = None

# In-memory storage (in real app, this would be a database)
users_db = []
quizzes_db = []

# Super Admin Configuration - SECURE ENVIRONMENT VARIABLES
SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL', 'hasanatk007@gmail.com')
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD', 'Reshun@786')

# School system storage
schools_db = []
school_quizzes_db = {}  # school_id -> quizzes
quiz_results_db = []

# Initialize super admin on startup
def create_super_admin():
    """Create the super admin user if it doesn't exist"""
    super_admin_exists = any(user.get('email') == SUPER_ADMIN_EMAIL for user in users_db)
    if not super_admin_exists:
        # Hash the super admin password
        hashed_password = hash_password(SUPER_ADMIN_PASSWORD)
        
        super_admin = {
            "id": 1,
            "name": "Super Admin",
            "email": SUPER_ADMIN_EMAIL,
            "password": hashed_password,  # Now securely hashed
            "role": "super_admin",
            "created_at": datetime.now().isoformat()
        }
        users_db.insert(0, super_admin)  # Insert at beginning
        print(f"Super Admin created: {SUPER_ADMIN_EMAIL}")
        print("Password is securely hashed!")

# Create super admin on startup
create_super_admin()

# Enhanced AI Quiz Generator with Realistic Questions
class EnhancedQuizGenerator:
    def __init__(self):
        self.subject_questions = {
            "python": {
                "easy": [
                    {
                        "question_text": "What is the correct syntax to create a variable in Python?",
                        "options": ["var x = 5", "x = 5", "int x = 5", "variable x = 5"],
                        "correct_answer": "x = 5",
                        "explanation": "Python uses simple assignment syntax without type declaration. Variables are created when you assign a value to them."
                    },
                    {
                        "question_text": "Which keyword is used to define a function in Python?",
                        "options": ["function", "def", "func", "define"],
                        "correct_answer": "def",
                        "explanation": "The 'def' keyword is used to define functions in Python. Example: def my_function():"
                    },
                    {
                        "question_text": "What does the 'len()' function do in Python?",
                        "options": ["Returns the length of a string", "Returns the length of a list", "Returns the length of any sequence", "All of the above"],
                        "correct_answer": "All of the above",
                        "explanation": "len() function returns the length of any sequence including strings, lists, tuples, dictionaries, etc."
                    },
                    {
                        "question_text": "Which of the following is NOT a Python data type?",
                        "options": ["list", "dictionary", "array", "tuple"],
                        "correct_answer": "array",
                        "explanation": "Python has lists, dictionaries, and tuples, but not arrays (though NumPy arrays exist)."
                    },
                    {
                        "question_text": "What is the output of print(2 ** 3) in Python?",
                        "options": ["6", "8", "9", "5"],
                        "correct_answer": "8",
                        "explanation": "** is the exponentiation operator, so 2 ** 3 = 2^3 = 8."
                    }
                ],
                "medium": [
                    {
                        "question_text": "What is the difference between '==' and 'is' in Python?",
                        "options": [
                            "No difference, they are the same",
                            "'==' compares values, 'is' compares object identity",
                            "'is' compares values, '==' compares object identity",
                            "Both compare object identity"
                        ],
                        "correct_answer": "'==' compares values, 'is' compares object identity",
                        "explanation": "'==' checks if values are equal, while 'is' checks if two variables refer to the same object in memory."
                    }
                ],
                "hard": [
                    {
                        "question_text": "Which statement about Python decorators is correct?",
                        "options": [
                            "They modify the behavior of functions",
                            "They are only used for classes",
                            "They cannot be chained",
                            "They are the same as functions"
                        ],
                        "correct_answer": "They modify the behavior of functions",
                        "explanation": "Decorators are functions that modify the behavior of other functions without changing their code."
                    }
                ]
            },
            "mathematics": {
                "easy": [
                                {
                                                "question_text": "What is 5 + 3?",
                                                "options": [
                                                                "6",
                                                                "7",
                                                                "8",
                                                                "9"
                                                ],
                                                "correct_answer": "8",
                                                "explanation": "5 + 3 = 8"
                                },
                                {
                                                "question_text": "What is 12 - 7?",
                                                "options": [
                                                                "4",
                                                                "5",
                                                                "6",
                                                                "7"
                                                ],
                                                "correct_answer": "5",
                                                "explanation": "12 - 7 = 5"
                                },
                                {
                                                "question_text": "What is 6 \u00d7 4?",
                                                "options": [
                                                                "20",
                                                                "22",
                                                                "24",
                                                                "26"
                                                ],
                                                "correct_answer": "24",
                                                "explanation": "6 \u00d7 4 = 24"
                                },
                                {
                                                "question_text": "What is 15 \u00f7 3?",
                                                "options": [
                                                                "3",
                                                                "4",
                                                                "5",
                                                                "6"
                                                ],
                                                "correct_answer": "5",
                                                "explanation": "15 \u00f7 3 = 5"
                                },
                                {
                                                "question_text": "What is 2\u00b2?",
                                                "options": [
                                                                "2",
                                                                "3",
                                                                "4",
                                                                "5"
                                                ],
                                                "correct_answer": "4",
                                                "explanation": "2\u00b2 = 2 \u00d7 2 = 4"
                                },
                                {
                                                "question_text": "What is the square root of 16?",
                                                "options": [
                                                                "2",
                                                                "3",
                                                                "4",
                                                                "5"
                                                ],
                                                "correct_answer": "4",
                                                "explanation": "\u221a16 = 4 because 4\u00b2 = 16"
                                },
                                {
                                                "question_text": "What is 10% of 50?",
                                                "options": [
                                                                "5",
                                                                "10",
                                                                "15",
                                                                "20"
                                                ],
                                                "correct_answer": "5",
                                                "explanation": "10% of 50 = 0.10 \u00d7 50 = 5"
                                },
                                {
                                                "question_text": "What is 3/4 as a decimal?",
                                                "options": [
                                                                "0.25",
                                                                "0.5",
                                                                "0.75",
                                                                "1.0"
                                                ],
                                                "correct_answer": "0.75",
                                                "explanation": "3/4 = 0.75"
                                },
                                {
                                                "question_text": "What is the perimeter of a square with side length 5?",
                                                "options": [
                                                                "15",
                                                                "20",
                                                                "25",
                                                                "30"
                                                ],
                                                "correct_answer": "20",
                                                "explanation": "Perimeter = 4 \u00d7 side = 4 \u00d7 5 = 20"
                                },
                                {
                                                "question_text": "What is the area of a rectangle with length 6 and width 4?",
                                                "options": [
                                                                "20",
                                                                "22",
                                                                "24",
                                                                "26"
                                                ],
                                                "correct_answer": "24",
                                                "explanation": "Area = length \u00d7 width = 6 \u00d7 4 = 24"
                                }
                ],
                "medium": [
                                {
                                                "question_text": "Solve for x: 2x + 5 = 13",
                                                "options": [
                                                                "x = 3",
                                                                "x = 4",
                                                                "x = 5",
                                                                "x = 6"
                                                ],
                                                "correct_answer": "x = 4",
                                                "explanation": "2x + 5 = 13, so 2x = 8, therefore x = 4"
                                },
                                {
                                                "question_text": "What is the slope of the line y = 2x + 3?",
                                                "options": [
                                                                "2",
                                                                "3",
                                                                "5",
                                                                "6"
                                                ],
                                                "correct_answer": "2",
                                                "explanation": "In y = mx + b, m is the slope, so slope = 2"
                                },
                                {
                                                "question_text": "What is the derivative of x\u00b2?",
                                                "options": [
                                                                "x",
                                                                "2x",
                                                                "x\u00b2",
                                                                "2x\u00b2"
                                                ],
                                                "correct_answer": "2x",
                                                "explanation": "Using the power rule: d/dx(x\u00b2) = 2x"
                                },
                                {
                                                "question_text": "What is sin(30\u00b0)?",
                                                "options": [
                                                                "0",
                                                                "0.5",
                                                                "1",
                                                                "\u221a2/2"
                                                ],
                                                "correct_answer": "0.5",
                                                "explanation": "sin(30\u00b0) = 1/2 = 0.5"
                                },
                                {
                                                "question_text": "What is the value of \u03c0 (pi) to 2 decimal places?",
                                                "options": [
                                                                "3.14",
                                                                "3.15",
                                                                "3.16",
                                                                "3.17"
                                                ],
                                                "correct_answer": "3.14",
                                                "explanation": "\u03c0 \u2248 3.14159, so to 2 decimal places it's 3.14"
                                }
                ],
                "hard": [
                                {
                                                "question_text": "What is the integral of 2x?",
                                                "options": [
                                                                "x\u00b2",
                                                                "x\u00b2 + C",
                                                                "2x\u00b2",
                                                                "x\u00b2/2"
                                                ],
                                                "correct_answer": "x\u00b2 + C",
                                                "explanation": "\u222b2x dx = 2\u222bx dx = 2(x\u00b2/2) + C = x\u00b2 + C"
                                },
                                {
                                                "question_text": "What is the limit of (x\u00b2 - 1)/(x - 1) as x approaches 1?",
                                                "options": [
                                                                "0",
                                                                "1",
                                                                "2",
                                                                "undefined"
                                                ],
                                                "correct_answer": "2",
                                                "explanation": "Using L'H\u00f4pital's rule or factoring: lim(x\u21921) (x\u00b2-1)/(x-1) = lim(x\u21921) (x+1) = 2"
                                }
                ]
},
            "english": {
                "easy": [
                                {
                                                "question_text": "Which word is a noun in the sentence: 'The cat runs quickly'?",
                                                "options": [
                                                                "The",
                                                                "cat",
                                                                "runs",
                                                                "quickly"
                                                ],
                                                "correct_answer": "cat",
                                                "explanation": "Cat is a noun as it names a person, place, or thing"
                                },
                                {
                                                "question_text": "Which word is a verb in the sentence: 'She sings beautifully'?",
                                                "options": [
                                                                "She",
                                                                "sings",
                                                                "beautifully",
                                                                "None"
                                                ],
                                                "correct_answer": "sings",
                                                "explanation": "Sings is a verb as it shows action"
                                },
                                {
                                                "question_text": "What is the plural of 'child'?",
                                                "options": [
                                                                "childs",
                                                                "children",
                                                                "childes",
                                                                "child"
                                                ],
                                                "correct_answer": "children",
                                                "explanation": "Children is the irregular plural form of child"
                                },
                                {
                                                "question_text": "Which sentence is correct?",
                                                "options": [
                                                                "I am going to school",
                                                                "I is going to school",
                                                                "I are going to school",
                                                                "I be going to school"
                                                ],
                                                "correct_answer": "I am going to school",
                                                "explanation": "Use 'am' with 'I' in present continuous tense"
                                },
                                {
                                                "question_text": "What is the past tense of 'go'?",
                                                "options": [
                                                                "goed",
                                                                "went",
                                                                "gone",
                                                                "going"
                                                ],
                                                "correct_answer": "went",
                                                "explanation": "Went is the irregular past tense of go"
                                }
                ],
                "medium": [
                                {
                                                "question_text": "Which sentence uses correct punctuation?",
                                                "options": [
                                                                "Hello, how are you?",
                                                                "Hello how are you?",
                                                                "Hello, how are you",
                                                                "Hello; how are you?"
                                                ],
                                                "correct_answer": "Hello, how are you?",
                                                "explanation": "Use comma after greeting and question mark at the end"
                                },
                                {
                                                "question_text": "What is the correct form: 'There ___ many books on the shelf'?",
                                                "options": [
                                                                "is",
                                                                "are",
                                                                "was",
                                                                "were"
                                                ],
                                                "correct_answer": "are",
                                                "explanation": "Use 'are' with plural subject 'books'"
                                }
                ]
},
            "science": {
                "easy": [
                                {
                                                "question_text": "What is the chemical symbol for water?",
                                                "options": [
                                                                "H2O",
                                                                "CO2",
                                                                "NaCl",
                                                                "O2"
                                                ],
                                                "correct_answer": "H2O",
                                                "explanation": "Water is made of 2 hydrogen atoms and 1 oxygen atom"
                                },
                                {
                                                "question_text": "What planet is closest to the Sun?",
                                                "options": [
                                                                "Venus",
                                                                "Earth",
                                                                "Mercury",
                                                                "Mars"
                                                ],
                                                "correct_answer": "Mercury",
                                                "explanation": "Mercury is the first planet from the Sun"
                                },
                                {
                                                "question_text": "What gas do plants produce during photosynthesis?",
                                                "options": [
                                                                "Carbon dioxide",
                                                                "Oxygen",
                                                                "Nitrogen",
                                                                "Hydrogen"
                                                ],
                                                "correct_answer": "Oxygen",
                                                "explanation": "Plants produce oxygen as a byproduct of photosynthesis"
                                },
                                {
                                                "question_text": "What is the hardest natural substance?",
                                                "options": [
                                                                "Gold",
                                                                "Iron",
                                                                "Diamond",
                                                                "Silver"
                                                ],
                                                "correct_answer": "Diamond",
                                                "explanation": "Diamond is the hardest known natural material"
                                },
                                {
                                                "question_text": "What is the speed of light?",
                                                "options": [
                                                                "300,000 km/s",
                                                                "150,000 km/s",
                                                                "600,000 km/s",
                                                                "450,000 km/s"
                                                ],
                                                "correct_answer": "300,000 km/s",
                                                "explanation": "Light travels at approximately 300,000 km/s in vacuum"
                                }
                ],
                "medium": [
                                {
                                                "question_text": "What is the atomic number of carbon?",
                                                "options": [
                                                                "6",
                                                                "12",
                                                                "14",
                                                                "16"
                                                ],
                                                "correct_answer": "6",
                                                "explanation": "Carbon has 6 protons, so its atomic number is 6"
                                },
                                {
                                                "question_text": "What is the formula for photosynthesis?",
                                                "options": [
                                                                "6CO2 + 6H2O \u2192 C6H12O6 + 6O2",
                                                                "6CO2 + 6H2O \u2192 C6H12O6 + 6CO2",
                                                                "6O2 + 6H2O \u2192 C6H12O6 + 6CO2",
                                                                "6CO2 + 6O2 \u2192 C6H12O6 + 6H2O"
                                                ],
                                                "correct_answer": "6CO2 + 6H2O \u2192 C6H12O6 + 6O2",
                                                "explanation": "Plants use carbon dioxide and water to produce glucose and oxygen"
                                }
                ]
},
            "history": {
                "easy": [
                                {
                                                "question_text": "In which year did World War II end?",
                                                "options": [
                                                                "1944",
                                                                "1945",
                                                                "1946",
                                                                "1947"
                                                ],
                                                "correct_answer": "1945",
                                                "explanation": "World War II ended in 1945"
                                },
                                {
                                                "question_text": "Who was the first President of the United States?",
                                                "options": [
                                                                "John Adams",
                                                                "Thomas Jefferson",
                                                                "George Washington",
                                                                "Benjamin Franklin"
                                                ],
                                                "correct_answer": "George Washington",
                                                "explanation": "George Washington was the first US President (1789-1797)"
                                },
                                {
                                                "question_text": "Which empire was ruled by Julius Caesar?",
                                                "options": [
                                                                "Greek Empire",
                                                                "Roman Empire",
                                                                "Persian Empire",
                                                                "Egyptian Empire"
                                                ],
                                                "correct_answer": "Roman Empire",
                                                "explanation": "Julius Caesar was a Roman general and statesman"
                                },
                                {
                                                "question_text": "In which country was the Great Wall built?",
                                                "options": [
                                                                "Japan",
                                                                "Korea",
                                                                "China",
                                                                "Mongolia"
                                                ],
                                                "correct_answer": "China",
                                                "explanation": "The Great Wall was built in China to protect against invasions"
                                },
                                {
                                                "question_text": "What was the name of the ship that brought the Pilgrims to America?",
                                                "options": [
                                                                "Santa Maria",
                                                                "Mayflower",
                                                                "Titanic",
                                                                "Endeavour"
                                                ],
                                                "correct_answer": "Mayflower",
                                                "explanation": "The Mayflower brought the Pilgrims to America in 1620"
                                }
                ],
                "medium": [
                                {
                                                "question_text": "Which pharaoh built the Great Pyramid of Giza?",
                                                "options": [
                                                                "Ramses II",
                                                                "Tutankhamun",
                                                                "Khufu",
                                                                "Cleopatra"
                                                ],
                                                "correct_answer": "Khufu",
                                                "explanation": "Khufu (Cheops) built the Great Pyramid around 2580-2560 BC"
                                },
                                {
                                                "question_text": "In which year did the Berlin Wall fall?",
                                                "options": [
                                                                "1987",
                                                                "1988",
                                                                "1989",
                                                                "1990"
                                                ],
                                                "correct_answer": "1989",
                                                "explanation": "The Berlin Wall fell on November 9, 1989"
                                }
                ]
}
        }
    
    def generate_questions(self, subject: str, difficulty: str, num_questions: int):
        questions = []
        subject_lower = subject.lower()
        
        # Determine which subject questions to use
        if "python" in subject_lower or "programming" in subject_lower:
            subject_key = "python"
        elif "javascript" in subject_lower or "js" in subject_lower:
            subject_key = "javascript"
        elif "math" in subject_lower or "mathematics" in subject_lower or "calculus" in subject_lower:
            subject_key = "mathematics"
        else:
            # Default to general programming questions
            subject_key = "python"
        
        # Get questions for the subject and difficulty
        if subject_key in self.subject_questions and difficulty in self.subject_questions[subject_key]:
            available_questions = self.subject_questions[subject_key][difficulty]
        else:
            # Fallback to easy python questions
            available_questions = self.subject_questions["python"]["easy"]
        
        # Select questions (repeat if needed)
        for i in range(num_questions):
            question_template = available_questions[i % len(available_questions)]
            
            # Calculate points based on difficulty
            if difficulty == "easy":
                points = 1
            elif difficulty == "medium":
                points = 2
            else:  # hard
                points = 3
            
            question = {
                "id": f"q_{i+1}",
                "question_text": question_template["question_text"],
                "question_type": "multiple_choice",
                "options": question_template["options"],
                "correct_answer": question_template["correct_answer"],
                "explanation": question_template["explanation"],
                "difficulty": difficulty,
                "points": points
            }
            questions.append(question)
        
        return questions

# Initialize both generators
enhanced_generator = EnhancedQuizGenerator()
# ai_quiz_generator is already imported from ai_models.py

@app.get("/")
def read_root():
    return {"message": "AI-Powered Quiz System Agent API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# Handle CORS preflight requests
@app.options("/{path:path}")
async def options_handler(path: str):
    from fastapi.responses import Response
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.post("/api/register")
def register_user(user: UserRegistration):
    # Prevent admin registration - only super admin can access admin features
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Admin registration is not allowed. Only super admin can access admin features.")
    
    # Check if user already exists
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with hashed password
    hashed_password = hash_password(user.password)
    new_user = {
        "id": len(users_db) + 1,
        "name": user.name,
        "email": user.email,
        "password": hashed_password,  # Now securely hashed
        "role": user.role,
        "created_at": "2024-01-01T00:00:00Z"
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

# School registration endpoint
@app.post("/api/schools/register")
def register_school(school_data: SchoolRegistration, teacher_data: SchoolTeacherRegistration):
    """Register a new school with teacher"""
    try:
        # Create school
        school_id = f"school_{len(schools_db) + 1}"
        school = {
            "id": school_id,
            "name": school_data.school_name,
            "type": school_data.school_type,
            "address": school_data.address,
            "city": school_data.city,
            "state": school_data.state,
            "country": school_data.country,
            "phone": school_data.phone,
            "email": school_data.email,
            "principal_name": school_data.principal_name,
            "established_year": school_data.established_year or "",
            "max_students": school_data.max_students or "",
            "max_teachers": school_data.max_teachers or "",
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        schools_db.append(school)
        
        # Create school teacher with hashed password
        teacher_id = len(users_db) + 1
        hashed_teacher_password = hash_password(teacher_data.password)
        teacher = {
            "id": teacher_id,
            "name": teacher_data.name,
            "email": teacher_data.email,
            "password": hashed_teacher_password,  # Now securely hashed
            "phone": teacher_data.phone,
            "role": "teacher",
            "school_id": school_id,
            "created_at": datetime.now().isoformat()
        }
        
        users_db.append(teacher)
        
        # Initialize school quizzes
        school_quizzes_db[school_id] = []
        
        return {
            "message": "School registered successfully",
            "school": school,
            "teacher": {
                "id": teacher["id"],
                "name": teacher["name"],
                "email": teacher["email"],
                "role": teacher["role"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create school: {str(e)}")

@app.post("/api/teachers/create-student")
def create_student_account(student_data: StudentCreationRequest):
    """Allow teachers to create student accounts for their school"""
    try:
        print(f"Creating student with data: {student_data}")
        print(f"Student data school_id: {student_data.school_id}")
        print(f"Student data teacher_id: {student_data.teacher_id}")
        
        # Verify the teacher exists and has the right school
        teacher = next((u for u in users_db if u["id"] == student_data.teacher_id), None)
        if not teacher:
            print(f"Teacher not found with ID: {student_data.teacher_id}")
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        print(f"Found teacher: {teacher}")
        print(f"Teacher school_id: {teacher.get('school_id')}")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can create student accounts")
        
        if teacher.get("school_id") != student_data.school_id:
            print(f"School ID mismatch: teacher has {teacher.get('school_id')}, student data has {student_data.school_id}")
            raise HTTPException(status_code=403, detail="Teacher can only create students for their own school")
        
        # Check if student email already exists
        for existing_user in users_db:
            if existing_user["email"] == student_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new student with hashed password
        student_id = len(users_db) + 1
        hashed_student_password = hash_password(student_data.password)
        student = {
            "id": student_id,
            "name": student_data.name,
            "email": student_data.email,
            "password": hashed_student_password,  # Now securely hashed
            "role": "student",
            "school_id": student_data.school_id,
            "created_by_teacher": student_data.teacher_id,
            "created_at": datetime.now().isoformat()
        }
        
        users_db.append(student)
        
        return {
            "message": "Student account created successfully",
            "student": {
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "role": student["role"],
                "school_id": student["school_id"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create student account: {str(e)}")

@app.get("/api/teachers/{teacher_id}/students")
def get_teacher_students(teacher_id: int):
    """Get all students created by a specific teacher"""
    try:
        # Verify the teacher exists
        teacher = next((u for u in users_db if u["id"] == teacher_id), None)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        if teacher["role"] != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can view their students")
        
        # Get all students created by this teacher
        students = [u for u in users_db if u.get("created_by_teacher") == teacher_id and u["role"] == "student"]
        
        return {
            "teacher": {
                "id": teacher["id"],
                "name": teacher["name"],
                "school_id": teacher["school_id"]
            },
            "students": students
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch students: {str(e)}")

@app.get("/api/super-admin/all-credentials")
def get_all_credentials(admin_id: int):
    """Get all user credentials for super admin"""
    try:
        # Verify the admin is super admin
        admin_user = next((u for u in users_db if u["id"] == admin_id), None)
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        if admin_user["role"] != "super_admin":
            raise HTTPException(status_code=403, detail="Access denied. Super admin role required.")
        
        # Get all users with their credentials (passwords are hashed)
        all_users = []
        for user in users_db:
            if user["role"] != "super_admin":  # Don't show super admin credentials
                all_users.append({
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "password": user["password"],  # Now securely hashed
                    "role": user["role"],
                    "school_id": user.get("school_id"),
                    "created_at": user.get("created_at"),
                    "created_by_teacher": user.get("created_by_teacher")
                })
        
        return {
            "message": "All user credentials retrieved",
            "users": all_users,
            "total_count": len(all_users)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch credentials: {str(e)}")

@app.post("/api/login")
def login_user(user: UserLogin):
    # Find user
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            # Check if password is hashed or plain text (for backward compatibility)
            stored_password = existing_user["password"]
            
            # If password contains ':' it's hashed, otherwise it's plain text
            if ':' in stored_password:
                # Verify hashed password
                if verify_password(user.password, stored_password):
                    return {
                        "message": "Login successful",
                        "user": {
                            "id": existing_user["id"],
                            "name": existing_user["name"],
                            "email": existing_user["email"],
                            "role": existing_user["role"],
                            "school_id": existing_user.get("school_id")
                        }
                    }
            else:
                # Legacy plain text password (for existing users)
                if stored_password == user.password:
                    # Hash the password for future use
                    existing_user["password"] = hash_password(user.password)
                    return {
                        "message": "Login successful",
                        "user": {
                            "id": existing_user["id"],
                            "name": existing_user["name"],
                            "email": existing_user["email"],
                            "role": existing_user["role"],
                            "school_id": existing_user.get("school_id")
                        }
                    }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/api/users")
def get_users():
    return {"users": users_db}

@app.get("/api/debug/users")
def debug_users():
    """Debug endpoint to see all users"""
    return {
        "users": users_db,
        "schools": schools_db,
        "total_users": len(users_db),
        "total_schools": len(schools_db)
    }

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@app.get("/api/admin/users")
def get_all_users_for_admin(admin_id: int):
    """Get all users for admin dashboard - only accessible by super admin"""
    # Check if the requesting user is a super admin
    admin_user = next((u for u in users_db if u["id"] == admin_id), None)
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    if admin_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super admin role required.")
    
    # Return all users with their details
    return {
        "users": users_db,
        "total_users": len(users_db),
        "teachers": [u for u in users_db if u["role"] == "teacher"],
        "students": [u for u in users_db if u["role"] == "student"],
        "admins": [u for u in users_db if u["role"] == "admin"]
    }

@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin_id: int):
    """Get comprehensive admin dashboard statistics - only accessible by super admin"""
    # Check if the requesting user is a super admin
    admin_user = next((u for u in users_db if u["id"] == admin_id), None)
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    if admin_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super admin role required.")
    
    # Calculate statistics
    teachers = [u for u in users_db if u["role"] == "teacher"]
    students = [u for u in users_db if u["role"] == "student"]
    admins = [u for u in users_db if u["role"] == "admin"]
    
    # Quiz statistics
    total_quizzes = len(quizzes_db)
    total_attempts = len(quiz_results_db)
    
    # Calculate average scores
    if quiz_results_db:
        avg_score = sum(r.get("percentage", 0) for r in quiz_results_db) / len(quiz_results_db)
        pass_rate = len([r for r in quiz_results_db if r.get("percentage", 0) >= 60]) / len(quiz_results_db) * 100
    else:
        avg_score = 0
        pass_rate = 0
    
    return {
        "overview": {
            "total_users": len(users_db),
            "total_teachers": len(teachers),
            "total_students": len(students),
            "total_admins": len(admins),
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 2),
            "pass_rate": round(pass_rate, 2)
        },
        "users": users_db,
        "teachers": teachers,
        "students": students,
        "admins": admins,
        "recent_activity": quiz_results_db[-10:] if quiz_results_db else []
    }

@app.delete("/api/admin/users/{user_id}")
def delete_user(admin_id: int, user_id: int):
    """Delete a user - only accessible by super admin"""
    # Check if the requesting user is a super admin
    admin_user = next((u for u in users_db if u["id"] == admin_id), None)
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    if admin_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super admin role required.")
    
    # Check if user exists
    user_to_delete = next((u for u in users_db if u["id"] == user_id), None)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user_id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Remove user from database
    users_db[:] = [u for u in users_db if u["id"] != user_id]
    
    # Also remove user's quiz results
    quiz_results_db[:] = [r for r in quiz_results_db if r.get("user_id") != user_id]
    
    # Remove quizzes created by this user
    quizzes_db[:] = [q for q in quizzes_db if q.get("created_by") != user_id]
    
    return {"message": f"User {user_to_delete['name']} has been deleted successfully"}

# AI Model Information
@app.get("/api/ai/models")
def get_available_ai_models():
    """Get information about available AI models"""
    available_models = []
    
    for model, key in ai_generator.api_keys.items():
        if key:
            available_models.append({
                "name": model,
                "status": "available",
                "endpoint": ai_generator.endpoints.get(model, "Unknown")
            })
        else:
            available_models.append({
                "name": model,
                "status": "not_configured",
                "endpoint": ai_generator.endpoints.get(model, "Unknown")
            })
    
    return {
        "available_models": available_models,
        "default_model": os.getenv('DEFAULT_AI_MODEL', 'gemini'),
        "setup_instructions": {
            "1": "Copy env_template.txt to .env",
            "2": "Add your API keys to .env file",
            "3": "Restart the server",
            "4": "AI generation will work automatically"
        }
    }

@app.post("/api/ai/test")
def test_ai_generation(test_request: dict):
    """Test AI generation with a specific model"""
    try:
        subject = test_request.get('subject', 'Python Programming')
        difficulty = test_request.get('difficulty', 'medium')
        num_questions = test_request.get('num_questions', 2)
        model = test_request.get('model', os.getenv('DEFAULT_AI_MODEL', 'gemini'))
        
        ai_questions = ai_generator.generate_quiz_with_ai(
            subject, difficulty, num_questions, model
        )
        
        if ai_questions:
            return {
                "status": "success",
                "model_used": model,
                "questions_generated": len(ai_questions),
                "questions": [
                    {
                        "question_text": q.question_text,
                        "options": q.options,
                        "correct_answer": q.correct_answer,
                        "explanation": q.explanation
                    } for q in ai_questions
                ]
            }
        else:
            return {
                "status": "fallback",
                "message": "AI generation failed, using template-based questions",
                "model_attempted": model
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI generation failed: {str(e)}"
        }

# Quiz management endpoints
@app.get("/api/quizzes")
def get_quizzes(user_id: int = None):
    if user_id:
        # Get user information
        user = next((u for u in users_db if u["id"] == user_id), None)
        if not user:
            return {"quizzes": [], "total": 0}
        
        user_quizzes = []
        
        if user["role"] == "student":
            # Students see:
            # 1. Quizzes created by their teacher
            # 2. Quizzes created by themselves
            # 3. Public quizzes
            teacher_id = user.get("created_by_teacher")
            user_quizzes = [
                q for q in quizzes_db 
                if (q.get("created_by") == user_id or  # Own quizzes
                    q.get("created_by_teacher") == teacher_id or  # Teacher's quizzes
                    q.get("is_public", True))  # Public quizzes
            ]
        elif user["role"] == "teacher":
            # Teachers see:
            # 1. Quizzes they created
            # 2. Quizzes created by their students
            # 3. Public quizzes
            student_ids = [u["id"] for u in users_db if u.get("created_by_teacher") == user_id]
            user_quizzes = [
                q for q in quizzes_db 
                if (q.get("created_by") == user_id or  # Own quizzes
                    q.get("created_by") in student_ids or  # Students' quizzes
                    q.get("is_public", True))  # Public quizzes
            ]
        elif user["role"] in ["admin", "super_admin"]:
            # Admins see all quizzes
            user_quizzes = quizzes_db
        else:
            # Other roles see public quizzes and their own
            user_quizzes = [q for q in quizzes_db if q.get("created_by") == user_id or q.get("is_public", True)]
        
        return {"quizzes": user_quizzes, "total": len(user_quizzes)}
    
    return {"quizzes": quizzes_db, "total": len(quizzes_db)}

@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate):
    # Allow all users including guests to create quizzes
    if quiz.user_role not in ["teacher", "admin", "super_admin", "student", "guest"]:
        raise HTTPException(status_code=403, detail="Invalid user role for quiz creation")
    
    import uuid
    from datetime import datetime
    
    quiz_id = str(uuid.uuid4())
    
    # Get creator information
    creator = next((u for u in users_db if u["id"] == quiz.user_id), None)
    teacher_id = creator.get("created_by_teacher") if creator and creator.get("role") == "student" else None
    school_id = creator.get("school_id") if creator else None
    
    new_quiz = {
        "id": quiz_id,
        "title": quiz.title,
        "description": quiz.description,
        "time_limit": quiz.time_limit,
        "is_public": quiz.is_public,
        "created_by": quiz.user_id,
        "created_by_teacher": teacher_id,  # For students, track their teacher
        "school_id": school_id,  # Associate with school
        "created_at": datetime.now().isoformat(),
        "total_questions": len(quiz.questions),
        "total_points": sum(q.get("points", 1) for q in quiz.questions),
        "questions": quiz.questions,
        "creation_type": "manual"
    }
    quizzes_db.append(new_quiz)
    return {"message": "Quiz created successfully", "quiz": new_quiz}

@app.post("/api/quizzes/auto-generate")
def auto_generate_quiz(request: QuizGenerationRequest):
    # Allow all users including guests to create quizzes
    if request.user_role not in ["teacher", "admin", "super_admin", "student", "guest"]:
        raise HTTPException(status_code=403, detail="Invalid user role for quiz creation")
    
    import uuid
    from datetime import datetime
    
    try:
        # Use the new AI models for quiz generation
        ai_questions = ai_quiz_generator.generate_quiz_questions(
            subject=request.subject,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            topic=request.title,  # Use title as topic
            preferred_model=DEFAULT_AI_MODEL
        )
        
        if ai_questions:
            # Convert AI questions to the expected format
            questions = []
            for i, q in enumerate(ai_questions):
                # Calculate points based on difficulty
                if request.difficulty == "easy":
                    points = 1
                elif request.difficulty == "medium":
                    points = 2
                else:  # hard
                    points = 3
                
                question = {
                    "id": f"q_{i+1}",
                    "question_text": q["question_text"],
                    "question_type": "multiple_choice",
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"],
                    "difficulty": request.difficulty,
                    "points": points
                }
                questions.append(question)
        else:
            # Fallback to enhanced generator
            questions = enhanced_generator.generate_questions(
                request.subject, 
                request.difficulty, 
                request.num_questions
            )
        
        # Create quiz
        quiz_id = str(uuid.uuid4())
        
        # Get creator information
        creator = next((u for u in users_db if u["id"] == request.user_id), None)
        teacher_id = creator.get("created_by_teacher") if creator and creator.get("role") == "student" else None
        school_id = creator.get("school_id") if creator else None
        
        new_quiz = {
            "id": quiz_id,
            "title": request.title,
            "description": request.description,
            "questions": questions,
            "time_limit": request.time_limit,
            "is_public": True,
            "created_by": request.user_id,
            "created_by_teacher": teacher_id,  # For students, track their teacher
            "school_id": school_id,  # Associate with school
            "created_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "total_points": sum(q.get("points", 1) for q in questions),
            "creation_type": "ai_generated",
            "topic": request.subject,
            "difficulty": request.difficulty
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: str):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"quiz": quiz}

@app.delete("/api/quizzes/{quiz_id}")
def delete_quiz(quiz_id: str, user_id: int, user_role: str):
    """Delete a quiz - teachers can delete their own, super admins can delete any"""
    # Find the quiz
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check permissions
    if user_role == "super_admin":
        # Super admin can delete any quiz
        pass
    elif user_role == "teacher" or user_role == "admin":
        # Teachers and admins can only delete their own quizzes
        if quiz.get("created_by") != user_id and quiz.get("user_id") != user_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only delete quizzes you created"
            )
    else:
        # Students and guests cannot delete quizzes
        raise HTTPException(
            status_code=403, 
            detail="You don't have permission to delete quizzes"
        )
    
    # Remove quiz from database
    quizzes_db[:] = [q for q in quizzes_db if q["id"] != quiz_id]
    
    # Also remove any quiz results for this quiz
    quiz_results_db[:] = [r for r in quiz_results_db if r.get("quiz_id") != quiz_id]
    
    return {
        "message": "Quiz deleted successfully",
        "deleted_quiz_id": quiz_id,
        "deleted_by": user_id,
        "deleted_by_role": user_role
    }

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: list
    user_id: int

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission_data: QuizSubmission):
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    total_score = 0
    max_score = 0
    answers = submission_data.get("answers", [])
    user_id = submission_data.get("user_id")
    
    # Track correct/incorrect answers for detailed results
    question_results = []
    
    for i, answer in enumerate(answers):
        question_id = f"q_{i+1}"  # Use question index as ID
        user_answer = answer if isinstance(answer, str) else str(answer)
        
        # Find question
        question = next((q for q in quiz["questions"] if q["id"] == question_id), None)
        if question:
            points = question.get("points", 1)
            max_score += points
            is_correct = user_answer == question.get("correct_answer")
            
            if is_correct:
                total_score += points
            
            question_results.append({
                "question_id": question_id,
                "question_text": question.get("question_text", ""),
                "user_answer": user_answer,
                "correct_answer": question.get("correct_answer", ""),
                "is_correct": is_correct,
                "points_earned": points if is_correct else 0,
                "max_points": points
            })
    
    percentage = round((total_score / max_score * 100), 2) if max_score > 0 else 0
    
    # Determine grade and pass/fail
    grade, grade_letter = calculate_grade(percentage)
    passed = percentage >= 60  # 60% passing threshold
    
    # Create detailed result
    import uuid
    result = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz_id,
        "quiz_title": quiz["title"],
        "user_id": user_id,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "grade": grade,
        "grade_letter": grade_letter,
        "passed": passed,
        "status": "PASSED" if passed else "FAILED",
        "question_results": question_results,
        "submitted_at": datetime.now().isoformat(),
        "message": f"Quiz submitted successfully! You scored {percentage}% and {'PASSED' if passed else 'FAILED'} with grade {grade_letter}"
    }
    
    # Store result in database
    quiz_results_db.append(result)
    
    # Update quiz statistics
    quiz["attempts"] = quiz.get("attempts", 0) + 1
    if "average_score" not in quiz:
        quiz["average_score"] = 0
    quiz["average_score"] = ((quiz["average_score"] * (quiz["attempts"] - 1)) + percentage) / quiz["attempts"]
    
    return {"result": result}

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 97:
        return 4.0, "A+"
    elif percentage >= 93:
        return 4.0, "A"
    elif percentage >= 90:
        return 3.7, "A-"
    elif percentage >= 87:
        return 3.3, "B+"
    elif percentage >= 83:
        return 3.0, "B"
    elif percentage >= 80:
        return 2.7, "B-"
    elif percentage >= 77:
        return 2.3, "C+"
    elif percentage >= 73:
        return 2.0, "C"
    elif percentage >= 70:
        return 1.7, "C-"
    elif percentage >= 67:
        return 1.3, "D+"
    elif percentage >= 63:
        return 1.0, "D"
    elif percentage >= 60:
        return 0.7, "D-"
    else:
        return 0.0, "F"

# Quiz Results Endpoints
@app.get("/api/quiz-results")
def get_quiz_results(user_id: int = None):
    """Get quiz results for a specific user or all results"""
    if user_id:
        user_results = [r for r in quiz_results_db if r.get("user_id") == user_id]
        return {"results": user_results, "total": len(user_results)}
    return {"results": quiz_results_db, "total": len(quiz_results_db)}

@app.get("/api/quiz-results/{result_id}")
def get_quiz_result(result_id: str):
    """Get a specific quiz result by ID"""
    result = next((r for r in quiz_results_db if r.get("id") == result_id), None)
    if not result:
        raise HTTPException(status_code=404, detail="Quiz result not found")
    return {"result": result}

@app.get("/api/users/{user_id}/quiz-stats")
def get_user_quiz_stats(user_id: int):
    """Get comprehensive quiz statistics for a user"""
    user_results = [r for r in quiz_results_db if r.get("user_id") == user_id]
    
    if not user_results:
        return {
            "user_id": user_id,
            "total_quizzes_taken": 0,
            "average_score": 0,
            "total_passed": 0,
            "total_failed": 0,
            "pass_rate": 0,
            "grade_distribution": {},
            "recent_results": []
        }
    
    total_quizzes = len(user_results)
    total_passed = sum(1 for r in user_results if r.get("passed", False))
    total_failed = total_quizzes - total_passed
    average_score = sum(r.get("percentage", 0) for r in user_results) / total_quizzes
    pass_rate = (total_passed / total_quizzes) * 100
    
    # Grade distribution
    grade_distribution = {}
    for result in user_results:
        grade = result.get("grade_letter", "F")
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    # Recent results (last 5)
    recent_results = sorted(user_results, key=lambda x: x.get("submitted_at", ""), reverse=True)[:5]
    
    return {
        "user_id": user_id,
        "total_quizzes_taken": total_quizzes,
        "average_score": round(average_score, 2),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "pass_rate": round(pass_rate, 2),
        "grade_distribution": grade_distribution,
        "recent_results": recent_results
    }

# Teacher Analytics Endpoints
@app.get("/api/analytics/overview")
def get_analytics_overview(teacher_id: int = None):
    """Get comprehensive analytics overview for teachers"""
    if not teacher_id:
        raise HTTPException(status_code=400, detail="Teacher ID required")
    
    # Get all quizzes created by this teacher
    teacher_quizzes = [q for q in quizzes_db if q.get("created_by") == teacher_id]
    
    # Get all results for these quizzes
    quiz_ids = [q["id"] for q in teacher_quizzes]
    all_results = [r for r in quiz_results_db if r.get("quiz_id") in quiz_ids]
    
    # Calculate analytics
    total_quizzes = len(teacher_quizzes)
    total_attempts = len(all_results)
    total_students = len(set(r.get("user_id") for r in all_results))
    
    if total_attempts == 0:
        return {
            "teacher_id": teacher_id,
            "total_quizzes_created": total_quizzes,
            "total_attempts": 0,
            "total_students": 0,
            "average_score": 0,
            "pass_rate": 0,
            "most_popular_quiz": None,
            "recent_activity": [],
            "grade_distribution": {},
            "subject_performance": {},
            "difficulty_analysis": {}
        }
    
    # Calculate average score and pass rate
    average_score = sum(r.get("percentage", 0) for r in all_results) / total_attempts
    passed_attempts = sum(1 for r in all_results if r.get("passed", False))
    pass_rate = (passed_attempts / total_attempts) * 100
    
    # Most popular quiz
    quiz_attempt_counts = {}
    for result in all_results:
        quiz_id = result.get("quiz_id")
        quiz_attempt_counts[quiz_id] = quiz_attempt_counts.get(quiz_id, 0) + 1
    
    most_popular_quiz_id = max(quiz_attempt_counts, key=quiz_attempt_counts.get) if quiz_attempt_counts else None
    most_popular_quiz = next((q for q in teacher_quizzes if q["id"] == most_popular_quiz_id), None)
    
    # Recent activity (last 10 results)
    recent_activity = sorted(all_results, key=lambda x: x.get("submitted_at", ""), reverse=True)[:10]
    
    # Grade distribution
    grade_distribution = {}
    for result in all_results:
        grade = result.get("grade_letter", "F")
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    # Subject performance
    subject_performance = {}
    for quiz in teacher_quizzes:
        subject = quiz.get("topic", "Unknown")
        quiz_results = [r for r in all_results if r.get("quiz_id") == quiz["id"]]
        if quiz_results:
            avg_score = sum(r.get("percentage", 0) for r in quiz_results) / len(quiz_results)
            subject_performance[subject] = {
                "average_score": round(avg_score, 2),
                "total_attempts": len(quiz_results),
                "pass_rate": round((sum(1 for r in quiz_results if r.get("passed", False)) / len(quiz_results)) * 100, 2)
            }
    
    # Difficulty analysis
    difficulty_analysis = {}
    for quiz in teacher_quizzes:
        difficulty = quiz.get("difficulty", "Unknown")
        quiz_results = [r for r in all_results if r.get("quiz_id") == quiz["id"]]
        if quiz_results:
            avg_score = sum(r.get("percentage", 0) for r in quiz_results) / len(quiz_results)
            difficulty_analysis[difficulty] = {
                "average_score": round(avg_score, 2),
                "total_attempts": len(quiz_results),
                "pass_rate": round((sum(1 for r in quiz_results if r.get("passed", False)) / len(quiz_results)) * 100, 2)
            }
    
    return {
        "teacher_id": teacher_id,
        "total_quizzes_created": total_quizzes,
        "total_attempts": total_attempts,
        "total_students": total_students,
        "average_score": round(average_score, 2),
        "pass_rate": round(pass_rate, 2),
        "most_popular_quiz": most_popular_quiz,
        "recent_activity": recent_activity,
        "grade_distribution": grade_distribution,
        "subject_performance": subject_performance,
        "difficulty_analysis": difficulty_analysis
    }

@app.get("/api/analytics/quiz/{quiz_id}")
def get_quiz_analytics(quiz_id: str):
    """Get detailed analytics for a specific quiz"""
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get all results for this quiz
    quiz_results = [r for r in quiz_results_db if r.get("quiz_id") == quiz_id]
    
    if not quiz_results:
        return {
            "quiz_id": quiz_id,
            "quiz_title": quiz["title"],
            "total_attempts": 0,
            "average_score": 0,
            "pass_rate": 0,
            "grade_distribution": {},
            "question_analysis": [],
            "student_performance": []
        }
    
    # Calculate basic stats
    total_attempts = len(quiz_results)
    average_score = sum(r.get("percentage", 0) for r in quiz_results) / total_attempts
    passed_attempts = sum(1 for r in quiz_results if r.get("passed", False))
    pass_rate = (passed_attempts / total_attempts) * 100
    
    # Grade distribution
    grade_distribution = {}
    for result in quiz_results:
        grade = result.get("grade_letter", "F")
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    # Question analysis
    question_analysis = []
    for i, question in enumerate(quiz.get("questions", [])):
        question_id = f"q_{i+1}"
        correct_count = sum(1 for result in quiz_results 
                          for q_result in result.get("question_results", [])
                          if q_result.get("question_id") == question_id and q_result.get("is_correct", False))
        
        question_analysis.append({
            "question_number": i + 1,
            "question_text": question.get("question_text", ""),
            "difficulty": question.get("difficulty", "Unknown"),
            "points": question.get("points", 1),
            "correct_attempts": correct_count,
            "total_attempts": total_attempts,
            "success_rate": round((correct_count / total_attempts) * 100, 2) if total_attempts > 0 else 0
        })
    
    # Student performance
    student_performance = []
    for result in quiz_results:
        student_performance.append({
            "user_id": result.get("user_id"),
            "score": result.get("score"),
            "max_score": result.get("max_score"),
            "percentage": result.get("percentage"),
            "grade": result.get("grade_letter"),
            "passed": result.get("passed"),
            "submitted_at": result.get("submitted_at")
        })
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": quiz["title"],
        "total_attempts": total_attempts,
        "average_score": round(average_score, 2),
        "pass_rate": round(pass_rate, 2),
        "grade_distribution": grade_distribution,
        "question_analysis": question_analysis,
        "student_performance": student_performance
    }

@app.get("/api/analytics/students")
def get_student_analytics(teacher_id: int = None):
    """Get analytics for all students who took teacher's quizzes"""
    if not teacher_id:
        raise HTTPException(status_code=400, detail="Teacher ID required")
    
    # Get all quizzes created by this teacher
    teacher_quizzes = [q for q in quizzes_db if q.get("created_by") == teacher_id]
    quiz_ids = [q["id"] for q in teacher_quizzes]
    
    # Get all results for these quizzes
    all_results = [r for r in quiz_results_db if r.get("quiz_id") in quiz_ids]
    
    # Group results by student
    student_results = {}
    for result in all_results:
        user_id = result.get("user_id")
        if user_id not in student_results:
            student_results[user_id] = []
        student_results[user_id].append(result)
    
    # Calculate student analytics
    student_analytics = []
    for user_id, results in student_results.items():
        # Get user info
        user = next((u for u in users_db if u["id"] == user_id), None)
        if not user:
            continue
            
        total_quizzes = len(results)
        average_score = sum(r.get("percentage", 0) for r in results) / total_quizzes
        passed_quizzes = sum(1 for r in results if r.get("passed", False))
        pass_rate = (passed_quizzes / total_quizzes) * 100
        
        # Recent activity
        recent_quiz = max(results, key=lambda x: x.get("submitted_at", ""))
        
        student_analytics.append({
            "user_id": user_id,
            "name": user.get("name", "Unknown"),
            "email": user.get("email", ""),
            "total_quizzes_taken": total_quizzes,
            "average_score": round(average_score, 2),
            "pass_rate": round(pass_rate, 2),
            "last_quiz": recent_quiz.get("quiz_title", ""),
            "last_quiz_date": recent_quiz.get("submitted_at", ""),
            "last_quiz_score": recent_quiz.get("percentage", 0)
        })
    
    # Sort by average score descending
    student_analytics.sort(key=lambda x: x["average_score"], reverse=True)
    
    return {
        "teacher_id": teacher_id,
        "total_students": len(student_analytics),
        "students": student_analytics
    }

# AI Model Management Endpoints
@app.get("/api/ai/status")
def get_ai_status():
    """Get the status of AI models"""
    available_models = ai_quiz_generator.get_available_models()
    return {
        "available_models": available_models,
        "default_model": DEFAULT_AI_MODEL,
        "total_models": len(available_models)
    }

@app.get("/api/ai/test/{model_name}")
def test_ai_model(model_name: str):
    """Test a specific AI model"""
    if model_name not in ['free', 'grok']:
        raise HTTPException(status_code=400, detail="Invalid model name")
    
    is_working = ai_quiz_generator.test_model(model_name)
    return {
        "model": model_name,
        "status": "working" if is_working else "not working",
        "available": model_name in ai_quiz_generator.get_available_models()
    }

# School system endpoints
@app.get("/api/schools")
def get_schools():
    """Get all schools"""
    return {
        "schools": schools_db,
        "total": len(schools_db)
    }

@app.get("/api/schools/{school_id}")
def get_school(school_id: str, user_id: Optional[int] = None):
    """Get school information"""
    school = next((s for s in schools_db if s["id"] == school_id), None)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Check if user has access to this school
    if user_id:
        user = next((u for u in users_db if u["id"] == user_id), None)
        if user and user["role"] in ["teacher", "student"] and user.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied. You can only view your own school.")
    
    # Add current statistics
    school_users = [u for u in users_db if u.get("school_id") == school_id]
    school["current_students"] = len([u for u in school_users if u.get("role") == "student"])
    school["current_teachers"] = len([u for u in school_users if u.get("role") == "teacher"])
    school["total_quizzes"] = len(school_quizzes_db.get(school_id, []))
    
    return {"school": school}

@app.get("/api/schools/{school_id}/quizzes")
def get_school_quizzes(school_id: str, user_id: Optional[int] = None):
    """Get quizzes for a specific school"""
    if school_id not in school_quizzes_db:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Check if user belongs to this school
    if user_id:
        user = next((u for u in users_db if u["id"] == user_id), None)
        if not user or user.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied: User not enrolled in this school")
    
    quizzes = school_quizzes_db[school_id]
    return {
        "quizzes": quizzes,
        "total": len(quizzes),
        "school_id": school_id
    }

@app.post("/api/schools/{school_id}/quizzes/auto-generate")
def generate_school_quiz(school_id: str, quiz_data: QuizGenerationRequest):
    """Generate quiz for specific school using AI"""
    try:
        # Check if school exists
        school = next((s for s in schools_db if s["id"] == school_id), None)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if user belongs to this school
        user = next((u for u in users_db if u["id"] == quiz_data.user_id), None)
        if not user or user.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied: User not enrolled in this school")
        
        # Check if user can create quizzes
        if user.get("role") not in ["teacher", "school_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied: Only teachers and admins can create quizzes")
        
        # Generate quiz using AI
        print(f"Generating school quiz using {DEFAULT_AI_MODEL} AI model...")
        questions = ai_quiz_generator.generate_quiz_questions(
            subject=quiz_data.subject,
            difficulty=quiz_data.difficulty,
            num_questions=quiz_data.num_questions,
            topic=getattr(quiz_data, 'topic', None)
        )
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate quiz questions")
        
        # Create quiz
        quiz_id = f"quiz_{len(quizzes_db) + 1}"
        quiz = {
            "id": quiz_id,
            "title": quiz_data.title,
            "description": quiz_data.description,
            "questions": json.dumps(questions),
            "time_limit": quiz_data.time_limit,
            "is_public": quiz_data.is_public,
            "school_id": school_id,
            "created_by": quiz_data.user_id,
            "created_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "total_points": len(questions) * 2,
            "creation_type": "ai_generated",
            "topic": quiz_data.subject,
            "difficulty": quiz_data.difficulty
        }
        
        # Add to both global and school-specific storage
        quizzes_db.append(quiz)
        school_quizzes_db[school_id].append(quiz)
        
        return {
            "message": "School quiz created successfully",
            "quiz": quiz
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schools/{school_id}/analytics")
def get_school_analytics(school_id: str):
    """Get analytics for a specific school"""
    school = next((s for s in schools_db if s["id"] == school_id), None)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Get school users
    school_users = [u for u in users_db if u.get("school_id") == school_id]
    school_quizzes = school_quizzes_db.get(school_id, [])
    
    # Get quiz results for this school
    school_results = [r for r in quiz_results_db if r.get("school_id") == school_id]
    
    analytics = {
        "school_id": school_id,
        "school_name": school["name"],
        "total_students": len([u for u in school_users if u.get("role") == "student"]),
        "total_teachers": len([u for u in school_users if u.get("role") == "teacher"]),
        "total_quizzes": len(school_quizzes),
        "total_quiz_attempts": len(school_results),
        "average_quiz_score": 0.0,
        "most_popular_subjects": [],
        "monthly_activity": {},
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # Calculate average score
    if school_results:
        total_score = sum(r.get("percentage", 0) for r in school_results)
        analytics["average_quiz_score"] = round(total_score / len(school_results), 2)
    
    return {"analytics": analytics}

@app.post("/api/ai/generate-test")
def generate_test_quiz(request: QuizGenerationRequest):
    """Generate a test quiz to verify AI functionality"""
    try:
        questions = ai_quiz_generator.generate_quiz_questions(
            subject=request.subject,
            difficulty=request.difficulty,
            num_questions=min(request.num_questions, 5),  # Limit to 5 for testing
            topic=request.title,
            preferred_model=DEFAULT_AI_MODEL
        )
        
        return {
            "success": True,
            "questions_generated": len(questions),
            "questions": questions[:3],  # Return first 3 questions as sample
            "model_used": DEFAULT_AI_MODEL
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "questions_generated": 0
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI-Powered Quiz System Backend")
    print("=" * 60)
    print("📍 Server: http://127.0.0.1:8002")
    print("📚 Features: AI Quiz Generation, User Management, Analytics")
    print("🤖 AI Models: Free AI Model, Grok AI, Hugging Face, Google Gemini")
    print("🏫 School System: Multi-tenant school management")
    print("👑 Super Admin: Protected admin access")
    print("🔐 Authentication: Regular login system")
    print("👤 Guest Mode: Create quizzes, take tests, view results without registration")
    print("🔗 API Documentation: http://127.0.0.1:8002/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 60)
    
    # Print AI model status
    print_ai_status()
    
    print("\n🔗 API Endpoints:")
    print("- POST /api/quizzes/auto-generate - Generate quizzes with AI")
    print("- GET  /api/ai/status - Check AI model status")
    print("- GET  /api/ai/test/{model} - Test specific AI model")
    print("- POST /api/ai/generate-test - Test AI quiz generation")
    print("\n🏫 School System Endpoints:")
    print("- POST /api/schools/register - Register new school")
    print("- GET  /api/schools - Get all schools")
    print("- GET  /api/schools/{school_id} - Get school info")
    print("- GET  /api/schools/{school_id}/quizzes - Get school quizzes")
    print("- POST /api/schools/{school_id}/quizzes/auto-generate - Create school quiz")
    print("- GET  /api/schools/{school_id}/analytics - Get school analytics")
    print("\n✨ Backend is ready!")
    
    uvicorn.run(app, host="127.0.0.1", port=8002)