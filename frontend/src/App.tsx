import { useState } from 'react';
import { Project } from './types';
import BriefInput from './components/BriefInput';
import StoryboardPreview from './components/StoryboardPreview';
import VideoRenderer from './components/VideoRenderer';

function App() {
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);
  const [project, setProject] = useState<Project | null>(null);

  const handleProjectCreated = (newProject: Project) => {
    setProject(newProject);
    // Automatically move to step 2 when script is ready
    if (newProject.status === 'expanded') {
      setCurrentStep(2);
    }
  };

  const handleStoryboardReady = (updatedProject: Project) => {
    setProject(updatedProject);
    setCurrentStep(3);
  };

  const handleVideoReady = (updatedProject: Project) => {
    setProject(updatedProject);
    setCurrentStep(4);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            VEO3 Ultra + Gemini AI
          </h1>
          <p className="text-lg text-white/90">
            Tạo video chất lượng cao từ ý tưởng trong vài phút
          </p>
        </div>

        {/* Progress Steps */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-between">
            {[
              { num: 1, label: 'Nhập ý tưởng' },
              { num: 2, label: 'Xem storyboard' },
              { num: 3, label: 'Render video' },
              { num: 4, label: 'Hoàn thành' }
            ].map((step, idx) => (
              <div key={step.num} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-colors ${
                      currentStep >= step.num
                        ? 'bg-white text-purple-600'
                        : 'bg-white/20 text-white/60'
                    }`}
                  >
                    {step.num}
                  </div>
                  <span
                    className={`mt-2 text-sm ${
                      currentStep >= step.num
                        ? 'text-white font-semibold'
                        : 'text-white/60'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
                {idx < 3 && (
                  <div
                    className={`h-1 flex-1 mx-2 transition-colors ${
                      currentStep > step.num
                        ? 'bg-white'
                        : 'bg-white/20'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {currentStep === 1 && (
            <BriefInput onProjectCreated={handleProjectCreated} />
          )}
          {currentStep === 2 && project && (
            <StoryboardPreview
              project={project}
              onStoryboardReady={handleStoryboardReady}
              onBack={() => setCurrentStep(1)}
            />
          )}
          {currentStep === 3 && project && (
            <VideoRenderer
              project={project}
              onVideoReady={handleVideoReady}
              onBack={() => setCurrentStep(2)}
            />
          )}
          {currentStep === 4 && project && project.video_url && (
            <div className="bg-white rounded-lg shadow-xl p-8">
              <div className="text-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 mb-2">
                  🎉 Video đã hoàn thành!
                </h2>
                <p className="text-gray-600">
                  Video của bạn đã được tạo thành công
                </p>
              </div>
              
              <div className="aspect-video mb-6">
                <video
                  controls
                  className="w-full h-full rounded-lg"
                  src={project.video_url}
                  poster={project.thumbnail_url}
                >
                  Trình duyệt của bạn không hỗ trợ video.
                </video>
              </div>

              <div className="flex gap-4 justify-center">
                <a
                  href={project.video_url}
                  download
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Tải xuống
                </a>
                <button
                  onClick={() => {
                    setCurrentStep(1);
                    setProject(null);
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Tạo video mới
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-white/70 text-sm">
          <p>
            Built with ❤️ by{' '}
            <a
              href="https://github.com/tranhoanganh2002"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white hover:underline"
            >
              @tranhoanganh2002
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
