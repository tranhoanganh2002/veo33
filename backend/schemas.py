from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from models import ProjectStatus


class BriefInput(BaseModel):
    """Input schema for creating a new project"""
    title: str = Field(..., min_length=1, max_length=255)
    brief: str = Field(..., min_length=10)
    target_audience: Optional[str] = Field(None, max_length=255)
    duration: float = Field(30.0, ge=10, le=300)
    tone: Optional[str] = Field(None, max_length=100)
    aspect_ratio: str = Field("16:9", pattern="^(16:9|9:16|1:1)$")
    style_references: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    """Response schema for project data"""
    id: int
    title: str
    brief: str
    target_audience: Optional[str]
    duration: float
    tone: Optional[str]
    expanded_prompt: Optional[str]
    script: Optional[Any]
    technical_params: Optional[Any]
    storyboard: Optional[Any]
    status: ProjectStatus
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    aspect_ratio: str
    style_references: Optional[Any]
    locked_attributes: Optional[Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StoryboardUpdateRequest(BaseModel):
    """Request schema for updating storyboard selections"""
    selected_scenes: List[int] = Field(..., description="Array of selected scene IDs")
    locked_attributes: Optional[dict] = Field(None, description="Locked attributes for consistency")


class RenderRequest(BaseModel):
    """Request schema for rendering video"""
    quality: str = Field("high", pattern="^(draft|high|ultra)$")
    format: str = Field("mp4", pattern="^(mp4|webm)$")
    include_subtitles: bool = Field(False)


class RenderJobResponse(BaseModel):
    """Response schema for render job"""
    id: int
    project_id: int
    scene_id: int
    prompt: str
    status: str
    progress: float
    result_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
