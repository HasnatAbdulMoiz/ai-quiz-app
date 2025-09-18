#!/usr/bin/env python3
"""
Sample Quiz Population Script for In-Memory Backend
Creates sample quizzes with different subjects and difficulty levels
"""

import requests
import json
import time

# Backend URL
BASE_URL = "http://127.0.0.1:8002"

def create_sample_quizzes():
    """Create sample quizzes by calling the backend API."""
    
    print("🚀 Starting sample quiz population for in-memory backend...")
    print("=" * 60)
    
    # Sample quiz data
    sample_quizzes = [
        {
            "title": "Mathematics - Easy Level",
            "description": "Basic mathematics concepts for beginners",
            "subject": "mathematics",
            "difficulty": "easy",
            "num_questions": 50,
            "time_limit": 30,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Mathematics - Medium Level", 
            "description": "Intermediate mathematics concepts",
            "subject": "mathematics",
            "difficulty": "medium",
            "num_questions": 50,
            "time_limit": 45,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Mathematics - Hard Level",
            "description": "Advanced mathematics concepts",
            "subject": "mathematics",
            "difficulty": "hard", 
            "num_questions": 50,
            "time_limit": 60,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "English Grammar - Easy Level",
            "description": "Basic English grammar concepts",
            "subject": "english",
            "difficulty": "easy",
            "num_questions": 50,
            "time_limit": 25,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "English Grammar - Medium Level",
            "description": "Intermediate English grammar concepts", 
            "subject": "english",
            "difficulty": "medium",
            "num_questions": 50,
            "time_limit": 35,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Python Programming - Easy Level",
            "description": "Basic Python programming concepts",
            "subject": "python",
            "difficulty": "easy",
            "num_questions": 50,
            "time_limit": 40,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Python Programming - Medium Level",
            "description": "Intermediate Python programming concepts",
            "subject": "python",
            "difficulty": "medium",
            "num_questions": 50,
            "time_limit": 50,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Python Programming - Hard Level",
            "description": "Advanced Python programming concepts",
            "subject": "python",
            "difficulty": "hard",
            "num_questions": 50,
            "time_limit": 60,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Science - Easy Level",
            "description": "Basic science concepts",
            "subject": "science",
            "difficulty": "easy",
            "num_questions": 50,
            "time_limit": 30,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "Science - Medium Level",
            "description": "Intermediate science concepts",
            "subject": "science",
            "difficulty": "medium",
            "num_questions": 50,
            "time_limit": 40,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "History - Easy Level",
            "description": "Basic world history concepts",
            "subject": "history",
            "difficulty": "easy",
            "num_questions": 50,
            "time_limit": 30,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        },
        {
            "title": "History - Medium Level",
            "description": "Intermediate world history concepts",
            "subject": "history",
            "difficulty": "medium",
            "num_questions": 50,
            "time_limit": 35,
            "is_public": True,
            "user_id": 2,
            "user_role": "teacher"
        }
    ]
    
    created_quizzes = 0
    
    for quiz_data in sample_quizzes:
        try:
            print(f"Creating quiz: {quiz_data['title']}...")
            
            # Call the auto-generate endpoint
            response = requests.post(
                f"{BASE_URL}/api/quizzes/auto-generate",
                json=quiz_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created: {quiz_data['title']} (ID: {result.get('quiz', {}).get('id', 'N/A')})")
                created_quizzes += 1
            else:
                print(f"❌ Failed to create {quiz_data['title']}: {response.text}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend at {BASE_URL}")
            print("Please make sure the backend is running on port 8002")
            break
        except Exception as e:
            print(f"❌ Error creating {quiz_data['title']}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Sample quiz population completed!")
    print(f"📊 Created {created_quizzes} out of {len(sample_quizzes)} quizzes")
    
    if created_quizzes > 0:
        print("\n📚 Subjects covered:")
        print("- Mathematics (Easy, Medium, Hard)")
        print("- English Grammar (Easy, Medium)")
        print("- Python Programming (Easy, Medium, Hard)")
        print("- Science (Easy, Medium)")
        print("- History (Easy, Medium)")
        print("\n🎯 Each quiz contains 50 questions")
        print("✅ All quizzes are public and available to students")
        print("\n🔑 Test with any student account after logging in!")

def check_backend_status():
    """Check if the backend is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running at {BASE_URL}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print("Please make sure the backend is running on port 8002")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking backend status...")
    
    if check_backend_status():
        print("\n🚀 Starting quiz population...")
        create_sample_quizzes()
    else:
        print("\n💡 To start the backend:")
        print("1. Navigate to the backend directory")
        print("2. Run: python complete_quiz_backend.py")
        print("3. Make sure it's running on port 8002")
        print("4. Then run this script again")
