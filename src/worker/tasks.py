from celery import Celery
from src.core.config import settings
from src.services.storage import S3Service
from src.services.vision import VisionService
import io

celery = Celery(
    "kubik_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Кешируем сервисы, чтобы не загружать модель каждый раз
vision_service = None 
storage_service = None

def get_services():
    global vision_service, storage_service
    if not vision_service:
        vision_service = VisionService()
    if not storage_service:
        storage_service = S3Service()
    return vision_service, storage_service

@celery.task(name="process_image_task", bind=True)
def process_image_task(self, file_path: str):
    v_service, s_service = get_services()

    # 1. Скачиваем
    image_data = s_service.download_file(file_path)

    # 2. Обрабатываем
    result_data = v_service.process_image(image_data)
    
    processed_bytes = result_data["image_bytes"]
    metadata = result_data["metadata"]
    inference_time = result_data["inference_time"]
    ai_model_name = result_data.get("ai_model", "Unknown")

    # 3. Генерируем путь для сохранения (ВОТ ЭТУ СТРОКУ МЫ ЗАБЫЛИ)
    processed_path = f"processed/{file_path.split('/')[-1]}"
    
    # 4. Загружаем результат
    s_service.upload_file(
        io.BytesIO(processed_bytes),
        processed_path,
        content_type="image/jpeg"
    )

    # 5. Возвращаем результат
    return {
        "status": "completed",
        "original_url": f"/files/{file_path}",
        "processed_url": f"/files/{processed_path}",
        "analytics": {
            "objects": metadata,
            "total_found": len(metadata),
            "time_taken": inference_time,
            "model_version": ai_model_name
        }
    }