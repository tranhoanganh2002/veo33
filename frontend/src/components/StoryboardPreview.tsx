import { useState, useEffect } from 'react';
import { Loader2, Film, Check, ArrowLeft } from 'lucide-react';
import { Project, StoryboardItem } from '../types';
import { projectsApi } from '../api/projects';

interface Props {
  project: Project;
  onStoryboardReady: (project: Project) => void;
  onBack: () => void;
}

export default function StoryboardPreview({ project, onStoryboardReady, onBack }: Props) {
  const [loading, setLoading] = useState(false);
  const [storyboard, setStoryboard] = useState<StoryboardItem[]>(project.storyboard || []);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Generate storyboard if not already generated
    if (!project.storyboard) {
      generateStoryboard();
    } else {
      setStoryboard(project.storyboard);
    }
  }, []);

  const generateStoryboard = async () => {
    setLoading(true);
    setError(null);

    try {
      const updatedProject = await projectsApi.generateStoryboard(project.id);
      setStoryboard(updatedProject.storyboard || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Không thể tạo storyboard. Vui lòng thử lại.');
      console.error('Error generating storyboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleScene = (sceneId: number) => {
    setStoryboard(prev =>
      prev.map(scene =>
        scene.scene_id === sceneId ? { ...scene, selected: !scene.selected } : scene
      )
    );
  };

  const handleSaveAndContinue = async () => {
    setLoading(true);
    setError(null);

    try {
      const selectedSceneIds = storyboard
        .filter(scene => scene.selected)
        .map(scene => scene.scene_id);

      if (selectedSceneIds.length === 0) {
        setError('Vui lòng chọn ít nhất một cảnh để tiếp tục.');
        setLoading(false);
        return;
      }

      const updatedProject = await projectsApi.updateStoryboard(project.id, {
        selected_scenes: selectedSceneIds,
      });

      onStoryboardReady({ ...updatedProject, storyboard });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Không thể lưu storyboard. Vui lòng thử lại.');
      console.error('Error updating storyboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedCount = storyboard.filter(scene => scene.selected).length;
  const totalDuration = storyboard
    .filter(scene => scene.selected)
    .reduce((sum, scene) => sum + scene.duration, 0);

  if (loading && storyboard.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-12 h-12 text-purple-600 animate-spin mb-4" />
          <p className="text-gray-600 text-lg">Đang tạo storyboard...</p>
          <p className="text-gray-500 text-sm mt-2">
            Gemini AI đang tối ưu hóa prompt và tạo preview cho từng cảnh
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Film className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-800">
            Bước 2: Xem và chỉnh sửa Storyboard
          </h2>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 text-gray-600 hover:text-gray-800 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Quay lại
        </button>
      </div>

      {/* Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">
              Đã chọn: <span className="font-bold text-purple-700">{selectedCount}</span> /{' '}
              {storyboard.length} cảnh
            </p>
            <p className="text-sm text-gray-600">
              Tổng thời lượng: <span className="font-bold text-purple-700">{totalDuration.toFixed(1)}s</span>
            </p>
          </div>
          <p className="text-xs text-gray-500">
            Click vào cảnh để chọn/bỏ chọn
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Storyboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {storyboard.map((scene) => (
          <div
            key={scene.scene_id}
            onClick={() => toggleScene(scene.scene_id)}
            className={`border-2 rounded-lg overflow-hidden cursor-pointer transition-all ${
              scene.selected
                ? 'border-purple-600 shadow-lg'
                : 'border-gray-300 opacity-50 hover:opacity-75'
            }`}
          >
            {/* Scene Number Badge */}
            <div className="relative">
              <img
                src={scene.preview_url}
                alt={`Scene ${scene.scene_id}`}
                className="w-full aspect-video object-cover"
              />
              <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">
                Cảnh {scene.scene_id}
              </div>
              {scene.selected && (
                <div className="absolute top-2 right-2 bg-purple-600 text-white p-1 rounded-full">
                  <Check className="w-4 h-4" />
                </div>
              )}
            </div>

            {/* Scene Info */}
            <div className="p-4 bg-white">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {scene.shot_type} • {scene.duration}s
                </span>
                <span className="text-xs text-gray-500">
                  {scene.camera_movement}
                </span>
              </div>
              <p className="text-sm text-gray-600 line-clamp-3">
                {scene.optimized_prompt}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={handleSaveAndContinue}
          disabled={loading || selectedCount === 0}
          className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Đang lưu...
            </>
          ) : (
            <>
              Lưu và Tiếp tục Render
            </>
          )}
        </button>
      </div>
    </div>
  );
}
