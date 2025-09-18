# AI-Powered Quiz System Agent

A comprehensive web application for generating, administering, and analyzing quizzes using AI agents. Built with React, FastAPI, and PostgreSQL.

## Project Structure

```
quiz-system-agent/
├── frontend/                 # React + Tailwind CSS
├── backend/                  # FastAPI + PostgreSQL
├── ai-agent/                 # LangChain/LangGraph AI implementation
├── docker-compose.yml        # Development environment
├── requirements.txt          # Python dependencies
└── README.md
```

## Features

- **User Management**: Admin/Teacher and Student authentication
- **AI Content Generation**: Automated quiz creation with ToC and questions
- **Quiz Administration**: Time management and randomization
- **Advanced Analytics**: Granular performance insights by chapters/topics
- **Notifications**: Email/SMS alerts for quiz events
- **Cloud Ready**: Deployable on AWS/GCP/Azure

## Quick Start

1. Clone the repository
2. Run `docker-compose up` for development
3. Access frontend at `http://localhost:3000`
4. Access backend API at `http://localhost:8000`

## Technologies

- **Frontend**: React, Tailwind CSS, TypeScript
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **AI**: LangChain, LangGraph, DeepSeek LLM
- **Deployment**: Docker, Cloud platforms

## Authors

- Hasnat Abdul Moiz (211324)
- Tauseef Ahmad (211334)
- Computer Science Section-A, Islamia College Peshawar
