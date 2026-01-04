👁️ KubikVision: Distributed AI Computer Vision System
Enterprise-grade distributed system for real-time object detection. Built with Python, FastAPI, Celery, Redis, and YOLO12.

PythonFastAPICeleryRedisDocker

🚀 Overview
KubikVision is a microservice-based architecture designed to decouple high-load AI processing from the web presentation layer. It implements the Producer-Consumer pattern to ensure scalability and responsiveness.

The system allows users to upload images, which are asynchronously processed by AI workers to detect objects, calculate confidence levels, and generate analytics.

🛠️ Key Features (Senior Level)
⚡ Distributed Task Processing: Web API (FastAPI) never blocks. Heavy AI tasks are offloaded to Celery workers via Redis.
🤖 Auto-Healing AI Engine: The system features a Model Discovery Mechanism. On startup, it automatically checks for the latest available SOTA model (YOLO12/11/...) and falls back to stable versions if bleeding-edge models are unavailable.
🛡️ Secure S3 Proxy: Direct access to the Object Storage (MinIO) is restricted. Files are streamed through a secure API endpoint.
📊 Real-time Dashboard: A responsive JS frontend that polls task status and visualizes AI analytics (Confidence scores, inference time).
🐳 Container Orchestration: Full infrastructure (Web, Worker, Redis, MinIO) deployed via Docker Compose.
🏗️ Architecture
mermaid

graph LR
    User[User / Frontend] -- Upload --> API[FastAPI Web]
    API -- Save File --> S3[(MinIO Storage)]
    API -- Push Task --> Redis[(Redis Broker)]
    Redis -- Pop Task --> Worker[Celery Worker]
    Worker -- Load Image --> S3
    Worker -- Process (YOLO) --> AI[AI Engine]
    AI -- Metadata & Result --> Worker
    Worker -- Save Result --> S3
    Worker -- Update Status --> Redis
⚙️ Tech Stack
Backend: Python 3.11, FastAPI, Pydantic v2
Asynchronous Tasks: Celery 5.3
Message Broker: Redis 7
Storage: MinIO (S3 Compatible)
Computer Vision: Ultralytics YOLO12 (Attention-based architecture)
Frontend: HTML5, CSS3 (Glassmorphism), Vanilla JS
🚀 How to Run
Clone the repository:

Bash

git clone https://github.com/your-username/KubikVision.git
cd KubikVision
Start Infrastructure:

Bash

docker-compose up --build
Access:

Web Dashboard: http://localhost:8000
Swagger API: http://localhost:8000/docs
MinIO Console: http://localhost:9001