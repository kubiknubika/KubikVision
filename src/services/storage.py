import boto3
from typing import BinaryIO
from src.core.config import settings

class S3Service:
    def __init__(self):
        # Подключаемся к MinIO как к S3
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name="us-east-1" # Для MinIO это формальность
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Создает бакет, если его нет"""
        try:
            self.client.head_bucket(Bucket=settings.S3_BUCKET)
        except Exception:
            self.client.create_bucket(Bucket=settings.S3_BUCKET)

    def upload_file(self, file_obj: BinaryIO, object_name: str, content_type: str = "image/jpeg"):
        """Загружает файл в S3"""
        self.client.upload_fileobj(
            file_obj,
            settings.S3_BUCKET,
            object_name,
            ExtraArgs={'ContentType': content_type}
        )

    def download_file(self, object_name: str) -> bytes:
        """Скачивает файл в память"""
        response = self.client.get_object(Bucket=settings.S3_BUCKET, Key=object_name)
        return response['Body'].read()

    def get_presigned_url(self, object_name: str) -> str:
        """Генерирует временную ссылку на скачивание"""
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET, 'Key': object_name},
            ExpiresIn=3600
        )