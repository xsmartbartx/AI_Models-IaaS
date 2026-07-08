# AI Influencer Factory (Zero-Budget Edition)

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Platform for generating realistic virtual AI influencers and automating content creation for social media — using entirely free and open-source software.

## Features

- **Character Management** — Define AI influencers with detailed personas (name, age, appearance, style, hobbies)
- **Image Generation** — Produce consistent, high-quality photos via ComfyUI + FLUX/SDXL
- **Video Generation** — Create 5–10 second video clips with Wan 2.1, Hunyuan Video, or CogVideoX
- **Content Library** — Browse and organize generated images and videos by character/category
- **AI Captioning** — Auto-generate captions and hashtags via Ollama (Qwen/Llama 3)
- **Post Scheduling** — Plan and queue posts for social media platforms
- **GPU-Accelerated** — ComfyUI and Ollama run directly on your local GPU (optional profile)

## Architecture

```
Frontend (Next.js + TypeScript + TailwindCSS + Shadcn UI)
    │
    ▼
Backend API (FastAPI + async PostgreSQL)
    │
 ┌──┼────────────┐
 ▼  ▼            ▼
AI  Media        Scheduler (Celery + Redis)
    │
 ┌──┼───────────────┐
 ▼  ▼               ▼
PostgreSQL  Local Storage  MinIO (optional)
```

```
AI Services:
  ComfyUI (image generation) ─── port 8188
  Ollama (LLM chat/captions) ─── port 11434
```

## Quick Start

### Prerequisites

- Docker + Docker Compose
- **GPU mode**: NVIDIA GPU + nvidia-container-toolkit (optional, for ComfyUI + Ollama)

### 1. Clone & Configure

```bash
git clone https://github.com/xsmartbartx/AI_Models-IaaS.git
 
cd AI_Models-IaaS
cp .env.example .env   # or edit .env directly
```

### 2. Start (CPU-only mode, no AI generation)

```bash
docker compose up -d
```

Services available at:
| Service | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### 3. Start with GPU (generation enabled)

```bash
docker compose --profile gpu up -d
```

Additional GPU services:
| Service | URL |
|----------|-----|
| ComfyUI | http://localhost:8188 |
| Ollama | http://localhost:11434 |

### 4. Pull LLM model for captions

```bash
docker compose exec ollama ollama pull qwen2.5:7b
```

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | RTX 3060 12GB | RTX 4090 |
| RAM | 32 GB | 64 GB |
| Storage | 1 TB SSD | 2 TB SSD |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (characters, images, videos, posts)
│   │   ├── core/         # Settings, database engine
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # ComfyUI + Ollama integration layer
│   │   └── tasks/        # Celery async tasks (image/video gen, publishing)
│   ├── alembic/          # DB migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages (dashboard, characters, images, videos)
│   │   ├── components/   # UI components (shadcn) + sidebar
│   │   └── lib/          # API client + utilities
│   ├── Dockerfile
│   └── package.json
├── comfyui/              # ComfyUI model/custom_nodes mounts
├── scripts/              # Utility scripts
├── docker-compose.yml
├── .env
└── README.md
```

## API Endpoints

### Characters
- `GET    /api/v1/characters/` — List all characters
- `POST   /api/v1/characters/` — Create character
- `GET    /api/v1/characters/{id}` — Get character
- `PATCH  /api/v1/characters/{id}` — Update character
- `DELETE /api/v1/characters/{id}` — Delete character
- `POST   /api/v1/characters/{id}/activate` — Activate character for generation

### Images
- `GET    /api/v1/images/` — List images
- `POST   /api/v1/images/generate` — Queue image generation
- `POST   /api/v1/images/generate/batch` — Batch generate
- `DELETE /api/v1/images/{id}` — Delete image

### Videos
- `GET    /api/v1/videos/` — List videos
- `POST   /api/v1/videos/generate` — Queue video generation
- `DELETE /api/v1/videos/{id}` — Delete video

### Posts
- `GET    /api/v1/posts/` — List posts
- `POST   /api/v1/posts/` — Create post
- `POST   /api/v1/posts/generate-caption` — AI caption generation
- `POST   /api/v1/posts/{id}/approve` — Approve for publishing
- `POST   /api/v1/posts/{id}/publish` — Publish now
- `POST   /api/v1/posts/{id}/schedule` — Schedule for later

## Technology Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Shadcn UI (Button, Input, Card, Textarea, Label)

### Backend
- FastAPI (async)
- SQLAlchemy 2.0 (async PostgreSQL)
- Celery + Redis (task queue)
- Alembic (migrations)

### AI Layer
- ComfyUI (FLUX Dev / SDXL / Juggernaut XL)
- Ollama (Qwen 2.5 / Llama 3)
- Wan 2.1 / Hunyuan Video / CogVideoX (video)

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Roadmap

### Phase 1 ✅
- Character creation & management
- Image generation (ComfyUI + FLUX/SDXL)
- Single character workflow
- Basic content library

### Phase 2 (in progress)
- Video generation (image-to-video)
- Multi-character support
- AI captioning with Ollama
- Post scheduling

### Phase 3
- Social media platform integrations
- Analytics dashboard
- Automated publishing engine

### Phase 4
- Multi-tenant SaaS
- Marketplace for AI characters
- Advanced analytics & optimization

## License

MIT — see [LICENSE](LICENSE) file.