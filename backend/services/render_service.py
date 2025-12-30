from typing import Dict, Any, List, Optional
import asyncio
from services.veo_service import veo_service
from services.storyboard_service import storyboard_service


class RenderService:
    """Service for orchestrating video rendering"""
    
    async def render_project(
        self,
        storyboard: List[Dict[str, Any]],
        quality: str = "high",
        aspect_ratio: str = "16:9",
        output_format: str = "mp4",
        style_references: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Render complete project from storyboard
        
        Args:
            storyboard: Storyboard array with selected scenes
            quality: Video quality (draft, high, ultra)
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1)
            output_format: Output format (mp4, webm)
            style_references: Optional style reference URLs
            
        Returns:
            Dictionary with video_url, thumbnail_url, and metadata
        """
        # Filter selected scenes only
        selected_scenes = storyboard_service.filter_selected_scenes(storyboard)
        
        if not selected_scenes:
            raise ValueError("No scenes selected for rendering")
        
        # Render each scene
        scene_jobs = []
        for scene in selected_scenes:
            job = await veo_service.generate_video_scene(
                prompt=scene.get('optimized_prompt', ''),
                duration=scene.get('duration', 5.0),
                aspect_ratio=aspect_ratio,
                quality=quality,
                style_reference=style_references[0] if style_references else None
            )
            scene_jobs.append(job)
        
        # Poll for completion
        scene_urls = []
        for job in scene_jobs:
            result = await veo_service.poll_job_status(job['job_id'])
            if result['status'] == 'completed':
                scene_urls.append(result['result_url'])
            else:
                raise RuntimeError(f"Scene rendering failed: {result.get('error', 'Unknown error')}")
        
        # Merge scenes
        transitions = [
            scene.get('original_scene', {}).get('transition_to_next', 'cut')
            for scene in selected_scenes[:-1]
        ]
        
        final_video_url = await veo_service.merge_scenes(
            scene_urls=scene_urls,
            transitions=transitions,
            output_format=output_format
        )
        
        # Generate thumbnail from first scene
        thumbnail_url = scene_urls[0].replace('.mp4', '_thumb.jpg').replace('.webm', '_thumb.jpg')
        
        return {
            "video_url": final_video_url,
            "thumbnail_url": thumbnail_url,
            "metadata": {
                "aspect_ratio": aspect_ratio,
                "duration": sum(scene.get('duration', 0) for scene in selected_scenes),
                "scenes_count": len(selected_scenes),
                "quality": quality,
                "format": output_format
            }
        }
    
    async def render_single_scene(
        self,
        scene: Dict[str, Any],
        quality: str = "high",
        aspect_ratio: str = "16:9",
        style_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Render a single scene
        
        Args:
            scene: Scene dictionary with optimized prompt
            quality: Video quality
            aspect_ratio: Aspect ratio
            style_reference: Optional style reference
            
        Returns:
            Dictionary with video URL and status
        """
        job = await veo_service.generate_video_scene(
            prompt=scene.get('optimized_prompt', ''),
            duration=scene.get('duration', 5.0),
            aspect_ratio=aspect_ratio,
            quality=quality,
            style_reference=style_reference
        )
        
        result = await veo_service.poll_job_status(job['job_id'])
        
        return {
            "status": result['status'],
            "video_url": result.get('result_url'),
            "thumbnail_url": result.get('thumbnail_url')
        }


# Singleton instance
render_service = RenderService()
