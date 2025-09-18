#!/usr/bin/env python3
"""
Script to generate 15 quiz questions using the AI Quiz Generator
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.quiz_generator import QuizGenerator

def main():
    """Generate 15 quiz questions and display them."""
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found in environment variables.")
        print("Please set your DeepSeek API key in the .env file.")
        return
    
    # Initialize the quiz generator
    generator = QuizGenerator()
    
    # Quiz parameters
    quiz_params = {
        "title": "General Knowledge Quiz",
        "description": "A comprehensive quiz covering various topics including science, history, geography, and literature",
        "subject": "General Knowledge",
        "difficulty": "medium",
        "num_questions": 15,
        "time_limit": 30  # 30 minutes for 15 questions
    }
    
    print("🎯 Generating 15 quiz questions...")
    print(f"Subject: {quiz_params['subject']}")
    print(f"Difficulty: {quiz_params['difficulty']}")
    print(f"Time Limit: {quiz_params['time_limit']} minutes")
    print("-" * 50)
    
    try:
        # Generate the quiz content
        result = generator.generate_quiz(**quiz_params)
        
        if result["status"] == "generated":
            print("✅ Quiz generated successfully!")
            print(f"Quality Score: {result['validation']['quality_score']}")
            print()
            
            # Display chapters
            if result["chapters"]:
                print("📚 Chapters:")
                for i, chapter in enumerate(result["chapters"], 1):
                    print(f"  {i}. {chapter['title']}")
                print()
            
            # Display topics
            if result["topics"]:
                print("📖 Topics:")
                for i, topic in enumerate(result["topics"], 1):
                    print(f"  {i}. {topic['title']}")
                print()
            
            # Display questions
            if result["questions"]:
                print("❓ Questions:")
                print("=" * 60)
                
                for i, question in enumerate(result["questions"], 1):
                    print(f"\nQuestion {i}:")
                    print(f"Text: {question['question_text']}")
                    print(f"Type: {question['question_type']}")
                    print(f"Difficulty: {question['difficulty_level']}")
                    print(f"Points: {question['points']}")
                    
                    if question.get('options'):
                        print("Options:")
                        for j, option in enumerate(question['options'], 1):
                            print(f"  {chr(64+j)}. {option}")
                    
                    print(f"Correct Answer: {question['correct_answer']}")
                    print(f"Explanation: {question['explanation']}")
                    print("-" * 40)
                
                print(f"\n📊 Summary:")
                print(f"Total Questions: {len(result['questions'])}")
                print(f"Total Points: {sum(q.get('points', 1) for q in result['questions'])}")
                
                # Save to file
                output_file = "generated_15_questions.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Quiz data saved to: {output_file}")
                
            else:
                print("❌ No questions were generated.")
                
        else:
            print("❌ Quiz generation failed!")
            print(f"Error: {result.get('validation', {}).get('issues', ['Unknown error'])}")
            
    except Exception as e:
        print(f"❌ Error generating quiz: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
