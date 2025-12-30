# Deployment Guide

This guide covers deploying the VEO3 Ultra + Gemini AI Video Generator to production.

## Prerequisites

- Docker & Docker Compose installed
- PostgreSQL database (managed service recommended)
- Redis instance (managed service recommended)
- Domain name with SSL certificate
- API keys for Gemini and Veo 3 Ultra

## Production Environment Variables

### Backend (.env)

```env
# API Keys (REQUIRED)
GEMINI_API_KEY=your_production_gemini_key
VEO_API_KEY=your_production_veo_key

# Database (use managed service)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (use managed service)
REDIS_URL=redis://host:6379/0

# Security (IMPORTANT)
SECRET_KEY=generate-a-strong-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Config
DEBUG=False
UPLOAD_DIR=/app/uploads
OUTPUT_DIR=/app/outputs
MAX_VIDEO_DURATION=300
```

### Frontend (.env.production)

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Deployment Options

### Option 1: Docker Compose (Simple VPS)

1. **Prepare server:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone and configure:**
```bash
git clone https://github.com/tranhoanganh2002/veo33.git
cd veo33

# Setup environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.production

# Edit with your production values
nano backend/.env
nano frontend/.env.production
```

3. **Deploy:**
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

4. **Setup Nginx reverse proxy:**
```nginx
# /etc/nginx/sites-available/veo3

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/veo3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

### Option 2: AWS ECS/Fargate

1. **Build and push images:**
```bash
# Build
docker build -t veo3-backend ./backend
docker build -t veo3-frontend ./frontend

# Tag
docker tag veo3-backend:latest <ECR_URI>/veo3-backend:latest
docker tag veo3-frontend:latest <ECR_URI>/veo3-frontend:latest

# Push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ECR_URI>
docker push <ECR_URI>/veo3-backend:latest
docker push <ECR_URI>/veo3-frontend:latest
```

2. **Create ECS task definition and service**
3. **Setup RDS PostgreSQL and ElastiCache Redis**
4. **Configure ALB for load balancing**
5. **Setup CloudFront for CDN**

### Option 3: Google Cloud Run

1. **Build and push:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/veo3-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/veo3-frontend ./frontend
```

2. **Deploy:**
```bash
# Backend
gcloud run deploy veo3-backend \
  --image gcr.io/PROJECT_ID/veo3-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=...,REDIS_URL=...

# Frontend
gcloud run deploy veo3-frontend \
  --image gcr.io/PROJECT_ID/veo3-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Setup Cloud SQL (PostgreSQL) and Memorystore (Redis)**

### Option 4: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure components:**
   - Backend: Docker, port 8000
   - Frontend: Docker, port 5173
   - Database: Managed PostgreSQL
   - Cache: Managed Redis
3. **Set environment variables**
4. **Deploy**

## Database Setup

### Initial Migration

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Backup Strategy

```bash
# Automated daily backups
0 2 * * * pg_dump $DATABASE_URL > /backups/veo3_$(date +\%Y\%m\%d).sql
```

## Storage Configuration

For production, use cloud storage for uploads and outputs:

### AWS S3

```python
# config.py
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id=settings.aws_access_key,
    aws_secret_access_key=settings.aws_secret_key
)
```

### Google Cloud Storage

```python
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('veo3-videos')
```

## Monitoring

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend health
curl https://yourdomain.com/
```

### Logging

**Backend logs:**
```bash
docker-compose logs -f backend
```

**Setup log aggregation:**
- AWS CloudWatch Logs
- Google Cloud Logging
- Datadog
- New Relic

### Metrics

Monitor:
- API response times
- Video generation success rate
- Database query performance
- Redis cache hit rate
- Disk usage for uploads/outputs

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Strong SECRET_KEY configured
- [ ] Database credentials secured
- [ ] API keys stored securely (not in code)
- [ ] CORS configured for production domain only
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention
- [ ] Regular dependency updates
- [ ] Database backups automated
- [ ] Access logs enabled

## Scaling

### Horizontal Scaling

- Deploy multiple backend instances behind load balancer
- Use managed PostgreSQL with read replicas
- Use Redis cluster for distributed caching
- Store videos on CDN (CloudFront, Cloud CDN)

### Performance Optimization

- Enable database connection pooling
- Implement Redis caching for frequent queries
- Use CDN for static assets
- Enable gzip compression
- Optimize database indexes
- Implement background job queue for video rendering

## Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify API keys are set
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify VITE_API_BASE_URL is correct
- Check CORS settings in backend
- Verify reverse proxy configuration

### Database connection errors
- Check PostgreSQL is running
- Verify connection string
- Check firewall rules

### Video generation fails
- Verify Gemini API key is valid
- Verify Veo API key is valid
- Check API quota limits
- Review error logs

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Cleanup

```bash
# Remove old videos (older than 30 days)
find /app/outputs -mtime +30 -delete

# Docker cleanup
docker system prune -a
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/tranhoanganh2002/veo33/issues
- Email: support@veo3.ai
