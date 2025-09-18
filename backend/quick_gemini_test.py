#!/usr/bin/env python3
"""
Quick Gemini test to verify API key is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_quick():
    """Quick test of Gemini API"""
    print("🧪 Quick Gemini Test")
    print("=" * 30)
    
    # Set API key
    api_key = "AIzaSyDom09ZeJmXM-nbKs1z05YKMDqNSU4gbyk"
    os.environ['GEMINI_API_KEY'] = api_key
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test
        response = model.generate_content("Generate 1 simple math question with 4 multiple choice options in JSON format.")
        
        if response and response.text:
            print("✅ Gemini API is working!")
            print(f"📝 Response: {response.text[:200]}...")
            return True
        else:
            print("❌ Empty response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_quick()
