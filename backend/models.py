from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """Project status enum"""
    CREATED = "created"
    EXPANDING = "expanding"
    EXPANDED = "expanded"
    STORYBOARDING = "storyboarding"
    STORYBOARDED = "storyboarded"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """Project model for storing video generation projects"""
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False)
    brief = Column(Text, nullable=False)
    target_audience = Column(String(255), nullable=True)
    duration = Column(Float, nullable=False, default=30.0)
    tone = Column(String(100), nullable=True)
    
    # Gemini generated
    expanded_prompt = Column(Text, nullable=True)
    script = Column(JSON, nullable=True)  # Array of scenes
    technical_params = Column(JSON, nullable=True)  # Overall style & params
    
    # Storyboard
    storyboard = Column(JSON, nullable=True)  # Array of preview images + prompts
    
    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.CREATED, nullable=False)
    video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Metadata
    aspect_ratio = Column(String(10), default="16:9", nullable=False)
    style_references = Column(JSON, nullable=True)  # Array of style reference URLs
    locked_attributes = Column(JSON, nullable=True)  # Attributes for consistency
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RenderJob(Base):
    """Render job model for background tracking"""
    __tablename__ = "render_jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Job details
    scene_id = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 - 1.0
    
    # Results
    result_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
