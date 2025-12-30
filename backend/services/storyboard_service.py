from typing import Dict, Any, List, Optional
import asyncio
from services.gemini_service import gemini_service
from services.veo_service import veo_service


class StoryboardService:
    """Service for generating storyboard previews"""
    
    async def generate_storyboard(
        self,
        script: Dict[str, Any],
        locked_attrs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate storyboard with preview images for all scenes
        
        Args:
            script: Script dictionary with scenes array
            locked_attrs: Optional locked attributes for consistency
            
        Returns:
            Array of storyboard items with preview images and optimized prompts
        """
        scenes = script.get('scenes', [])
        
        if not scenes:
            return []
        
        # Process all scenes in parallel
        tasks = [
            self._process_scene(scene, locked_attrs)
            for scene in scenes
        ]
        
        storyboard = await asyncio.gather(*tasks)
        return storyboard
    
    async def _process_scene(
        self,
        scene: Dict[str, Any],
        locked_attrs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process individual scene: optimize prompt and generate preview
        
        Args:
            scene: Scene dictionary
            locked_attrs: Locked attributes
            
        Returns:
            Storyboard item dictionary
        """
        # Optimize prompt with Gemini
        optimized_prompt = await gemini_service.optimize_scene_prompt(scene, locked_attrs)
        
        # Generate preview image
        preview_url = await veo_service.generate_storyboard_frame(optimized_prompt)
        
        return {
            "scene_id": scene.get('id'),
            "preview_url": preview_url,
            "optimized_prompt": optimized_prompt,
            "duration": scene.get('duration', 5.0),
            "shot_type": scene.get('shot_type', 'medium'),
            "camera_movement": scene.get('camera_movement', 'static'),
            "selected": True,  # Default to selected
            "original_scene": scene
        }
    
    def filter_selected_scenes(self, storyboard: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter only selected scenes from storyboard
        
        Args:
            storyboard: Full storyboard array
            
        Returns:
            Filtered array of selected scenes only
        """
        return [item for item in storyboard if item.get('selected', True)]
    
    def calculate_total_duration(self, storyboard: List[Dict[str, Any]]) -> float:
        """
        Calculate total duration of selected scenes
        
        Args:
            storyboard: Storyboard array
            
        Returns:
            Total duration in seconds
        """
        selected = self.filter_selected_scenes(storyboard)
        return sum(scene.get('duration', 0) for scene in selected)


# Singleton instance
storyboard_service = StoryboardService()
