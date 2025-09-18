"""
Custom error handlers and exception classes for the AI Quiz System.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with enhanced error details."""
    
    def __init__(
        self, 
        status_code: int, 
        error_type: str,
        message: str, 
        suggestion: str = None,
        details: Dict[str, Any] = None
    ):
        self.error_type = error_type
        self.suggestion = suggestion
        self.details = details or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_type,
                "message": message,
                "suggestion": suggestion,
                "status_code": status_code,
                **self.details
            }
        )


def create_quiz_not_found_error(quiz_id: int) -> CustomHTTPException:
    """Create a custom quiz not found error."""
    return CustomHTTPException(
        status_code=404,
        error_type="Quiz Not Found",
        message=f"Quiz with ID {quiz_id} could not be found.",
        suggestion="Please check the quiz ID and try again, or contact your teacher if you believe this is an error.",
        details={"quiz_id": quiz_id, "resource_type": "quiz"}
    )


def create_user_not_found_error(user_id: int) -> CustomHTTPException:
    """Create a custom user not found error."""
    return CustomHTTPException(
        status_code=404,
        error_type="User Not Found",
        message=f"User with ID {user_id} could not be found.",
        suggestion="Please check the user ID and try again.",
        details={"user_id": user_id, "resource_type": "user"}
    )


def create_notification_not_found_error(notification_id: int) -> CustomHTTPException:
    """Create a custom notification not found error."""
    return CustomHTTPException(
        status_code=404,
        error_type="Notification Not Found",
        message=f"Notification with ID {notification_id} could not be found.",
        suggestion="The notification may have been deleted or you may not have permission to view it.",
        details={"notification_id": notification_id, "resource_type": "notification"}
    )


def create_question_not_found_error(question_id: int) -> CustomHTTPException:
    """Create a custom question not found error."""
    return CustomHTTPException(
        status_code=404,
        error_type="Question Not Found",
        message=f"Question with ID {question_id} could not be found.",
        suggestion="Please check the question ID and try again.",
        details={"question_id": question_id, "resource_type": "question"}
    )


# Global exception handlers
async def custom_404_handler(request: Request, exc: HTTPException):
    """Custom 404 error handler with user-friendly messages."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource Not Found",
            "message": "The requested resource could not be found. Please check the URL and try again.",
            "status_code": 404,
            "path": str(request.url),
            "suggestion": "Verify the URL is correct or contact support if you believe this is an error."
        }
    )


async def custom_500_handler(request: Request, exc: Exception):
    """Custom 500 error handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong on our end. Please try again later.",
            "status_code": 500,
            "suggestion": "If the problem persists, please contact support with the error details."
        }
    )


async def custom_validation_handler(request: Request, exc: Exception):
    """Custom validation error handler."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The provided data is invalid. Please check your input and try again.",
            "status_code": 422,
            "suggestion": "Review the error details below and correct the invalid fields."
        }
    )
