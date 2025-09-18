#!/usr/bin/env python3
"""
Test script to verify Vercel deployment works correctly
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_endpoints():
    """Test the main API endpoints"""
    
    # Get the base URL from environment or use localhost for testing
    base_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
    if not base_url.startswith('http'):
        base_url = f'https://{base_url}'
    
    print(f"Testing API at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/api/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test quizzes endpoint
    try:
        response = requests.get(f"{base_url}/api/quizzes")
        if response.status_code == 200:
            print("✅ Quizzes endpoint passed")
            data = response.json()
            print(f"   Found {data.get('total', 0)} quizzes")
        else:
            print(f"❌ Quizzes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quizzes endpoint error: {e}")
    
    # Test login with super admin
    try:
        login_data = {
            "email": os.getenv('SUPER_ADMIN_EMAIL', 'hasanatk007@gmail.com'),
            "password": os.getenv('SUPER_ADMIN_PASSWORD', 'Reshun@786')
        }
        response = requests.post(f"{base_url}/api/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login endpoint passed")
            data = response.json()
            print(f"   User: {data.get('user', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")
    
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_api_endpoints()
