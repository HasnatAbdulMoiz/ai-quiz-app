# Vercel Deployment Guide for AI Quiz Agent

This guide will help you deploy your AI Quiz Agent project to Vercel.

## Prerequisites

1. A Vercel account (free at vercel.com)
2. Your Gemini API key from Google AI Studio
3. Git repository (GitHub, GitLab, or Bitbucket)

## Environment Variables

Set these environment variables in your Vercel dashboard:

1. Go to your project in Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add the following variables:

```
GEMINI_API_KEY=your-actual-gemini-api-key
SUPER_ADMIN_EMAIL=hasanatk007@gmail.com
SUPER_ADMIN_PASSWORD=Reshun@786
```

## Deployment Steps

### Method 1: Deploy from Git Repository

1. **Push your code to a Git repository** (GitHub, GitLab, or Bitbucket)

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository
   - Vercel will automatically detect it's a Python/React project

3. **Configure Build Settings:**
   - Root Directory: Leave as is (should be the project root)
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/build`

4. **Set Environment Variables:**
   - Add the environment variables listed above

5. **Deploy:**
   - Click "Deploy"
   - Wait for the build to complete

### Method 2: Deploy using Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Navigate to your project directory:**
   ```bash
   cd project/Class
   ```

4. **Deploy:**
   ```bash
   vercel
   ```

5. **Set environment variables:**
   ```bash
   vercel env add GEMINI_API_KEY
   vercel env add SUPER_ADMIN_EMAIL
   vercel env add SUPER_ADMIN_PASSWORD
   ```

6. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

## Project Structure

```
project/Class/
├── api/                    # Vercel serverless functions
│   ├── index.py           # Main API handler
│   ├── complete_backend.py # Backend logic
│   └── ai_models.py       # AI integration
├── frontend/              # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── env.vercel.example   # Environment variables template
```

## Features Included

✅ **Complete Quiz System:**
- User authentication (login/register)
- Quiz creation (manual and AI-generated)
- Quiz taking and submission
- Results and analytics
- Admin dashboard
- School management system

✅ **AI Integration:**
- Google Gemini AI for quiz generation
- Multiple difficulty levels
- Subject-specific questions

✅ **Responsive Design:**
- Mobile-friendly interface
- Modern UI components
- Real-time updates

## API Endpoints

The following API endpoints are available:

- `GET /` - Health check
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `GET /api/quizzes` - Get all quizzes
- `GET /api/quizzes/{id}` - Get specific quiz
- `POST /api/quizzes/{id}/submit` - Submit quiz
- `POST /api/quizzes` - Create manual quiz
- `POST /api/quizzes/auto-generate` - Generate AI quiz
- `GET /api/quiz-results` - Get quiz results
- `GET /api/analytics/*` - Analytics endpoints
- `GET /api/admin/*` - Admin endpoints
- `GET /api/schools/*` - School management

## Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check that all dependencies are in requirements.txt
   - Ensure Python version is compatible (3.8+)

2. **API Not Working:**
   - Verify environment variables are set correctly
   - Check Vercel function logs in the dashboard

3. **Frontend Not Loading:**
   - Ensure build command is correct
   - Check that output directory is set to `frontend/build`

4. **AI Generation Fails:**
   - Verify GEMINI_API_KEY is set correctly
   - Check API key has proper permissions

### Getting Help:

- Check Vercel logs in the dashboard
- Review the function logs for errors
- Ensure all environment variables are set

## Post-Deployment

After successful deployment:

1. **Test the application:**
   - Visit your Vercel URL
   - Test user registration and login
   - Create and take a quiz
   - Test AI quiz generation

2. **Monitor performance:**
   - Check Vercel analytics
   - Monitor function execution times
   - Review error logs

3. **Custom domain (optional):**
   - Add a custom domain in Vercel settings
   - Update DNS records as instructed

## Security Notes

- Environment variables are encrypted in Vercel
- API keys are not exposed to the frontend
- All API calls go through Vercel's secure infrastructure
- CORS is properly configured for production

Your AI Quiz Agent is now live on Vercel! 🚀
