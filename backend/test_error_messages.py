"""
Test script to demonstrate the new error messages.
Run this to see how the custom error messages look.
"""

import requests
import json

# Test the new error messages
def test_error_messages():
    base_url = "http://localhost:8000"
    
    print("Testing Custom Error Messages")
    print("=" * 50)
    
    # Test 1: Non-existent quiz
    print("\n1. Testing non-existent quiz (should show custom error):")
    try:
        response = requests.get(f"{base_url}/quizzes/99999")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python main.py")
        return
    
    # Test 2: Non-existent notification
    print("\n2. Testing non-existent notification:")
    try:
        response = requests.get(f"{base_url}/notifications/99999")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python main.py")
        return
    
    # Test 3: Non-existent endpoint
    print("\n3. Testing non-existent endpoint:")
    try:
        response = requests.get(f"{base_url}/nonexistent-endpoint")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python main.py")
        return

if __name__ == "__main__":
    test_error_messages()
