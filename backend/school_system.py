#!/usr/bin/env python3
"""
Multi-Tenant School System for AI-Powered Quiz System
Implements school registration, student enrollment, and isolated quiz management
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import json
import os
import time
from datetime import datetime, timedelta
from enum import Enum
import uuid

# School-related models
class SchoolType(str, Enum):
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    UNIVERSITY = "university"
    TRAINING_CENTER = "training_center"
    ONLINE_ACADEMY = "online_academy"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"      # Platform admin
    SCHOOL_ADMIN = "school_admin"    # School administrator
    TEACHER = "teacher"              # School teacher
    STUDENT = "student"              # School student
    PARENT = "parent"                # Student's parent
    GUEST = "guest"                  # Public user

class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"

# Pydantic models
class SchoolRegistration(BaseModel):
    school_name: str
    school_type: SchoolType
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str
    email: str
    website: Optional[str] = None
    principal_name: str
    established_year: int
    max_students: int = 1000
    max_teachers: int = 50
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('established_year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1800 or v > current_year:
            raise ValueError(f'Established year must be between 1800 and {current_year}')
        return v

class SchoolAdminRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    school_id: str
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()

class TeacherRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    school_id: str
    subject_specialization: List[str]
    experience_years: int
    qualification: str
    
    @validator('experience_years')
    def validate_experience(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Experience years must be between 0 and 50')
        return v

class StudentRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    school_id: str
    grade_level: str
    student_id: str
    parent_email: Optional[str] = None
    date_of_birth: str
    
    @validator('grade_level')
    def validate_grade(cls, v):
        valid_grades = [
            "kindergarten", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th",
            "freshman", "sophomore", "junior", "senior", "graduate", "postgraduate"
        ]
        if v.lower() not in valid_grades:
            raise ValueError(f'Grade level must be one of: {", ".join(valid_grades)}')
        return v.lower()

class EnrollmentRequest(BaseModel):
    student_id: str
    school_id: str
    grade_level: str
    parent_email: Optional[str] = None

class SchoolInvitation(BaseModel):
    email: str
    role: UserRole
    school_id: str
    message: Optional[str] = None

# In-memory storage (replace with database in production)
schools_db = {}
users_db = {}
enrollments_db = {}
invitations_db = {}
school_quizzes_db = {}  # school_id -> quizzes
school_analytics_db = {}

class SchoolSystem:
    """Multi-tenant school management system"""
    
    def __init__(self):
        self.schools = schools_db
        self.users = users_db
        self.enrollments = enrollments_db
        self.invitations = invitations_db
        self.school_quizzes = school_quizzes_db
        self.analytics = school_analytics_db
    
    def create_school(self, school_data: SchoolRegistration, admin_data: SchoolAdminRegistration) -> Dict[str, Any]:
        """Create a new school with admin"""
        try:
            # Generate school ID
            school_id = f"school_{uuid.uuid4().hex[:8]}"
            
            # Create school
            school = {
                "id": school_id,
                "name": school_data.school_name,
                "type": school_data.school_type,
                "address": school_data.address,
                "city": school_data.city,
                "state": school_data.state,
                "country": school_data.country,
                "postal_code": school_data.postal_code,
                "phone": school_data.phone,
                "email": school_data.email,
                "website": school_data.website,
                "principal_name": school_data.principal_name,
                "established_year": school_data.established_year,
                "max_students": school_data.max_students,
                "max_teachers": school_data.max_teachers,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "subscription_plan": "basic",  # basic, premium, enterprise
                "features": {
                    "ai_quiz_generation": True,
                    "analytics": True,
                    "custom_branding": False,
                    "api_access": False,
                    "priority_support": False
                }
            }
            
            self.schools[school_id] = school
            
            # Create school admin
            admin_id = f"admin_{uuid.uuid4().hex[:8]}"
            admin = {
                "id": admin_id,
                "name": admin_data.name,
                "email": admin_data.email,
                "password": admin_data.password,  # Should be hashed
                "phone": admin_data.phone,
                "role": UserRole.SCHOOL_ADMIN,
                "school_id": school_id,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "permissions": {
                    "manage_teachers": True,
                    "manage_students": True,
                    "view_analytics": True,
                    "manage_school_settings": True,
                    "create_quizzes": True
                }
            }
            
            self.users[admin_id] = admin
            
            # Initialize school analytics
            self.analytics[school_id] = {
                "total_students": 0,
                "total_teachers": 1,  # Admin counts as teacher
                "total_quizzes": 0,
                "total_quiz_attempts": 0,
                "average_quiz_score": 0.0,
                "most_popular_subjects": [],
                "monthly_activity": {},
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Initialize school quizzes
            self.school_quizzes[school_id] = []
            
            return {
                "school": school,
                "admin": admin,
                "message": "School created successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create school: {str(e)}")
    
    def add_teacher_to_school(self, teacher_data: TeacherRegistration, school_id: str) -> Dict[str, Any]:
        """Add teacher to school"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if school has capacity
        school = self.schools[school_id]
        current_teachers = len([u for u in self.users.values() 
                              if u.get("school_id") == school_id and u.get("role") == UserRole.TEACHER])
        
        if current_teachers >= school["max_teachers"]:
            raise HTTPException(status_code=400, detail="School has reached maximum teacher capacity")
        
        # Create teacher
        teacher_id = f"teacher_{uuid.uuid4().hex[:8]}"
        teacher = {
            "id": teacher_id,
            "name": teacher_data.name,
            "email": teacher_data.email,
            "password": teacher_data.password,  # Should be hashed
            "phone": teacher_data.phone,
            "role": UserRole.TEACHER,
            "school_id": school_id,
            "subject_specialization": teacher_data.subject_specialization,
            "experience_years": teacher_data.experience_years,
            "qualification": teacher_data.qualification,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "permissions": {
                "create_quizzes": True,
                "view_student_progress": True,
                "manage_own_quizzes": True,
                "view_analytics": True
            }
        }
        
        self.users[teacher_id] = teacher
        
        # Update school analytics
        if school_id in self.analytics:
            self.analytics[school_id]["total_teachers"] += 1
        
        return {
            "teacher": teacher,
            "message": "Teacher added to school successfully"
        }
    
    def enroll_student(self, student_data: StudentRegistration, school_id: str) -> Dict[str, Any]:
        """Enroll student in school"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if school has capacity
        school = self.schools[school_id]
        current_students = len([u for u in self.users.values() 
                              if u.get("school_id") == school_id and u.get("role") == UserRole.STUDENT])
        
        if current_students >= school["max_students"]:
            raise HTTPException(status_code=400, detail="School has reached maximum student capacity")
        
        # Create student
        student_id = f"student_{uuid.uuid4().hex[:8]}"
        student = {
            "id": student_id,
            "name": student_data.name,
            "email": student_data.email,
            "password": student_data.password,  # Should be hashed
            "phone": student_data.phone,
            "role": UserRole.STUDENT,
            "school_id": school_id,
            "grade_level": student_data.grade_level,
            "student_id": student_data.student_id,
            "parent_email": student_data.parent_email,
            "date_of_birth": student_data.date_of_birth,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "enrollment_status": EnrollmentStatus.ACTIVE,
            "permissions": {
                "take_quizzes": True,
                "view_own_progress": True,
                "view_school_quizzes": True
            }
        }
        
        self.users[student_id] = student
        
        # Create enrollment record
        enrollment_id = f"enrollment_{uuid.uuid4().hex[:8]}"
        enrollment = {
            "id": enrollment_id,
            "student_id": student_id,
            "school_id": school_id,
            "grade_level": student_data.grade_level,
            "enrollment_date": datetime.utcnow().isoformat(),
            "status": EnrollmentStatus.ACTIVE,
            "parent_email": student_data.parent_email
        }
        
        self.enrollments[enrollment_id] = enrollment
        
        # Update school analytics
        if school_id in self.analytics:
            self.analytics[school_id]["total_students"] += 1
        
        return {
            "student": student,
            "enrollment": enrollment,
            "message": "Student enrolled successfully"
        }
    
    def get_school_quizzes(self, school_id: str, user_role: str, user_id: str) -> List[Dict[str, Any]]:
        """Get quizzes for a specific school"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if user belongs to this school
        user = self.users.get(user_id)
        if not user or user.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied: User not enrolled in this school")
        
        # Get school quizzes
        school_quizzes = self.school_quizzes.get(school_id, [])
        
        # Filter based on user role
        if user_role == UserRole.STUDENT:
            # Students can only see public quizzes
            visible_quizzes = [q for q in school_quizzes if q.get("is_public", True)]
        elif user_role == UserRole.TEACHER:
            # Teachers can see all quizzes in their school
            visible_quizzes = school_quizzes
        elif user_role == UserRole.SCHOOL_ADMIN:
            # School admins can see all quizzes
            visible_quizzes = school_quizzes
        else:
            visible_quizzes = []
        
        return visible_quizzes
    
    def create_school_quiz(self, quiz_data: Dict[str, Any], school_id: str, creator_id: str) -> Dict[str, Any]:
        """Create quiz for specific school"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if creator belongs to this school
        creator = self.users.get(creator_id)
        if not creator or creator.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied: User not enrolled in this school")
        
        # Check if creator can create quizzes
        if creator.get("role") not in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN]:
            raise HTTPException(status_code=403, detail="Access denied: Only teachers and admins can create quizzes")
        
        # Create quiz
        quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
        quiz = {
            "id": quiz_id,
            "title": quiz_data["title"],
            "description": quiz_data["description"],
            "subject": quiz_data["subject"],
            "difficulty": quiz_data["difficulty"],
            "questions": quiz_data.get("questions", []),
            "time_limit": quiz_data.get("time_limit", 60),
            "is_public": quiz_data.get("is_public", True),
            "school_id": school_id,
            "created_by": creator_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_questions": quiz_data.get("num_questions", 0),
            "total_points": quiz_data.get("num_questions", 0) * 2,
            "creation_type": "ai_generated",
            "topic": quiz_data["subject"],
            "grade_level": quiz_data.get("grade_level"),
            "class_section": quiz_data.get("class_section"),
            "due_date": quiz_data.get("due_date"),
            "max_attempts": quiz_data.get("max_attempts", 3)
        }
        
        # Add to school quizzes
        if school_id not in self.school_quizzes:
            self.school_quizzes[school_id] = []
        
        self.school_quizzes[school_id].append(quiz)
        
        # Update school analytics
        if school_id in self.analytics:
            self.analytics[school_id]["total_quizzes"] += 1
        
        return {
            "quiz": quiz,
            "message": "School quiz created successfully"
        }
    
    def get_school_analytics(self, school_id: str, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific school"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Check if user has permission to view analytics
        user = self.users.get(user_id)
        if not user or user.get("school_id") != school_id:
            raise HTTPException(status_code=403, detail="Access denied: User not enrolled in this school")
        
        if user.get("role") not in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN]:
            raise HTTPException(status_code=403, detail="Access denied: Only teachers and admins can view analytics")
        
        return self.analytics.get(school_id, {})
    
    def get_school_info(self, school_id: str) -> Dict[str, Any]:
        """Get school information"""
        if school_id not in self.schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        school = self.schools[school_id].copy()
        
        # Add current statistics
        school["current_students"] = len([u for u in self.users.values() 
                                        if u.get("school_id") == school_id and u.get("role") == UserRole.STUDENT])
        school["current_teachers"] = len([u for u in self.users.values() 
                                        if u.get("school_id") == school_id and u.get("role") == UserRole.TEACHER])
        school["total_quizzes"] = len(self.school_quizzes.get(school_id, []))
        
        return school
    
    def search_schools(self, query: str, school_type: Optional[SchoolType] = None) -> List[Dict[str, Any]]:
        """Search for schools"""
        results = []
        
        for school in self.schools.values():
            if not school.get("is_active", True):
                continue
            
            # Filter by type if specified
            if school_type and school.get("type") != school_type:
                continue
            
            # Search in name, city, state
            search_text = f"{school.get('name', '')} {school.get('city', '')} {school.get('state', '')}".lower()
            if query.lower() in search_text:
                # Return limited info for search results
                results.append({
                    "id": school["id"],
                    "name": school["name"],
                    "type": school["type"],
                    "city": school["city"],
                    "state": school["state"],
                    "country": school["country"],
                    "established_year": school["established_year"],
                    "current_students": len([u for u in self.users.values() 
                                            if u.get("school_id") == school["id"] and u.get("role") == UserRole.STUDENT])
                })
        
        return results

# Global instance
school_system = SchoolSystem()

if __name__ == "__main__":
    print("🏫 Multi-Tenant School System")
    print("=" * 35)
    print("✅ School registration system ready")
    print("👨‍🏫 Teacher management ready")
    print("🎓 Student enrollment ready")
    print("📚 School-specific quizzes ready")
    print("📊 School analytics ready")
