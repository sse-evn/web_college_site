import os

# Путь к файлу с новостями
NEWS_FILE = "news.json"

# Директория для загрузки изображений
UPLOAD_DIR = "uploads"

# Создаём директорию, если её нет
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)