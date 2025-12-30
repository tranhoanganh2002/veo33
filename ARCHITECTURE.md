# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                            │
│                      (React + TypeScript)                           │
└────────────────┬────────────────────────────────────────────────────┘
                 │ HTTP/REST API
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API                                 │
│                      (FastAPI + Python)                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │   Gemini   │  │    Veo     │  │ Storyboard │  │   Render   │  │
│  │  Service   │  │  Service   │  │  Service   │  │  Service   │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────┬─────────────────┬───────────────────────────────┬─────────┘
         │                 │                               │
         ▼                 ▼                               ▼
┌────────────────┐  ┌──────────────────┐      ┌─────────────────────┐
│  Google Gemini │  │  Veo 3 Ultra API │      │    PostgreSQL       │
│      API       │  │  (Placeholder)   │      │  + Redis Cache      │
└────────────────┘  └──────────────────┘      └─────────────────────┘
```

## Component Details

### Frontend Layer
```
┌─────────────────────────────────────────────────────────────┐
│                         App.tsx                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              4-Step Workflow Manager                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ BriefInput   │  │ Storyboard   │  │   Video      │    │
│  │ Component    │  │  Preview     │  │  Renderer    │    │
│  │   (Step 1)   │  │   (Step 2)   │  │  (Step 3)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API Client (Axios)                      │   │
│  │    - projects.ts: API endpoints                      │   │
│  │    - client.ts: HTTP client config                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Backend Layer
```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                     │   │
│  │  - CORS middleware                                   │   │
│  │  - 9 REST endpoints                                  │   │
│  │  - Request validation                                │   │
│  │  - Error handling                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  models.py  │  │ schemas.py  │  │ database.py │       │
│  │  (SQLAlch)  │  │ (Pydantic)  │  │  (Session)  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Services Layer
```
┌─────────────────────────────────────────────────────────────┐
│                      Services Package                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           GeminiService (gemini_service.py)          │  │
│  │  - expand_brief(): Brief → Detailed Script           │  │
│  │  - optimize_scene_prompt(): Scene → Optimized Text   │  │
│  │  - Fallback mechanism for API failures               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             VeoService (veo_service.py)              │  │
│  │  - generate_video_scene(): Create video clip         │  │
│  │  - generate_storyboard_frame(): Preview image        │  │
│  │  - poll_job_status(): Check render progress          │  │
│  │  - merge_scenes(): Combine clips into final video    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       StoryboardService (storyboard_service.py)      │  │
│  │  - generate_storyboard(): Process all scenes         │  │
│  │  - Parallel processing with asyncio                  │  │
│  │  - filter_selected_scenes(): Get selected only       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         RenderService (render_service.py)            │  │
│  │  - render_project(): Full project rendering          │  │
│  │  - render_single_scene(): Individual scene render    │  │
│  │  - Orchestrates Veo calls and merging                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Workflow 1: Brief Expansion
```
User Input → BriefInput Component → POST /api/projects
                                   → POST /api/projects/{id}/expand
                                   ↓
                            GeminiService.expand_brief()
                                   ↓
                            Gemini API (JSON Response)
                                   ↓
                            Parse & Store in Database
                                   ↓
                            Return expanded script
```

### Workflow 2: Storyboard Generation
```
Expanded Script → POST /api/projects/{id}/storyboard
                        ↓
                StoryboardService.generate_storyboard()
                        ↓
        ┌───────────────┴───────────────┐
        ▼                               ▼
Optimize Prompts (Gemini)    Generate Previews (Veo)
        │                               │
        └───────────────┬───────────────┘
                        ▼
              Parallel Processing (asyncio.gather)
                        ↓
                Store storyboard array
                        ↓
                Return to frontend
```

### Workflow 3: Video Rendering
```
Selected Scenes → POST /api/projects/{id}/render
                        ↓
                RenderService.render_project()
                        ↓
        ┌───────────────┴───────────────┐
        ▼                               ▼
   Render Each Scene             Poll for Completion
   (VeoService calls)             (Status checks)
        │                               │
        └───────────────┬───────────────┘
                        ▼
              Merge Scenes (transitions)
                        ↓
            Store video URL in database
                        ↓
              Return completed project
```

## Database Schema

### Project Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    brief TEXT NOT NULL,
    target_audience VARCHAR(255),
    duration FLOAT NOT NULL DEFAULT 30.0,
    tone VARCHAR(100),
    
    -- AI Generated
    expanded_prompt TEXT,
    script JSON,
    technical_params JSON,
    storyboard JSON,
    
    -- Status & Results
    status VARCHAR(20) NOT NULL,
    video_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    
    -- Metadata
    aspect_ratio VARCHAR(10) DEFAULT '16:9',
    style_references JSON,
    locked_attributes JSON,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### RenderJob Table
```sql
CREATE TABLE render_jobs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    scene_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    result_url VARCHAR(500),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Projects Management
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects (paginated)
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Delete project

### Workflow Steps
- `POST /api/projects/{id}/expand` - Expand brief with Gemini
- `POST /api/projects/{id}/storyboard` - Generate storyboard
- `PUT /api/projects/{id}/storyboard` - Update scene selections
- `POST /api/projects/{id}/render` - Start video rendering

### Monitoring
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/projects/{id}/jobs` - List render jobs

## Technology Stack

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.3
- **Build Tool**: Vite 5.0
- **Styling**: TailwindCSS 3.4
- **HTTP Client**: Axios 1.6
- **State Management**: React Query 5.17
- **Icons**: Lucide React 0.309

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic 1.13
- **Validation**: Pydantic 2.5
- **AI SDK**: google-generativeai 0.3

### Database & Cache
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Connection Pooling**: SQLAlchemy pool

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Uvicorn

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **CORS**: Configured to allow specific origins only
3. **SQL Injection**: Prevented by SQLAlchemy ORM
4. **XSS**: Prevented by React's automatic escaping
5. **Input Validation**: Pydantic schemas on all endpoints
6. **HTTPS**: Required in production
7. **Rate Limiting**: To be implemented for production

## Scalability Considerations

1. **Horizontal Scaling**: Backend can run multiple instances
2. **Database**: Connection pooling configured
3. **Cache**: Redis for frequently accessed data
4. **Async Operations**: FastAPI with asyncio for concurrent requests
5. **CDN**: For video delivery (to be implemented)
6. **Background Jobs**: Structure ready for Celery integration

## Performance Optimization

1. **Parallel Processing**: asyncio.gather() for storyboard generation
2. **Database Indexes**: On frequently queried fields
3. **Response Compression**: Gzip enabled
4. **Code Splitting**: Vite for optimized frontend bundles
5. **Lazy Loading**: Components loaded on demand

---

This architecture provides a solid foundation for the VEO3 Ultra + Gemini AI Video Generator, with room for future enhancements and scaling.
