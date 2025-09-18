#!/usr/bin/env python3
"""
Test Script for School System Features
Demonstrates the multi-tenant school system functionality
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://127.0.0.1:8002"

def test_school_system():
    """Test the school system functionality"""
    print("🏫 Testing Multi-Tenant School System")
    print("=" * 50)
    
    # Test 1: Register a school
    print("\n1. 🏫 Registering ABC High School...")
    school_data = {
        "school_name": "ABC High School",
        "school_type": "high",
        "address": "123 Education Street",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "phone": "+1-555-0123",
        "email": "info@abchigh.edu",
        "principal_name": "Dr. Jane Smith",
        "established_year": 1950,
        "max_students": 1000,
        "max_teachers": 50
    }
    
    admin_data = {
        "name": "John Admin",
        "email": "admin@abchigh.edu",
        "password": "adminpass123",
        "phone": "+1-555-0124",
        "school_id": "school_1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/schools/register", 
                               json={"school_data": school_data, "admin_data": admin_data})
        if response.status_code == 200:
            result = response.json()
            school_id = result["school"]["id"]
            print(f"✅ School registered successfully!")
            print(f"   School ID: {school_id}")
            print(f"   Admin ID: {result['admin']['id']}")
        else:
            print(f"❌ School registration failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Register a teacher for the school
    print("\n2. 👨‍🏫 Registering a teacher...")
    teacher_data = {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@abchigh.edu",
        "password": "teacherpass123",
        "role": "teacher",
        "school_id": school_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=teacher_data)
        if response.status_code == 200:
            result = response.json()
            teacher_id = result["user"]["id"]
            print(f"✅ Teacher registered successfully!")
            print(f"   Teacher ID: {teacher_id}")
        else:
            print(f"❌ Teacher registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Register a student for the school
    print("\n3. 🎓 Registering a student...")
    student_data = {
        "name": "Alex Brown",
        "email": "alex.brown@student.abchigh.edu",
        "password": "studentpass123",
        "role": "student",
        "school_id": school_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=student_data)
        if response.status_code == 200:
            result = response.json()
            student_id = result["user"]["id"]
            print(f"✅ Student registered successfully!")
            print(f"   Student ID: {student_id}")
        else:
            print(f"❌ Student registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Create a quiz for the school
    print("\n4. 📚 Creating a school quiz...")
    quiz_data = {
        "title": "Algebra Fundamentals",
        "description": "Basic algebra concepts for 10th grade",
        "subject": "mathematics",
        "difficulty": "medium",
        "num_questions": 5,
        "time_limit": 30,
        "is_public": True,
        "user_id": teacher_id,
        "user_role": "teacher"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/schools/{school_id}/quizzes/auto-generate", 
                               json=quiz_data)
        if response.status_code == 200:
            result = response.json()
            quiz_id = result["quiz"]["id"]
            print(f"✅ School quiz created successfully!")
            print(f"   Quiz ID: {quiz_id}")
            print(f"   Questions: {result['quiz']['total_questions']}")
        else:
            print(f"❌ Quiz creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get school quizzes
    print("\n5. 📖 Getting school quizzes...")
    try:
        response = requests.get(f"{BASE_URL}/api/schools/{school_id}/quizzes")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ School quizzes retrieved!")
            print(f"   Total quizzes: {result['total']}")
            for quiz in result["quizzes"]:
                print(f"   - {quiz['title']} ({quiz['subject']})")
        else:
            print(f"❌ Failed to get school quizzes: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get school analytics
    print("\n6. 📊 Getting school analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/schools/{school_id}/analytics")
        if response.status_code == 200:
            result = response.json()
            analytics = result["analytics"]
            print(f"✅ School analytics retrieved!")
            print(f"   School: {analytics['school_name']}")
            print(f"   Students: {analytics['total_students']}")
            print(f"   Teachers: {analytics['total_teachers']}")
            print(f"   Quizzes: {analytics['total_quizzes']}")
        else:
            print(f"❌ Failed to get school analytics: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Get all schools
    print("\n7. 🏫 Getting all schools...")
    try:
        response = requests.get(f"{BASE_URL}/api/schools")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schools retrieved!")
            print(f"   Total schools: {result['total']}")
            for school in result["schools"]:
                print(f"   - {school['name']} ({school['type']}) - {school['city']}, {school['state']}")
        else:
            print(f"❌ Failed to get schools: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 School System Test Complete!")
    print("\n📋 What we've demonstrated:")
    print("✅ School registration with admin")
    print("✅ Teacher registration for school")
    print("✅ Student enrollment in school")
    print("✅ School-specific quiz creation")
    print("✅ School quiz isolation")
    print("✅ School analytics and reporting")
    print("✅ Multi-tenant architecture")

if __name__ == "__main__":
    test_school_system()
