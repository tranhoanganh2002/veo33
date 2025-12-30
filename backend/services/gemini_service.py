import google.generativeai as genai
from config import get_settings
import json
import re
from typing import Dict, Any, Optional

settings = get_settings()


class GeminiService:
    """Service for Gemini AI integration"""
    
    def __init__(self):
        """Initialize Gemini API"""
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def expand_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand user brief into detailed script with scenes
        
        Args:
            brief_data: Dictionary containing title, brief, target_audience, duration, tone, aspect_ratio
            
        Returns:
            Dictionary with expanded_prompt, overall_style, technical_params, and scenes array
        """
        if not self.model:
            return self._generate_fallback_script(brief_data)
        
        try:
            prompt = self._build_expansion_prompt(brief_data)
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            result = self._parse_gemini_response(response.text)
            return result
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_script(brief_data)
    
    def _build_expansion_prompt(self, brief_data: Dict[str, Any]) -> str:
        """Build detailed prompt for Gemini"""
        return f"""You are an expert cinematographer and AI video prompt engineer. Convert this video brief into a detailed, production-ready script.

Brief Information:
- Title: {brief_data.get('title')}
- Description: {brief_data.get('brief')}
- Target Audience: {brief_data.get('target_audience', 'General')}
- Duration: {brief_data.get('duration', 30)} seconds
- Tone: {brief_data.get('tone', 'Professional')}
- Aspect Ratio: {brief_data.get('aspect_ratio', '16:9')}

Generate a comprehensive video production plan in JSON format with the following structure:

{{
  "expanded_prompt": "A concise 2-3 sentence summary of the overall video concept",
  "overall_style": {{
    "visual_style": "Detailed description of the visual aesthetic",
    "color_palette": ["color1", "color2", "color3"],
    "mood": "Overall mood/atmosphere",
    "pacing": "Description of video pacing"
  }},
  "technical_params": {{
    "default_lens": "Lens type (e.g., 35mm, 50mm, 24-70mm)",
    "camera_style": "Camera movement style",
    "lighting": "Lighting approach"
  }},
  "scenes": [
    {{
      "id": 1,
      "description": "Extremely detailed visual description of the scene including: environment, subjects, actions, spatial layout, lighting conditions, specific colors, textures, and atmosphere",
      "duration": 5.0,
      "shot_type": "wide|medium|close-up|extreme-close-up",
      "camera_movement": "static|pan|tilt|dolly|crane|tracking|handheld",
      "lens": "Specific lens (e.g., 24mm wide angle, 85mm portrait)",
      "focal_length": "e.g., 24mm, 50mm, 85mm",
      "aperture": "e.g., f/2.8, f/5.6",
      "lighting": "Detailed lighting description",
      "color_notes": "Specific color emphasis for this scene",
      "mood": "Scene-specific mood",
      "transition_to_next": "cut|fade|dissolve|wipe"
    }}
  ]
}}

Requirements:
- Create {max(3, int(brief_data.get('duration', 30) / 10))} to {max(5, int(brief_data.get('duration', 30) / 5))} scenes
- Each scene should have extremely detailed visual descriptions (minimum 100 words)
- Include specific technical cinematography details
- Ensure total duration matches approximately {brief_data.get('duration', 30)} seconds
- Descriptions should be vivid enough for AI video generation
- Return ONLY valid JSON, no markdown formatting

JSON OUTPUT:"""
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response with fallback"""
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            cleaned = re.sub(r'```json\s*|\s*```', '', response_text)
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError("Could not parse JSON from Gemini response")
    
    def _generate_fallback_script(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic script when Gemini API is unavailable"""
        duration = brief_data.get('duration', 30)
        num_scenes = max(3, int(duration / 10))
        scene_duration = duration / num_scenes
        
        scenes = []
        for i in range(num_scenes):
            scenes.append({
                "id": i + 1,
                "description": f"Scene {i + 1}: {brief_data.get('brief', 'Video content')} - Part {i + 1}. Professional cinematography with balanced composition, natural lighting, and smooth camera work. High attention to detail and visual quality.",
                "duration": scene_duration,
                "shot_type": ["wide", "medium", "close-up"][i % 3],
                "camera_movement": "static",
                "lens": "50mm",
                "focal_length": "50mm",
                "aperture": "f/2.8",
                "lighting": "Natural, balanced lighting",
                "color_notes": "Natural color palette",
                "mood": brief_data.get('tone', 'Professional'),
                "transition_to_next": "cut" if i < num_scenes - 1 else None
            })
        
        return {
            "expanded_prompt": f"{brief_data.get('title')}: {brief_data.get('brief')}",
            "overall_style": {
                "visual_style": "Professional cinematography with clean composition",
                "color_palette": ["neutral", "balanced", "natural"],
                "mood": brief_data.get('tone', 'Professional'),
                "pacing": "Steady and engaging"
            },
            "technical_params": {
                "default_lens": "50mm",
                "camera_style": "Smooth and professional",
                "lighting": "Natural balanced lighting"
            },
            "scenes": scenes
        }
    
    async def optimize_scene_prompt(self, scene: Dict[str, Any], locked_attrs: Optional[Dict[str, Any]] = None) -> str:
        """
        Optimize individual scene prompt for Veo 3 Ultra
        
        Args:
            scene: Scene dictionary with description and technical params
            locked_attrs: Optional locked attributes for consistency
            
        Returns:
            Optimized prompt string for video generation
        """
        if not self.model:
            return self._generate_basic_prompt(scene, locked_attrs)
        
        try:
            prompt = f"""You are an expert at writing prompts for AI video generation systems. 
Convert this scene description into an optimal prompt for Veo 3 Ultra video generation.

Scene Details:
{json.dumps(scene, indent=2)}

Locked Attributes (must maintain consistency):
{json.dumps(locked_attrs or {}, indent=2)}

Requirements:
- Create a single, detailed paragraph (150-250 words)
- Include all visual elements, camera work, lighting, and mood
- Be extremely specific about colors, textures, and spatial relationships
- Include technical cinematography terms
- Maintain consistency with locked attributes
- NO JSON, NO bullet points, just a flowing descriptive paragraph
- Start directly with the visual description

Optimized Prompt:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini optimization error: {e}")
            return self._generate_basic_prompt(scene, locked_attrs)
    
    def _generate_basic_prompt(self, scene: Dict[str, Any], locked_attrs: Optional[Dict[str, Any]] = None) -> str:
        """Generate basic prompt without Gemini"""
        parts = [scene.get('description', '')]
        
        # Add technical details
        if scene.get('shot_type'):
            parts.append(f"{scene['shot_type']} shot")
        if scene.get('camera_movement') and scene['camera_movement'] != 'static':
            parts.append(f"{scene['camera_movement']} camera movement")
        if scene.get('lens'):
            parts.append(f"shot with {scene['lens']}")
        if scene.get('lighting'):
            parts.append(f"{scene['lighting']}")
        if scene.get('mood'):
            parts.append(f"{scene['mood']} atmosphere")
        
        # Add locked attributes
        if locked_attrs:
            if locked_attrs.get('character'):
                parts.append(f"featuring {locked_attrs['character']}")
            if locked_attrs.get('color_palette'):
                parts.append(f"with {', '.join(locked_attrs['color_palette'])} color palette")
        
        return ". ".join(parts) + ". Professional cinematography, high quality, detailed, 4K resolution."


# Singleton instance
gemini_service = GeminiService()
