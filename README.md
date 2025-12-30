# VEO3 Ultra + Gemini AI Video Generator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)

> Xây dựng tool tạo video AI tự động, kết hợp Veo 3 Ultra và Gemini để chuyển hóa ý tưởng thành video chất lượng cao trong vài phút.

## 🌟 Tính năng chính

### 1. **Prompt thông minh bởi Gemini**
- Tự động phân rã ý tưởng thành kịch bản đầy đủ với mô tả chi tiết từng cảnh
- Tối ưu prompt trước khi render để đảm bảo chất lượng
- Hỗ trợ tiếng Việt tự nhiên, tự động chuyển sang prompt kỹ thuật tiếng Anh
- Fallback mechanism khi API không khả dụng

### 2. **Chất lượng hình ảnh từ Veo 3 Ultra**
- Render video với độ trung thực cao
- Chuyển động mượt mà, tự nhiên
- Hỗ trợ nhiều tỉ lệ khung hình: 16:9, 9:16, 1:1
- Quality levels: draft/high/ultra

### 3. **Storyboard tự động**
- Phác thảo preview image cho từng cảnh
- Cho phép duyệt và điều chỉnh trước khi render
- Parallel processing với asyncio
- Chọn/bỏ chọn cảnh theo ý muốn

### 4. **Điều khiển phong cách**
- Tham chiếu hình ảnh mẫu (style references)
- Câu lệnh điện ảnh chi tiết (lens, focal length, shot type)
- Color palette customization
- Lock attributes để giữ consistency

## 🏗️ Kiến trúc hệ thống

### Tech Stack
- **Backend**: Python + FastAPI
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Database**: PostgreSQL + Redis
- **AI Services**: Google Gemini API + Veo 3 Ultra API

### Cấu trúc thư mục
```
veo33/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   ├── database.py                # SQLAlchemy setup
│   ├── models.py                  # Database models
│   ├── schemas.py                 # Pydantic schemas
│   ├── requirements.txt           # Dependencies
│   ├── services/
│   │   ├── gemini_service.py     # Gemini integration
│   │   ├── veo_service.py        # Veo 3 Ultra API
│   │   ├── storyboard_service.py # Storyboard generation
│   │   └── render_service.py     # Video rendering
│   └── alembic/                   # Database migrations
├── frontend/
│   └── src/
│       ├── App.tsx               # Main app
│       ├── api/                  # API client
│       └── components/           # React components
├── docker-compose.yml
└── setup.sh
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- API keys for Gemini and Veo 3 Ultra

### Installation

1. **Clone repository:**
```bash
git clone https://github.com/tranhoanganh2002/veo33.git
cd veo33
```

2. **Run setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Configure API keys:**
```bash
# Edit backend/.env
nano backend/.env

# Add your keys:
GEMINI_API_KEY=your_gemini_api_key_here
VEO_API_KEY=your_veo_api_key_here
```

4. **Restart services:**
```bash
docker-compose restart
```

5. **Access application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Workflow (4 bước)

#### Bước 1: Nhập ý tưởng
- Nhập tiêu đề và mô tả ý tưởng video
- Chọn thời lượng, giọng điệu, tỉ lệ khung hình
- AI sẽ tự động tạo kịch bản chi tiết

#### Bước 2: Xem storyboard
- Preview từng cảnh với hình ảnh minh họa
- Chọn/bỏ chọn cảnh theo ý muốn
- Xem prompt đã được tối ưu

#### Bước 3: Render video
- Chọn chất lượng (draft/high/ultra)
- Chọn định dạng (mp4/webm)
- Bắt đầu render với Veo 3 Ultra

#### Bước 4: Hoàn thành
- Xem video đã render
- Tải xuống hoặc chia sẻ

## 🔧 Development

### Manual Setup (without Docker)

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local

# Start dev server
npm run dev
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🎨 API Documentation

### Endpoints

**Projects Management:**
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Delete project

**Workflow Steps:**
- `POST /api/projects/{id}/expand` - Expand brief with Gemini
- `POST /api/projects/{id}/storyboard` - Generate storyboard
- `PUT /api/projects/{id}/storyboard` - Update selections
- `POST /api/projects/{id}/render` - Render video

Interactive API docs: http://localhost:8000/docs

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build

# Execute command in backend
docker-compose exec backend alembic upgrade head

# Access database
docker-compose exec postgres psql -U postgres -d veo3db
```

## 🔒 Security

- HTTPS enforced in production
- Environment variables for sensitive data
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via React escaping
- CORS configured properly
- Input validation on all endpoints

## 📊 Monitoring

Health checks available at:
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:5173`

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Docker Compose deployment
- AWS ECS/Fargate
- Google Cloud Run
- DigitalOcean App Platform

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style
- Backend: PEP 8, Black formatter
- Frontend: ESLint, Prettier
- Types: Full TypeScript coverage

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Google Gemini](https://ai.google.dev/) - AI prompt expansion
- [Veo 3 Ultra](https://deepmind.google/technologies/veo/) - Video generation
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS

## 📧 Support

- GitHub Issues: [Report bugs](https://github.com/tranhoanganh2002/veo33/issues)
- Email: support@veo3.ai

## 🗺️ Roadmap

- [x] Core video generation pipeline
- [x] Gemini integration
- [x] Storyboard preview
- [x] Docker setup
- [ ] Real Veo 3 Ultra API integration
- [ ] User authentication
- [ ] Video storage (S3/GCS)
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] API rate limiting
- [ ] WebSocket for real-time updates
- [ ] Template library
- [ ] AI voice-over generation

---

Built with ❤️ by [@tranhoanganh2002](https://github.com/tranhoanganh2002)
