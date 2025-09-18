from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class QuizStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Quiz Schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit: Optional[int] = None

class QuizCreate(QuizBase):
    pass

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    status: Optional[QuizStatus] = None

class Quiz(QuizBase):
    id: int
    creator_id: int
    status: QuizStatus
    total_questions: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Chapter Schemas
class ChapterBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int
    quiz_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Topic Schemas
class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int

class TopicCreate(TopicBase):
    chapter_id: int

class Topic(TopicBase):
    id: int
    chapter_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Subtopic Schemas
class SubtopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int

class SubtopicCreate(SubtopicBase):
    topic_id: int

class Subtopic(SubtopicBase):
    id: int
    topic_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Question Schemas
class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    points: int = 1

class QuestionCreate(QuestionBase):
    quiz_id: int
    topic_id: int
    subtopic_id: Optional[int] = None

class Question(QuestionBase):
    id: int
    quiz_id: int
    topic_id: int
    subtopic_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Answer Schemas
class AnswerBase(BaseModel):
    answer_text: str
    time_taken: Optional[int] = None

class AnswerCreate(AnswerBase):
    question_id: int

class Answer(AnswerBase):
    id: int
    question_id: int
    student_id: int
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Quiz Result Schemas
class QuizResultBase(BaseModel):
    total_score: float
    max_score: float
    percentage: float
    time_taken: int
    chapter_scores: Optional[Dict[str, Any]] = None
    topic_scores: Optional[Dict[str, Any]] = None
    subtopic_scores: Optional[Dict[str, Any]] = None

class QuizResultCreate(QuizResultBase):
    quiz_id: int

class QuizResult(QuizResultBase):
    id: int
    quiz_id: int
    student_id: int
    completed_at: datetime

    class Config:
        from_attributes = True

# AI Generation Schemas
class QuizGenerationRequest(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: str = "medium"
    num_questions: int = 10
    time_limit: Optional[int] = None

class TableOfContentsResponse(BaseModel):
    chapters: List[ChapterCreate]
    topics: List[TopicCreate]
    subtopics: List[SubtopicCreate]

class QuestionGenerationResponse(BaseModel):
    questions: List[QuestionCreate]

# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class PerformanceAnalytics(BaseModel):
    overall_average: float
    chapter_analytics: Dict[str, Dict[str, Any]]
    topic_analytics: Dict[str, Dict[str, Any]]
    subtopic_analytics: Dict[str, Dict[str, Any]]
    student_rankings: List[Dict[str, Any]]
