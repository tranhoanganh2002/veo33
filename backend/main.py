from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import asyncio

from database import get_db, engine, Base
from models import Project, ProjectStatus, RenderJob
from schemas import (
    BriefInput, 
    ProjectResponse, 
    StoryboardUpdateRequest, 
    RenderRequest,
    RenderJobResponse
)
from services.gemini_service import gemini_service
from services.storyboard_service import storyboard_service
from services.render_service import render_service
from config import get_settings

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="VEO3 Ultra + Gemini AI Video Generator",
    description="AI-powered video generation with Veo 3 Ultra and Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VEO3 Ultra + Gemini AI Video Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ========================================
# PROJECT MANAGEMENT ENDPOINTS
# ========================================

@app.post("/api/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(brief: BriefInput, db: Session = Depends(get_db)):
    """
    Create a new video generation project
    
    Args:
        brief: Project brief input data
        db: Database session
        
    Returns:
        Created project details
    """
    project = Project(
        title=brief.title,
        brief=brief.brief,
        target_audience=brief.target_audience,
        duration=brief.duration,
        tone=brief.tone,
        aspect_ratio=brief.aspect_ratio,
        style_references=brief.style_references,
        status=ProjectStatus.CREATED
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@app.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    List all projects with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of projects
    """
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get project details by ID
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Project details
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Success message
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete associated render jobs
    db.query(RenderJob).filter(RenderJob.project_id == project_id).delete()
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


# ========================================
# WORKFLOW STEP ENDPOINTS
# ========================================

@app.post("/api/projects/{project_id}/expand", response_model=ProjectResponse)
async def expand_brief(project_id: int, db: Session = Depends(get_db)):
    """
    Expand project brief with Gemini AI
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Updated project with expanded script
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update status
    project.status = ProjectStatus.EXPANDING
    db.commit()
    
    try:
        # Prepare brief data
        brief_data = {
            "title": project.title,
            "brief": project.brief,
            "target_audience": project.target_audience,
            "duration": project.duration,
            "tone": project.tone,
            "aspect_ratio": project.aspect_ratio
        }
        
        # Expand with Gemini
        result = await gemini_service.expand_brief(brief_data)
        
        # Update project
        project.expanded_prompt = result.get('expanded_prompt')
        project.script = {
            "overall_style": result.get('overall_style'),
            "scenes": result.get('scenes')
        }
        project.technical_params = result.get('technical_params')
        project.status = ProjectStatus.EXPANDED
        
        db.commit()
        db.refresh(project)
        
        return project
        
    except Exception as e:
        project.status = ProjectStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to expand brief: {str(e)}")


@app.post("/api/projects/{project_id}/storyboard", response_model=ProjectResponse)
async def generate_storyboard(project_id: int, db: Session = Depends(get_db)):
    """
    Generate storyboard preview images
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Updated project with storyboard
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.script:
        raise HTTPException(status_code=400, detail="Project script not generated yet")
    
    # Update status
    project.status = ProjectStatus.STORYBOARDING
    db.commit()
    
    try:
        # Generate storyboard
        storyboard = await storyboard_service.generate_storyboard(
            script=project.script,
            locked_attrs=project.locked_attributes
        )
        
        # Update project
        project.storyboard = storyboard
        project.status = ProjectStatus.STORYBOARDED
        
        db.commit()
        db.refresh(project)
        
        return project
        
    except Exception as e:
        project.status = ProjectStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to generate storyboard: {str(e)}")


@app.put("/api/projects/{project_id}/storyboard", response_model=ProjectResponse)
async def update_storyboard(
    project_id: int, 
    update: StoryboardUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update storyboard scene selections and locked attributes
    
    Args:
        project_id: Project ID
        update: Storyboard update data
        db: Database session
        
    Returns:
        Updated project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.storyboard:
        raise HTTPException(status_code=400, detail="Storyboard not generated yet")
    
    # Update selections
    storyboard = project.storyboard
    selected_ids = set(update.selected_scenes)
    
    for scene in storyboard:
        scene['selected'] = scene['scene_id'] in selected_ids
    
    project.storyboard = storyboard
    
    # Update locked attributes
    if update.locked_attributes:
        project.locked_attributes = update.locked_attributes
    
    db.commit()
    db.refresh(project)
    
    return project


@app.post("/api/projects/{project_id}/render", response_model=ProjectResponse)
async def render_video(
    project_id: int,
    render_request: RenderRequest,
    db: Session = Depends(get_db)
):
    """
    Start video rendering process (background task)
    
    Args:
        project_id: Project ID
        render_request: Render configuration
        db: Database session
        
    Returns:
        Updated project with rendering status
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.storyboard:
        raise HTTPException(status_code=400, detail="Storyboard not generated yet")
    
    # Update status
    project.status = ProjectStatus.RENDERING
    db.commit()
    
    try:
        # Render project
        result = await render_service.render_project(
            storyboard=project.storyboard,
            quality=render_request.quality,
            aspect_ratio=project.aspect_ratio,
            output_format=render_request.format,
            style_references=project.style_references
        )
        
        # Update project
        project.video_url = result['video_url']
        project.thumbnail_url = result['thumbnail_url']
        project.status = ProjectStatus.COMPLETED
        
        db.commit()
        db.refresh(project)
        
        return project
        
    except Exception as e:
        project.status = ProjectStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to render video: {str(e)}")


# ========================================
# RENDER JOBS ENDPOINTS (for tracking)
# ========================================

@app.get("/api/projects/{project_id}/jobs", response_model=List[RenderJobResponse])
async def list_render_jobs(project_id: int, db: Session = Depends(get_db)):
    """
    List render jobs for a project
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List of render jobs
    """
    jobs = db.query(RenderJob).filter(RenderJob.project_id == project_id).all()
    return jobs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
