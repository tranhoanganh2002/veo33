# Quick Start Guide

## Prerequisites
- Docker & Docker Compose installed
- API keys for Gemini (required) and Veo 3 Ultra (when available)

## Installation (3 steps)

### Step 1: Clone & Configure
```bash
# Clone repository
git clone https://github.com/tranhoanganh2002/veo33.git
cd veo33

# Setup environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit backend/.env and add your API keys
nano backend/.env  # or use your preferred editor
```

### Step 2: Start Services
```bash
# Option A: Use setup script (recommended)
chmod +x setup.sh
./setup.sh

# Option B: Manual start
docker-compose up -d
sleep 30
docker-compose exec backend alembic upgrade head
```

### Step 3: Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## First Use

1. **Open Frontend** at http://localhost:5173
2. **Enter Project Details:**
   - Title: "Test Video"
   - Brief: "Create a 30-second product demo video with professional cinematography"
   - Duration: 30 seconds
   - Aspect Ratio: 16:9
3. **Click "Tạo kịch bản với AI"** - Gemini will expand your brief
4. **Review Storyboard** - See preview images for each scene
5. **Select Scenes** - Click to select/deselect scenes
6. **Configure Render** - Choose quality and format
7. **Render Video** - Wait for completion
8. **Download** - Get your generated video

## Troubleshooting

### Services won't start
```bash
# Check if ports are available
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# View logs
docker-compose logs -f
```

### Backend errors
```bash
# Check backend logs
docker-compose logs backend

# Verify database
docker-compose exec postgres psql -U postgres -d veo3db -c "\dt"

# Restart backend
docker-compose restart backend
```

### Frontend can't connect
- Check `frontend/.env.local` has correct `VITE_API_BASE_URL`
- Verify CORS settings in `backend/main.py`
- Check browser console for errors

### Gemini API errors
- Verify API key in `backend/.env`
- Check API quota at https://ai.google.dev/
- Review logs: `docker-compose logs backend | grep -i gemini`

## Common Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild images
docker-compose build
docker-compose up -d

# Execute command in backend
docker-compose exec backend python -c "print('Hello')"

# Access database
docker-compose exec postgres psql -U postgres -d veo3db

# Create database backup
docker-compose exec postgres pg_dump -U postgres veo3db > backup.sql
```

## Development Workflow

### Backend Development
```bash
# Install dependencies locally
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally (without Docker)
uvicorn main:app --reload --port 8000

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Run locally (without Docker)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Testing

### Using cURL
```bash
# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Video",
    "brief": "Create a short video",
    "duration": 30,
    "aspect_ratio": "16:9"
  }'

# List projects
curl http://localhost:8000/api/projects

# Get project
curl http://localhost:8000/api/projects/1
```

### Using API Docs
Visit http://localhost:8000/docs for interactive API documentation.

## Environment Variables

### Backend Required
- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

### Backend Optional
- `VEO_API_KEY` - Veo 3 Ultra API key (when available)
- `SECRET_KEY` - JWT secret key
- `DEBUG` - Debug mode (True/False)
- `MAX_VIDEO_DURATION` - Maximum video duration in seconds

### Frontend Required
- `VITE_API_BASE_URL` - Backend API URL

## Next Steps

1. **Test the workflow** - Create a test project
2. **Review the code** - Understand the architecture
3. **Customize** - Modify to fit your needs
4. **Deploy** - See DEPLOYMENT.md for production setup
5. **Integrate Veo API** - When API becomes available

## Support

- Documentation: See README.md
- Issues: https://github.com/tranhoanganh2002/veo33/issues
- Deployment: See DEPLOYMENT.md
