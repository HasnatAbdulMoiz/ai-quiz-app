# AI-Powered Quiz System Agent - Deployment Guide

## Overview

This guide covers deploying the AI-Powered Quiz System Agent to various cloud platforms. The system consists of:
- **Frontend**: React application with Tailwind CSS
- **Backend**: FastAPI with PostgreSQL database
- **AI Agent**: LangChain/LangGraph integration with DeepSeek LLM

## Prerequisites

- Docker and Docker Compose
- Cloud platform account (AWS/GCP/Azure)
- Domain name (optional)
- API keys for external services

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd quiz-system-agent
```

### 2. Environment Configuration

Create environment files:

```bash
# Backend environment
cp backend/env.example backend/.env

# Edit backend/.env with your configuration
DATABASE_URL=postgresql://quiz_user:quiz_password@postgres:5432/quiz_system
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
SENDGRID_API_KEY=your-sendgrid-api-key-here
FROM_EMAIL=noreply@quizsystem.com
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Production Deployment

### Option 1: Docker Compose (Single Server)

#### 1. Production Environment Setup

```bash
# Create production environment file
cp backend/env.example backend/.env.prod

# Update with production values
DATABASE_URL=postgresql://quiz_user:STRONG_PASSWORD@postgres:5432/quiz_system
JWT_SECRET_KEY=STRONG_JWT_SECRET_KEY
DEEPSEEK_API_KEY=your-deepseek-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
```

#### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: quiz_system
      POSTGRES_USER: quiz_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - quiz_network

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://quiz_user:${POSTGRES_PASSWORD}@postgres:5432/quiz_system
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - FROM_EMAIL=${FROM_EMAIL}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
      - DEBUG=False
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - quiz_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_URL=${API_URL}
    restart: unless-stopped
    networks:
      - quiz_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - quiz_network

volumes:
  postgres_data:

networks:
  quiz_network:
    driver: bridge
```

#### 3. Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 4. Deploy

```bash
# Create production environment file
echo "POSTGRES_PASSWORD=your_strong_password" > .env.prod
echo "JWT_SECRET_KEY=your_jwt_secret" >> .env.prod
echo "DEEPSEEK_API_KEY=your_deepseek_key" >> .env.prod
echo "API_URL=https://yourdomain.com/api" >> .env.prod
echo "CORS_ORIGINS=https://yourdomain.com" >> .env.prod

# Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Option 2: AWS Deployment

#### 1. AWS ECS with Fargate

```yaml
# aws-ecs-task-definition.json
{
  "family": "quiz-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/quiz-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/quiz_system"
        }
      ],
      "secrets": [
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:quiz-system/jwt-key"
        }
      ]
    }
  ]
}
```

#### 2. AWS RDS PostgreSQL

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier quiz-system-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username quiz_user \
  --master-user-password your_password \
  --allocated-storage 20
```

#### 3. AWS ECR for Container Registry

```bash
# Create ECR repositories
aws ecr create-repository --repository-name quiz-backend
aws ecr create-repository --repository-name quiz-frontend

# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

docker build -t quiz-backend ./backend
docker tag quiz-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/quiz-backend:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/quiz-backend:latest
```

### Option 3: Google Cloud Platform

#### 1. Cloud Run Deployment

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/quiz-backend', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/quiz-backend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'quiz-backend', '--image', 'gcr.io/$PROJECT_ID/quiz-backend', '--platform', 'managed', '--region', 'us-central1']
```

#### 2. Cloud SQL PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create quiz-system-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create quiz_system --instance=quiz-system-db
```

### Option 4: Azure Container Instances

#### 1. Azure Container Registry

```bash
# Create ACR
az acr create --resource-group myResourceGroup --name quizsystemregistry --sku Basic

# Build and push images
az acr build --registry quizsystemregistry --image quiz-backend:latest ./backend
```

#### 2. Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group myResourceGroup \
  --name quiz-system-db \
  --location eastus \
  --admin-user quizuser \
  --admin-password your_password \
  --sku-name GP_Gen5_2
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Secret for JWT token signing | `your-secret-key` |
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI generation | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | Email notifications | - |
| `TWILIO_ACCOUNT_SID` | SMS notifications | - |
| `DEBUG` | Debug mode | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl https://yourdomain.com/api/health

# Check database connection
curl https://yourdomain.com/api/health/db
```

### Logs

```bash
# View application logs
docker-compose logs -f backend

# View specific service logs
docker-compose logs -f postgres
```

### Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U quiz_user quiz_system > backup.sql

# Restore database
docker-compose exec -T postgres psql -U quiz_user quiz_system < backup.sql
```

## Security Considerations

1. **Environment Variables**: Store sensitive data in environment variables or secret management services
2. **HTTPS**: Always use HTTPS in production
3. **Database Security**: Use strong passwords and restrict database access
4. **API Keys**: Rotate API keys regularly
5. **CORS**: Configure CORS properly for your domain
6. **Rate Limiting**: Implement rate limiting for API endpoints

## Scaling

### Horizontal Scaling

- Use load balancers for multiple backend instances
- Implement database read replicas
- Use CDN for static assets

### Vertical Scaling

- Increase container resources
- Upgrade database instance size
- Optimize database queries

## Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL and network connectivity
2. **CORS Errors**: Verify CORS_ORIGINS configuration
3. **AI Generation Fails**: Check DEEPSEEK_API_KEY and API limits
4. **Email Notifications**: Verify SENDGRID_API_KEY and email configuration

### Debug Mode

```bash
# Enable debug mode
export DEBUG=True
docker-compose up -d
```

## Support

For issues and questions:
- Check the logs: `docker-compose logs -f`
- Review environment configuration
- Verify external service API keys
- Check network connectivity
