"""
Test script for the AI Quiz API
"""
import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing AI Quiz API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: AI Quiz Generation
    print("\n3. Testing AI Quiz Generation...")
    try:
        data = {
            "title": "Python Basics Quiz",
            "description": "Test your Python knowledge",
            "subject": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3,
            "time_limit": 30
        }
        
        response = requests.post(
            f"{base_url}/api/quizzes/auto-generate",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['message']}")
            print(f"Quiz ID: {result['quiz']['id']}")
            print(f"Questions: {result['quiz']['total_questions']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get quizzes
    print("\n4. Testing get quizzes...")
    try:
        response = requests.get(f"{base_url}/api/quizzes")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Quizzes count: {len(result['quizzes'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
