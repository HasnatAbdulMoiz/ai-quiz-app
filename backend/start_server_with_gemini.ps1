# PowerShell script to start the backend server with Gemini API key
# This ensures the Gemini API key is properly set for the server

Write-Host "🚀 Starting Backend Server with Gemini AI..." -ForegroundColor Green

# Set environment variables
$env:GEMINI_API_KEY = "AIzaSyDom09ZeJmXM-nbKs1z05YKMDqNSU4gbyk"
$env:DEFAULT_AI_MODEL = "gemini"

Write-Host "✅ Environment variables set:" -ForegroundColor Yellow
Write-Host "   GEMINI_API_KEY: $($env:GEMINI_API_KEY.Substring(0,10))..." -ForegroundColor Cyan
Write-Host "   DEFAULT_AI_MODEL: $env:DEFAULT_AI_MODEL" -ForegroundColor Cyan

Write-Host "`n🌐 Starting backend server on port 8006..." -ForegroundColor Blue
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Gray

# Start the server
python complete_backend.py
