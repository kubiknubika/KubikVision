# Используем легкий образ, но с возможностью компиляции
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# ВАЖНО: Устанавливаем системные зависимости для OpenCV (cv2)
# ВАЖНО: Устанавливаем системные зависимости для OpenCV (cv2)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Управление зависимостями
# Копируем только requirements сначала (для кэширования слоев Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Переменная окружения, чтобы Python не буферизировал вывод (видим логи сразу)
ENV PYTHONUNBUFFERED=1