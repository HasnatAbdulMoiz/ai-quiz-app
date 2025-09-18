# PowerShell script to set Gemini API key environment variable
# Run this script to set your Gemini API key for the current session

Write-Host "🔧 Setting up Gemini API Key..." -ForegroundColor Green

# Set the environment variable
$env:GEMINI_API_KEY = "AIzaSyDom09ZeJmXM-nbKs1z05YKMDqNSU4gbyk"

Write-Host "✅ Gemini API Key set successfully!" -ForegroundColor Green
Write-Host "🔑 API Key: $($env:GEMINI_API_KEY.Substring(0,10))..." -ForegroundColor Yellow

# Test the connection
Write-Host "`n🧪 Testing Gemini connection..." -ForegroundColor Blue
try {
    python test_gemini_quiz.py
    Write-Host "`n🎉 Gemini AI is ready to use!" -ForegroundColor Green
} catch {
    Write-Host "❌ Test failed. Please check your internet connection." -ForegroundColor Red
}

Write-Host "`n💡 To make this permanent, add this line to your .env file:" -ForegroundColor Cyan
Write-Host "GEMINI_API_KEY=AIzaSyDom09ZeJmXM-nbKs1z05YKMDqNSU4gbyk" -ForegroundColor White
