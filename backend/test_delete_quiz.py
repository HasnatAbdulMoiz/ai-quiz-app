#!/usr/bin/env python3
"""
Test script for quiz deletion functionality
"""

import requests
import json

def test_delete_quiz():
    """Test quiz deletion with different user roles"""
    print("🧪 Testing Quiz Deletion Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8006"
    
    # Test data
    test_cases = [
        {
            "name": "Super Admin Delete Any Quiz",
            "user_id": 1,
            "user_role": "super_admin",
            "quiz_id": "sample_quiz_1",
            "expected": "success"
        },
        {
            "name": "Teacher Delete Own Quiz",
            "user_id": 2,
            "user_role": "teacher", 
            "quiz_id": "sample_quiz_2",
            "expected": "success"
        },
        {
            "name": "Teacher Delete Other's Quiz",
            "user_id": 2,
            "user_role": "teacher",
            "quiz_id": "sample_quiz_1", 
            "expected": "forbidden"
        },
        {
            "name": "Student Delete Quiz",
            "user_id": 3,
            "user_role": "student",
            "quiz_id": "sample_quiz_1",
            "expected": "forbidden"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}")
        print("-" * 30)
        
        try:
            # First, check if quiz exists
            quiz_response = requests.get(f"{base_url}/api/quizzes/{test_case['quiz_id']}")
            if quiz_response.status_code != 200:
                print(f"❌ Quiz {test_case['quiz_id']} not found, skipping test")
                continue
            
            quiz_data = quiz_response.json()
            print(f"📋 Quiz: {quiz_data['quiz']['title']}")
            print(f"👤 Created by: {quiz_data['quiz'].get('created_by', 'Unknown')}")
            
            # Attempt to delete quiz
            delete_url = f"{base_url}/api/quizzes/{test_case['quiz_id']}"
            params = {
                "user_id": test_case["user_id"],
                "user_role": test_case["user_role"]
            }
            
            response = requests.delete(delete_url, params=params)
            
            print(f"🔍 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('message', 'Quiz deleted')}")
                print(f"🗑️ Deleted by: {result.get('deleted_by')} ({result.get('deleted_by_role')})")
                
                # Verify quiz is actually deleted
                verify_response = requests.get(f"{base_url}/api/quizzes/{test_case['quiz_id']}")
                if verify_response.status_code == 404:
                    print("✅ Quiz successfully removed from database")
                else:
                    print("⚠️ Quiz still exists in database")
                    
            elif response.status_code == 403:
                result = response.json()
                print(f"🚫 Forbidden: {result.get('detail', 'Access denied')}")
                
            elif response.status_code == 404:
                print("❌ Quiz not found")
                
            else:
                print(f"❌ Unexpected response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🎯 Test completed!")

def test_quiz_list():
    """Test getting quiz list to see current quizzes"""
    print("\n📋 Current Quiz List")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8006/api/quizzes")
        if response.status_code == 200:
            data = response.json()
            quizzes = data.get('quizzes', [])
            print(f"📊 Total quizzes: {len(quizzes)}")
            
            for i, quiz in enumerate(quizzes[:5], 1):  # Show first 5
                print(f"{i}. {quiz['title']} (ID: {quiz['id']})")
                print(f"   Created by: {quiz.get('created_by', 'Unknown')}")
                print(f"   Questions: {quiz.get('total_questions', 0)}")
        else:
            print(f"❌ Failed to fetch quizzes: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # First show current quizzes
    test_quiz_list()
    
    # Then test deletion
    test_delete_quiz()
    
    # Show final quiz list
    print("\n" + "="*50)
    test_quiz_list()
