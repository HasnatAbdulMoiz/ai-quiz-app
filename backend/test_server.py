# test_server.py - Minimal test server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test Quiz System API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Test Quiz System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Test server is running"}

@app.get("/api/quizzes")
def get_quizzes():
    return {"quizzes": [], "total": 0}

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission_data: dict):
    return {
        "message": "Quiz submitted successfully",
        "result": {
            "quiz_id": quiz_id,
            "score": 85,
            "percentage": 85.0,
            "status": "PASSED"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Test Server...")
    print("📍 Server: http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)