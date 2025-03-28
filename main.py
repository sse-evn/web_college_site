from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routers.news import router as news_router
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Создаём директорию uploads, если она не существует
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.40.0.51:8000", "http://10.40.0.51:3000"],  # Разрешаем оба источника
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача статических файлов (для изображений)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Подключаем маршруты новостей
app.include_router(news_router)

# Главная страница (админ-панель)
@app.get("/", response_class=HTMLResponse)
async def admin_panel():
    logger.info("Accessed admin panel")
    with open("views/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Публичная лента
@app.get("/index", response_class=HTMLResponse)
async def public_feed():
    logger.info("Accessed public feed")
    with open("views/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)