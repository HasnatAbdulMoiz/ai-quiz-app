"""
Quick test for the complete quiz backend
"""
import requests
import json

def test_quiz_generation():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Complete AI Quiz System")
    print("=" * 50)
    
    # Test AI Quiz Generation
    print("\n🤖 Testing AI Quiz Generation...")
    try:
        data = {
            "title": "Python Programming Quiz",
            "description": "Test your Python knowledge",
            "topic": "Python Programming",
            "difficulty": "medium",
            "total_questions": 3,
            "time_limit": 30,
            "is_public": True,
            "user_id": 1
        }
        
        response = requests.post(
            f"{base_url}/api/quizzes/auto-generate",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Quiz ID: {result['quiz']['id']}")
            print(f"Title: {result['quiz']['title']}")
            print(f"Questions: {result['quiz']['total_questions']}")
            print(f"Points: {result['quiz']['total_points']}")
            print(f"Topic: {result['quiz']['topic']}")
            print(f"Difficulty: {result['quiz']['difficulty']}")
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test Get Quizzes
    print("\n📚 Testing Get Quizzes...")
    try:
        response = requests.get(f"{base_url}/api/quizzes")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['total']} quizzes")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_quiz_generation()
