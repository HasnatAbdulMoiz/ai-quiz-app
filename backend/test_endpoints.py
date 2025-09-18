# test_endpoints.py - Test the new endpoints
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test data
users_db = [
    {"id": 1, "name": "Super Admin", "email": "admin@example.com", "role": "super_admin", "password": "hashed_password"},
    {"id": 2, "name": "Test User", "email": "user@example.com", "role": "student", "password": "hashed_password"}
]

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Test server is working!"}

@app.post("/api/register")
def register_user(user_data: dict):
    """Register a new user"""
    return {"message": "User registered successfully", "user": {"id": 3, "name": user_data.get("name", "Test User")}}

@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin_id: int):
    """Get admin dashboard data"""
    return {
        "total_users": len(users_db),
        "total_quizzes": 5,
        "total_results": 10,
        "recent_users": users_db,
        "recent_quizzes": [],
        "admin_info": {"id": admin_id, "name": "Test Admin", "email": "admin@test.com", "role": "super_admin"}
    }

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, admin_id: int):
    """Delete a user (admin only)"""
    return {"message": f"User {user_id} deleted successfully"}

@app.get("/api/super-admin/all-credentials")
def get_all_credentials(admin_id: int):
    """Get all user credentials (super admin only)"""
    return {"users": users_db}

if __name__ == "__main__":
    print("🚀 Starting Test Endpoints Server")
    print("📍 Server: http://127.0.0.1:8007")
    uvicorn.run(app, host="127.0.0.1", port=8007)
