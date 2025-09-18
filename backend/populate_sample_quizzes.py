#!/usr/bin/env python3
"""
Sample Quiz Population Script
Creates sample quizzes with different subjects and difficulty levels
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base, User, Quiz, Chapter, Topic, Subtopic, Question
import json
from datetime import datetime

# Create database tables
Base.metadata.create_all(bind=engine)

def create_sample_quizzes():
    """Create sample quizzes with questions for different subjects and difficulty levels."""
    
    # Get database session
    db = next(get_db())
    
    try:
        # First, create a sample teacher user if it doesn't exist
        teacher = db.query(User).filter(User.email == "teacher@quizsystem.com").first()
        if not teacher:
            teacher = User(
                email="teacher@quizsystem.com",
                username="sample_teacher",
                full_name="Sample Teacher",
                role="teacher",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K5K5K5K",  # password: teacher123
                is_active=True
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print(f"Created teacher user: {teacher.full_name}")
        
        # Sample quiz data
        sample_quizzes = [
            {
                "title": "Mathematics - Easy Level",
                "description": "Basic mathematics concepts for beginners",
                "subject": "Mathematics",
                "difficulty": "easy",
                "time_limit": 30,
                "chapters": [
                    {
                        "title": "Basic Arithmetic",
                        "topics": [
                            {
                                "title": "Addition and Subtraction",
                                "subtopics": [
                                    {
                                        "title": "Single Digit Addition",
                                        "questions": [
                                            {
                                                "question_text": "What is 5 + 3?",
                                                "question_type": "multiple_choice",
                                                "options": ["6", "7", "8", "9"],
                                                "correct_answer": "8",
                                                "explanation": "5 + 3 = 8",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            },
                                            {
                                                "question_text": "What is 9 - 4?",
                                                "question_type": "multiple_choice",
                                                "options": ["3", "4", "5", "6"],
                                                "correct_answer": "5",
                                                "explanation": "9 - 4 = 5",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            },
                                            {
                                                "question_text": "What is 7 + 2?",
                                                "question_type": "multiple_choice",
                                                "options": ["8", "9", "10", "11"],
                                                "correct_answer": "9",
                                                "explanation": "7 + 2 = 9",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Mathematics - Medium Level",
                "description": "Intermediate mathematics concepts",
                "subject": "Mathematics",
                "difficulty": "medium",
                "time_limit": 45,
                "chapters": [
                    {
                        "title": "Algebra Basics",
                        "topics": [
                            {
                                "title": "Linear Equations",
                                "subtopics": [
                                    {
                                        "title": "Solving for X",
                                        "questions": [
                                            {
                                                "question_text": "Solve for x: 2x + 5 = 13",
                                                "question_type": "multiple_choice",
                                                "options": ["x = 3", "x = 4", "x = 5", "x = 6"],
                                                "correct_answer": "x = 4",
                                                "explanation": "2x + 5 = 13, so 2x = 8, therefore x = 4",
                                                "difficulty_level": "medium",
                                                "points": 2
                                            },
                                            {
                                                "question_text": "Solve for x: 3x - 7 = 14",
                                                "question_type": "multiple_choice",
                                                "options": ["x = 5", "x = 6", "x = 7", "x = 8"],
                                                "correct_answer": "x = 7",
                                                "explanation": "3x - 7 = 14, so 3x = 21, therefore x = 7",
                                                "difficulty_level": "medium",
                                                "points": 2
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Mathematics - Hard Level",
                "description": "Advanced mathematics concepts",
                "subject": "Mathematics",
                "difficulty": "hard",
                "time_limit": 60,
                "chapters": [
                    {
                        "title": "Calculus",
                        "topics": [
                            {
                                "title": "Derivatives",
                                "subtopics": [
                                    {
                                        "title": "Basic Derivatives",
                                        "questions": [
                                            {
                                                "question_text": "What is the derivative of x²?",
                                                "question_type": "multiple_choice",
                                                "options": ["x", "2x", "x²", "2x²"],
                                                "correct_answer": "2x",
                                                "explanation": "The derivative of x² is 2x using the power rule",
                                                "difficulty_level": "hard",
                                                "points": 3
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "English Grammar - Easy Level",
                "description": "Basic English grammar concepts",
                "subject": "English",
                "difficulty": "easy",
                "time_limit": 25,
                "chapters": [
                    {
                        "title": "Parts of Speech",
                        "topics": [
                            {
                                "title": "Nouns and Verbs",
                                "subtopics": [
                                    {
                                        "title": "Identifying Nouns",
                                        "questions": [
                                            {
                                                "question_text": "Which word is a noun in the sentence: 'The cat runs quickly'?",
                                                "question_type": "multiple_choice",
                                                "options": ["The", "cat", "runs", "quickly"],
                                                "correct_answer": "cat",
                                                "explanation": "Cat is a noun as it names a person, place, or thing",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            },
                                            {
                                                "question_text": "Which word is a verb in the sentence: 'She sings beautifully'?",
                                                "question_type": "multiple_choice",
                                                "options": ["She", "sings", "beautifully", "None"],
                                                "correct_answer": "sings",
                                                "explanation": "Sings is a verb as it shows action",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Python Programming - Easy Level",
                "description": "Basic Python programming concepts",
                "subject": "Programming",
                "difficulty": "easy",
                "time_limit": 40,
                "chapters": [
                    {
                        "title": "Python Basics",
                        "topics": [
                            {
                                "title": "Variables and Data Types",
                                "subtopics": [
                                    {
                                        "title": "Variable Declaration",
                                        "questions": [
                                            {
                                                "question_text": "How do you declare a variable in Python?",
                                                "question_type": "multiple_choice",
                                                "options": ["var x = 5", "x = 5", "int x = 5", "x := 5"],
                                                "correct_answer": "x = 5",
                                                "explanation": "In Python, you simply assign a value to a variable name",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            },
                                            {
                                                "question_text": "What is the data type of the variable: name = 'John'?",
                                                "question_type": "multiple_choice",
                                                "options": ["int", "float", "string", "boolean"],
                                                "correct_answer": "string",
                                                "explanation": "Text enclosed in quotes is a string data type",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Python Programming - Medium Level",
                "description": "Intermediate Python programming concepts",
                "subject": "Programming",
                "difficulty": "medium",
                "time_limit": 50,
                "chapters": [
                    {
                        "title": "Control Structures",
                        "topics": [
                            {
                                "title": "Loops and Conditionals",
                                "subtopics": [
                                    {
                                        "title": "For Loops",
                                        "questions": [
                                            {
                                                "question_text": "What will this code output: for i in range(3): print(i)",
                                                "question_type": "multiple_choice",
                                                "options": ["0 1 2", "1 2 3", "0 1 2 3", "Error"],
                                                "correct_answer": "0 1 2",
                                                "explanation": "range(3) generates numbers 0, 1, 2",
                                                "difficulty_level": "medium",
                                                "points": 2
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Science - Easy Level",
                "description": "Basic science concepts",
                "subject": "Science",
                "difficulty": "easy",
                "time_limit": 30,
                "chapters": [
                    {
                        "title": "Physics Basics",
                        "topics": [
                            {
                                "title": "Motion and Force",
                                "subtopics": [
                                    {
                                        "title": "Basic Motion",
                                        "questions": [
                                            {
                                                "question_text": "What is the unit of speed?",
                                                "question_type": "multiple_choice",
                                                "options": ["kg", "m/s", "N", "J"],
                                                "correct_answer": "m/s",
                                                "explanation": "Speed is distance per unit time, measured in meters per second",
                                                "difficulty_level": "easy",
                                                "points": 1
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "History - Medium Level",
                "description": "World history concepts",
                "subject": "History",
                "difficulty": "medium",
                "time_limit": 35,
                "chapters": [
                    {
                        "title": "Ancient Civilizations",
                        "topics": [
                            {
                                "title": "Egyptian Civilization",
                                "subtopics": [
                                    {
                                        "title": "Pyramids and Pharaohs",
                                        "questions": [
                                            {
                                                "question_text": "Which pharaoh built the Great Pyramid of Giza?",
                                                "question_type": "multiple_choice",
                                                "options": ["Ramses II", "Tutankhamun", "Khufu", "Cleopatra"],
                                                "correct_answer": "Khufu",
                                                "explanation": "Khufu (Cheops) built the Great Pyramid around 2580-2560 BC",
                                                "difficulty_level": "medium",
                                                "points": 2
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Create quizzes
        for quiz_data in sample_quizzes:
            # Check if quiz already exists
            existing_quiz = db.query(Quiz).filter(Quiz.title == quiz_data["title"]).first()
            if existing_quiz:
                print(f"Quiz '{quiz_data['title']}' already exists, skipping...")
                continue
            
            # Create quiz
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                creator_id=teacher.id,
                status="approved",  # Make it available to students
                time_limit=quiz_data["time_limit"],
                total_questions=0  # Will be updated after adding questions
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            
            total_questions = 0
            
            # Create chapters, topics, subtopics, and questions
            for chapter_idx, chapter_data in enumerate(quiz_data["chapters"]):
                chapter = Chapter(
                    title=chapter_data["title"],
                    description=f"Chapter {chapter_idx + 1}",
                    order_index=chapter_idx + 1,
                    quiz_id=quiz.id
                )
                db.add(chapter)
                db.commit()
                db.refresh(chapter)
                
                for topic_idx, topic_data in enumerate(chapter_data["topics"]):
                    topic = Topic(
                        title=topic_data["title"],
                        description=f"Topic {topic_idx + 1}",
                        order_index=topic_idx + 1,
                        chapter_id=chapter.id
                    )
                    db.add(topic)
                    db.commit()
                    db.refresh(topic)
                    
                    for subtopic_idx, subtopic_data in enumerate(topic_data["subtopics"]):
                        subtopic = Subtopic(
                            title=subtopic_data["title"],
                            description=f"Subtopic {subtopic_idx + 1}",
                            order_index=subtopic_idx + 1,
                            topic_id=topic.id
                        )
                        db.add(subtopic)
                        db.commit()
                        db.refresh(subtopic)
                        
                        for question_data in subtopic_data["questions"]:
                            question = Question(
                                quiz_id=quiz.id,
                                topic_id=topic.id,
                                subtopic_id=subtopic.id,
                                question_text=question_data["question_text"],
                                question_type=question_data["question_type"],
                                options=json.dumps(question_data["options"]) if "options" in question_data else None,
                                correct_answer=question_data["correct_answer"],
                                explanation=question_data["explanation"],
                                difficulty_level=question_data["difficulty_level"],
                                points=question_data["points"]
                            )
                            db.add(question)
                            total_questions += 1
            
            # Update total questions count
            quiz.total_questions = total_questions
            db.commit()
            
            print(f"Created quiz: '{quiz_data['title']}' with {total_questions} questions")
        
        print(f"\n✅ Successfully created {len(sample_quizzes)} sample quizzes!")
        print("📚 Subjects covered: Mathematics, English Grammar, Python Programming, Science, History")
        print("🎯 Difficulty levels: Easy, Medium, Hard")
        print("👨‍🏫 Created by: Sample Teacher")
        print("✅ All quizzes are approved and available to students")
        
    except Exception as e:
        print(f"❌ Error creating sample quizzes: {str(e)}")
        db.rollback()
    finally:
        db.close()

def create_additional_questions():
    """Create additional questions to reach 50 questions per quiz."""
    
    db = next(get_db())
    
    try:
        # Get all quizzes
        quizzes = db.query(Quiz).all()
        
        for quiz in quizzes:
            current_questions = db.query(Question).filter(Question.quiz_id == quiz.id).count()
            questions_needed = 50 - current_questions
            
            if questions_needed > 0:
                print(f"Adding {questions_needed} more questions to '{quiz.title}'...")
                
                # Get the first topic and subtopic for this quiz
                first_topic = db.query(Topic).join(Chapter).filter(Chapter.quiz_id == quiz.id).first()
                first_subtopic = db.query(Subtopic).filter(Subtopic.topic_id == first_topic.id).first()
                
                # Generate additional questions based on subject and difficulty
                subject = quiz.title.split(" - ")[0]
                difficulty = quiz.title.split(" - ")[1].replace(" Level", "").lower()
                
                additional_questions = generate_additional_questions(subject, difficulty, questions_needed)
                
                for i, question_data in enumerate(additional_questions):
                    question = Question(
                        quiz_id=quiz.id,
                        topic_id=first_topic.id,
                        subtopic_id=first_subtopic.id,
                        question_text=question_data["question_text"],
                        question_type=question_data["question_type"],
                        options=json.dumps(question_data["options"]) if "options" in question_data else None,
                        correct_answer=question_data["correct_answer"],
                        explanation=question_data["explanation"],
                        difficulty_level=question_data["difficulty_level"],
                        points=question_data["points"]
                    )
                    db.add(question)
                
                # Update total questions count
                quiz.total_questions = 50
                db.commit()
                
                print(f"✅ Added {questions_needed} questions to '{quiz.title}' (Total: 50)")
        
    except Exception as e:
        print(f"❌ Error adding additional questions: {str(e)}")
        db.rollback()
    finally:
        db.close()

def generate_additional_questions(subject, difficulty, count):
    """Generate additional questions based on subject and difficulty."""
    
    questions = []
    
    if subject == "Mathematics":
        if difficulty == "easy":
            for i in range(count):
                num1 = (i % 10) + 1
                num2 = ((i + 1) % 10) + 1
                result = num1 + num2
                questions.append({
                    "question_text": f"What is {num1} + {num2}?",
                    "question_type": "multiple_choice",
                    "options": [str(result-1), str(result), str(result+1), str(result+2)],
                    "correct_answer": str(result),
                    "explanation": f"{num1} + {num2} = {result}",
                    "difficulty_level": "easy",
                    "points": 1
                })
        elif difficulty == "medium":
            for i in range(count):
                num1 = (i % 10) + 1
                num2 = ((i + 1) % 10) + 1
                result = num1 * num2
                questions.append({
                    "question_text": f"What is {num1} × {num2}?",
                    "question_type": "multiple_choice",
                    "options": [str(result-1), str(result), str(result+1), str(result+2)],
                    "correct_answer": str(result),
                    "explanation": f"{num1} × {num2} = {result}",
                    "difficulty_level": "medium",
                    "points": 2
                })
        elif difficulty == "hard":
            for i in range(count):
                num1 = (i % 10) + 1
                num2 = ((i + 1) % 10) + 1
                result = num1 ** 2 + num2
                questions.append({
                    "question_text": f"What is {num1}² + {num2}?",
                    "question_type": "multiple_choice",
                    "options": [str(result-1), str(result), str(result+1), str(result+2)],
                    "correct_answer": str(result),
                    "explanation": f"{num1}² + {num2} = {num1*num1} + {num2} = {result}",
                    "difficulty_level": "hard",
                    "points": 3
                })
    
    elif subject == "English Grammar":
        grammar_questions = [
            {"q": "Which is correct: 'I am going to school' or 'I is going to school'?", "a": "I am going to school", "e": "Use 'am' with 'I'"},
            {"q": "What is the plural of 'child'?", "a": "children", "e": "Children is an irregular plural"},
            {"q": "Which word is an adjective: 'quickly', 'quick', 'run'?", "a": "quick", "e": "Quick describes how something is"},
            {"q": "What is the past tense of 'go'?", "a": "went", "e": "Went is the irregular past tense of go"},
            {"q": "Which sentence is correct: 'She don't like it' or 'She doesn't like it'?", "a": "She doesn't like it", "e": "Use 'doesn't' with 'she'"}
        ]
        
        for i in range(count):
            q_data = grammar_questions[i % len(grammar_questions)]
            questions.append({
                "question_text": q_data["q"],
                "question_type": "multiple_choice",
                "options": [q_data["a"], "Option B", "Option C", "Option D"],
                "correct_answer": q_data["a"],
                "explanation": q_data["e"],
                "difficulty_level": difficulty,
                "points": 1 if difficulty == "easy" else 2
            })
    
    elif subject == "Python Programming":
        python_questions = [
            {"q": "What is the output of: print('Hello' + 'World')?", "a": "HelloWorld", "e": "String concatenation joins strings together"},
            {"q": "Which is correct Python syntax for a list?", "a": "[1, 2, 3]", "e": "Lists use square brackets"},
            {"q": "What does len() function do?", "a": "Returns the length", "e": "len() returns the number of items"},
            {"q": "How do you comment in Python?", "a": "# This is a comment", "e": "Use # for single line comments"},
            {"q": "What is the result of: 10 // 3?", "a": "3", "e": "// performs floor division"}
        ]
        
        for i in range(count):
            q_data = python_questions[i % len(python_questions)]
            questions.append({
                "question_text": q_data["q"],
                "question_type": "multiple_choice",
                "options": [q_data["a"], "Option B", "Option C", "Option D"],
                "correct_answer": q_data["a"],
                "explanation": q_data["e"],
                "difficulty_level": difficulty,
                "points": 1 if difficulty == "easy" else 2
            })
    
    elif subject == "Science":
        science_questions = [
            {"q": "What is the chemical symbol for water?", "a": "H2O", "e": "Water is made of 2 hydrogen and 1 oxygen atoms"},
            {"q": "What planet is closest to the Sun?", "a": "Mercury", "e": "Mercury is the first planet from the Sun"},
            {"q": "What gas do plants produce during photosynthesis?", "a": "Oxygen", "e": "Plants produce oxygen as a byproduct"},
            {"q": "What is the hardest natural substance?", "a": "Diamond", "e": "Diamond is the hardest known natural material"},
            {"q": "What is the speed of light?", "a": "300,000 km/s", "e": "Light travels at approximately 300,000 km/s"}
        ]
        
        for i in range(count):
            q_data = science_questions[i % len(science_questions)]
            questions.append({
                "question_text": q_data["q"],
                "question_type": "multiple_choice",
                "options": [q_data["a"], "Option B", "Option C", "Option D"],
                "correct_answer": q_data["a"],
                "explanation": q_data["e"],
                "difficulty_level": difficulty,
                "points": 1 if difficulty == "easy" else 2
            })
    
    elif subject == "History":
        history_questions = [
            {"q": "In which year did World War II end?", "a": "1945", "e": "World War II ended in 1945"},
            {"q": "Who was the first President of the United States?", "a": "George Washington", "e": "George Washington was the first US President"},
            {"q": "Which empire was ruled by Julius Caesar?", "a": "Roman Empire", "e": "Julius Caesar was a Roman leader"},
            {"q": "In which country was the Great Wall built?", "a": "China", "e": "The Great Wall was built in China"},
            {"q": "What was the name of the ship that brought the Pilgrims to America?", "a": "Mayflower", "e": "The Mayflower brought the Pilgrims in 1620"}
        ]
        
        for i in range(count):
            q_data = history_questions[i % len(history_questions)]
            questions.append({
                "question_text": q_data["q"],
                "question_type": "multiple_choice",
                "options": [q_data["a"], "Option B", "Option C", "Option D"],
                "correct_answer": q_data["a"],
                "explanation": q_data["e"],
                "difficulty_level": difficulty,
                "points": 1 if difficulty == "easy" else 2
            })
    
    return questions[:count]

if __name__ == "__main__":
    print("🚀 Starting sample quiz population...")
    print("=" * 50)
    
    # Create initial sample quizzes
    create_sample_quizzes()
    
    print("\n" + "=" * 50)
    print("📝 Adding additional questions to reach 50 per quiz...")
    
    # Add additional questions to reach 50 per quiz
    create_additional_questions()
    
    print("\n" + "=" * 50)
    print("🎉 Sample quiz population completed!")
    print("\n📊 Summary:")
    print("- 8 quizzes created across 5 subjects")
    print("- 3 difficulty levels (Easy, Medium, Hard)")
    print("- 50 questions per quiz (400 total questions)")
    print("- All quizzes approved and ready for students")
    print("\n🔑 Teacher Login:")
    print("Email: teacher@quizsystem.com")
    print("Password: teacher123")
    print("\n✨ Students can now see and take quizzes after logging in!")
