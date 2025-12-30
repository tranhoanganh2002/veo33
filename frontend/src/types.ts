export type ProjectStatus = 
  | "created"
  | "expanding"
  | "expanded"
  | "storyboarding"
  | "storyboarded"
  | "rendering"
  | "completed"
  | "failed";

export interface BriefInput {
  title: string;
  brief: string;
  target_audience?: string;
  duration: number;
  tone?: string;
  aspect_ratio: "16:9" | "9:16" | "1:1";
  style_references?: string[];
}

export interface Scene {
  id: number;
  description: string;
  duration: number;
  shot_type: string;
  camera_movement: string;
  lens: string;
  focal_length: string;
  aperture: string;
  lighting: string;
  color_notes: string;
  mood: string;
  transition_to_next?: string;
}

export interface StoryboardItem {
  scene_id: number;
  preview_url: string;
  optimized_prompt: string;
  duration: number;
  shot_type: string;
  camera_movement: string;
  selected: boolean;
  original_scene: Scene;
}

export interface Project {
  id: number;
  title: string;
  brief: string;
  target_audience?: string;
  duration: number;
  tone?: string;
  expanded_prompt?: string;
  script?: {
    overall_style: {
      visual_style: string;
      color_palette: string[];
      mood: string;
      pacing: string;
    };
    scenes: Scene[];
  };
  technical_params?: any;
  storyboard?: StoryboardItem[];
  status: ProjectStatus;
  video_url?: string;
  thumbnail_url?: string;
  aspect_ratio: string;
  style_references?: string[];
  locked_attributes?: any;
  created_at: string;
  updated_at?: string;
}

export interface RenderRequest {
  quality: "draft" | "high" | "ultra";
  format: "mp4" | "webm";
  include_subtitles: boolean;
}

export interface StoryboardUpdateRequest {
  selected_scenes: number[];
  locked_attributes?: any;
}
