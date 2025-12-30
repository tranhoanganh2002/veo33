import { useState } from 'react';
import { Loader2, Video, ArrowLeft } from 'lucide-react';
import { Project, RenderRequest } from '../types';
import { projectsApi } from '../api/projects';

interface Props {
  project: Project;
  onVideoReady: (project: Project) => void;
  onBack: () => void;
}

export default function VideoRenderer({ project, onVideoReady, onBack }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [renderConfig, setRenderConfig] = useState<RenderRequest>({
    quality: 'high',
    format: 'mp4',
    include_subtitles: false,
  });

  const handleRender = async () => {
    setLoading(true);
    setError(null);

    try {
      const updatedProject = await projectsApi.render(project.id, renderConfig);
      onVideoReady(updatedProject);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Không thể render video. Vui lòng thử lại.');
      console.error('Error rendering video:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedScenes = project.storyboard?.filter(scene => scene.selected) || [];

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Video className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-800">
            Bước 3: Render Video
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

      {/* Render Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mb-6">
        <h3 className="font-semibold text-gray-800 mb-3">Thông tin render:</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Số cảnh: </span>
            <span className="font-bold text-purple-700">{selectedScenes.length}</span>
          </div>
          <div>
            <span className="text-gray-600">Tỉ lệ khung hình: </span>
            <span className="font-bold text-purple-700">{project.aspect_ratio}</span>
          </div>
          <div>
            <span className="text-gray-600">Thời lượng: </span>
            <span className="font-bold text-purple-700">
              {selectedScenes.reduce((sum, scene) => sum + scene.duration, 0).toFixed(1)}s
            </span>
          </div>
          <div>
            <span className="text-gray-600">Giọng điệu: </span>
            <span className="font-bold text-purple-700">{project.tone || 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Render Configuration */}
      <div className="space-y-6 mb-6">
        {/* Quality */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Chất lượng
          </label>
          <div className="grid grid-cols-3 gap-4">
            {(['draft', 'high', 'ultra'] as const).map((quality) => (
              <button
                key={quality}
                type="button"
                onClick={() => setRenderConfig(prev => ({ ...prev, quality }))}
                disabled={loading}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition-colors disabled:cursor-not-allowed ${
                  renderConfig.quality === quality
                    ? 'border-purple-600 bg-purple-50 text-purple-700'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {quality === 'draft' && 'Nháp'}
                {quality === 'high' && 'Cao'}
                {quality === 'ultra' && 'Siêu cao'}
                <div className="text-xs text-gray-500 mt-1">
                  {quality === 'draft' && 'Nhanh, chất lượng cơ bản'}
                  {quality === 'high' && 'Cân bằng tốt'}
                  {quality === 'ultra' && 'Chất lượng tốt nhất'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Định dạng
          </label>
          <div className="grid grid-cols-2 gap-4">
            {(['mp4', 'webm'] as const).map((format) => (
              <button
                key={format}
                type="button"
                onClick={() => setRenderConfig(prev => ({ ...prev, format }))}
                disabled={loading}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition-colors disabled:cursor-not-allowed ${
                  renderConfig.format === format
                    ? 'border-purple-600 bg-purple-50 text-purple-700'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {format.toUpperCase()}
                <div className="text-xs text-gray-500 mt-1">
                  {format === 'mp4' && 'Phổ biến nhất'}
                  {format === 'webm' && 'Tối ưu cho web'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Subtitles */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="subtitles"
            checked={renderConfig.include_subtitles}
            onChange={(e) =>
              setRenderConfig(prev => ({ ...prev, include_subtitles: e.target.checked }))
            }
            disabled={loading}
            className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500 disabled:cursor-not-allowed"
          />
          <label htmlFor="subtitles" className="ml-2 text-sm text-gray-700">
            Thêm phụ đề (nếu có)
          </label>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Render Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>Lưu ý:</strong> Quá trình render có thể mất từ vài phút đến hơn 10 phút tùy thuộc vào 
          số lượng cảnh và chất lượng đã chọn. Vui lòng kiên nhẫn chờ đợi.
        </p>
      </div>

      {/* Render Button */}
      <button
        onClick={handleRender}
        disabled={loading}
        className="w-full py-3 px-6 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Đang render với Veo 3 Ultra...
          </>
        ) : (
          <>
            <Video className="w-5 h-5" />
            Bắt đầu Render
          </>
        )}
      </button>

      {loading && (
        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            Đang xử lý {selectedScenes.length} cảnh...
          </p>
          <p className="text-gray-500 text-xs mt-1">
            Veo 3 Ultra đang tạo video chất lượng cao
          </p>
        </div>
      )}
    </div>
  );
}
