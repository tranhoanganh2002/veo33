import { apiClient } from './client';
import { 
  BriefInput, 
  Project, 
  RenderRequest, 
  StoryboardUpdateRequest 
} from '../types';

export const projectsApi = {
  // Create new project
  create: async (brief: BriefInput): Promise<Project> => {
    const response = await apiClient.post<Project>('/api/projects', brief);
    return response.data;
  },

  // List all projects
  list: async (skip = 0, limit = 20): Promise<Project[]> => {
    const response = await apiClient.get<Project[]>('/api/projects', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Get project by ID
  get: async (projectId: number): Promise<Project> => {
    const response = await apiClient.get<Project>(`/api/projects/${projectId}`);
    return response.data;
  },

  // Delete project
  delete: async (projectId: number): Promise<void> => {
    await apiClient.delete(`/api/projects/${projectId}`);
  },

  // Expand brief with Gemini
  expand: async (projectId: number): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/projects/${projectId}/expand`
    );
    return response.data;
  },

  // Generate storyboard
  generateStoryboard: async (projectId: number): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/projects/${projectId}/storyboard`
    );
    return response.data;
  },

  // Update storyboard selections
  updateStoryboard: async (
    projectId: number,
    update: StoryboardUpdateRequest
  ): Promise<Project> => {
    const response = await apiClient.put<Project>(
      `/api/projects/${projectId}/storyboard`,
      update
    );
    return response.data;
  },

  // Render video
  render: async (
    projectId: number,
    renderRequest: RenderRequest
  ): Promise<Project> => {
    const response = await apiClient.post<Project>(
      `/api/projects/${projectId}/render`,
      renderRequest
    );
    return response.data;
  },
};
