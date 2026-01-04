import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.model_name = "unknown" # Дефолтное значение
        self.model = self._load_best_available_model()

    def _load_best_available_model(self) -> YOLO:
        """
        Пытается загрузить самую новую модель из списка.
        Если модели нет - пробует следующую.
        """
        candidates = [
            "yolo26n.pt", # Из будущего (упадет, и это нормально)
            "yolo13n.pt", 
            "yolo12n.pt", 
            "yolo11n.pt", # Реальная SOTA (загрузится эта)
            "yolov8n.pt"  # Классика (резерв)
        ]

        for model_name in candidates:
            try:
                logger.info(f"Checking availability of AI model: {model_name}...")
                model = YOLO(model_name)
                
                # Тестовый прогон (проверка весов)
                dummy = np.zeros((64, 64, 3), dtype=np.uint8)
                model(dummy, verbose=False)
                
                logger.info(f"✅ SUCCESS: Loaded {model_name}")
                self.model_name = model_name
                return model
            except Exception:
                # Если файл не найден - молча идем дальше
                continue

        # Если вообще ничего не нашли - берем то, что точно есть в библиотеке
        logger.warning("⚠️ All bleeding-edge models failed. Loading default fallback.")
        self.model_name = "yolov8n.pt"
        return YOLO("yolov8n.pt")

    def process_image(self, image_bytes: bytes) -> dict:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        start_time = time.time()
        results = self.model(img)
        end_time = time.time()

        detections = []
        result = results[0]
        
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])
            
            detections.append({
                "label": class_name,
                "confidence": round(confidence, 2)
            })

        plotted_img = result.plot()
        _, encoded_img = cv2.imencode('.jpg', plotted_img)

        return {
            "image_bytes": encoded_img.tobytes(),
            "metadata": detections,
            "inference_time": round(end_time - start_time, 3),
            "ai_model": self.model_name
        }