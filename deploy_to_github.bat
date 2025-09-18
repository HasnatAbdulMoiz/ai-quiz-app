@echo off
echo ========================================
echo AI Quiz Agent - GitHub Deployment
echo ========================================

echo.
echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: AI Quiz Agent ready for Vercel deployment"

echo.
echo Step 4: Adding GitHub remote...
git remote add origin https://github.com/HasnatAbdulMoiz/ai-quiz-app.git

echo.
echo Step 5: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Deployment to GitHub completed!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://vercel.com
echo 2. Click "New Project"
echo 3. Import your repository: HasnatAbdulMoiz/ai-quiz-app
echo 4. Set environment variables
echo 5. Deploy!
echo.
pause
