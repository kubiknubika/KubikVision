import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.core.config import settings
from src.worker.tasks import process_image_task
from src.services.storage import S3Service
from celery.result import AsyncResult
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title=settings.PROJECT_NAME)

# Монтируем папку static, чтобы браузер мог получать JS/CSS (если будут)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("src/static/index.html")

@app.post("/upload", status_code=202)
async def upload_image(file: UploadFile = File(...)):
    """Загрузка изображения для обработки"""
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG images allowed")

    # Инициализируем S3 (в реальном проекте - через Depends)
    storage = S3Service()

    # Генерируем уникальное имя
    file_ext = file.filename.split(".")[-1]
    file_id = str(uuid.uuid4())
    file_path = f"raw/{file_id}.{file_ext}"

    # Загружаем
    storage.upload_file(file.file, file_path, file.content_type)

    # Ставим задачу
    task = process_image_task.delay(file_path)

    return {
        "task_id": task.id,
        "message": "File uploaded and queued for processing"
    }

@app.get("/results/{task_id}")
async def get_result(task_id: str):
    """Проверка статуса задачи"""
    task_result = AsyncResult(task_id)
    
    if task_result.ready():
        if task_result.successful():
            return task_result.result
        else:
            return {"status": "failed", "error": str(task_result.result)}
    
    return {"status": "processing"}

@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """
    Прокси-метод. 
    Скачивает файл из MinIO (внутри сети Docker) и отдает пользователю.
    """
    storage = S3Service()
    try:
        # Скачиваем файл в память (в продакшене лучше использовать streaming response)
        file_content = storage.download_file(file_path)
        
        # Определяем тип контента (упрощенно)
        media_type = "image/jpeg" if file_path.endswith((".jpg", ".jpeg")) else "image/png"
        
        return Response(content=file_content, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")