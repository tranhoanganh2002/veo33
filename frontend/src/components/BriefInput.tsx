import { useState } from 'react';
import { Loader2, Sparkles } from 'lucide-react';
import { BriefInput as BriefInputType, Project } from '../types';
import { projectsApi } from '../api/projects';

interface Props {
  onProjectCreated: (project: Project) => void;
}

export default function BriefInput({ onProjectCreated }: Props) {
  const [formData, setFormData] = useState<BriefInputType>({
    title: '',
    brief: '',
    target_audience: '',
    duration: 30,
    tone: 'Professional',
    aspect_ratio: '16:9',
    style_references: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Create project
      const project = await projectsApi.create(formData);
      
      // Expand brief with Gemini
      const expandedProject = await projectsApi.expand(project.id);
      
      onProjectCreated(expandedProject);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Đã xảy ra lỗi. Vui lòng thử lại.');
      console.error('Error creating project:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'duration' ? parseFloat(value) : value,
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl mx-auto">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-6 h-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-800">
          Bước 1: Nhập ý tưởng của bạn
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Tiêu đề dự án <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            required
            value={formData.title}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="VD: Quảng cáo sản phẩm mới"
          />
        </div>

        {/* Brief */}
        <div>
          <label htmlFor="brief" className="block text-sm font-medium text-gray-700 mb-2">
            Mô tả ý tưởng <span className="text-red-500">*</span>
          </label>
          <textarea
            id="brief"
            name="brief"
            required
            rows={6}
            value={formData.brief}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Mô tả chi tiết ý tưởng video của bạn. VD: Tạo video giới thiệu sản phẩm điện thoại mới với phong cách hiện đại, năng động..."
            minLength={10}
          />
          <p className="mt-1 text-sm text-gray-500">
            Tối thiểu 10 ký tự. Mô tả càng chi tiết, kết quả càng tốt.
          </p>
        </div>

        {/* Target Audience */}
        <div>
          <label htmlFor="target_audience" className="block text-sm font-medium text-gray-700 mb-2">
            Đối tượng mục tiêu
          </label>
          <input
            type="text"
            id="target_audience"
            name="target_audience"
            value={formData.target_audience}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="VD: Giới trẻ 18-25 tuổi"
          />
        </div>

        {/* Duration */}
        <div>
          <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
            Thời lượng (giây): {formData.duration}s
          </label>
          <input
            type="range"
            id="duration"
            name="duration"
            min="10"
            max="300"
            step="5"
            value={formData.duration}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10s</span>
            <span>300s</span>
          </div>
        </div>

        {/* Tone */}
        <div>
          <label htmlFor="tone" className="block text-sm font-medium text-gray-700 mb-2">
            Giọng điệu
          </label>
          <select
            id="tone"
            name="tone"
            value={formData.tone}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="Professional">Chuyên nghiệp</option>
            <option value="Casual">Thân thiện</option>
            <option value="Energetic">Năng động</option>
            <option value="Elegant">Sang trọng</option>
            <option value="Playful">Vui tươi</option>
            <option value="Dramatic">Kịch tính</option>
          </select>
        </div>

        {/* Aspect Ratio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tỉ lệ khung hình
          </label>
          <div className="grid grid-cols-3 gap-4">
            {(['16:9', '9:16', '1:1'] as const).map((ratio) => (
              <button
                key={ratio}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, aspect_ratio: ratio }))}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition-colors ${
                  formData.aspect_ratio === ratio
                    ? 'border-purple-600 bg-purple-50 text-purple-700'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {ratio}
                <div className="text-xs text-gray-500 mt-1">
                  {ratio === '16:9' && 'Ngang'}
                  {ratio === '9:16' && 'Dọc'}
                  {ratio === '1:1' && 'Vuông'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-6 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Đang xử lý với Gemini AI...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Tạo kịch bản với AI
            </>
          )}
        </button>
      </form>
    </div>
  );
}
