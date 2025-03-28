import json
import os
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from config import NEWS_FILE, UPLOAD_DIR
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["Новости"])

# === Функции для работы с новостями ===
def load_news():
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_news(news_list):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)

# === Получить список новостей ===
@router.get("/")
async def get_news():
    logger.info("GET /news/ called")
    return load_news()

# === Добавить новость ===
@router.post("/", response_class=HTMLResponse)
async def add_news(text: str = Form(...), image: UploadFile = File(...)):
    logger.info("POST /news/ called")
    news_list = load_news()
    
    # Проверка на максимальное количество новостей (8)
    if len(news_list) >= 8:
        return HTMLResponse('<p class="text-red-600">Достигнут лимит в 8 новостей!</p>')

    news_id = len(news_list) + 1
    image_path = ""

    # Сохранение изображения
    ext = image.filename.split(".")[-1]
    image_path = f"news_{news_id}.{ext}"
    full_image_path = os.path.join(UPLOAD_DIR, image_path)
    with open(full_image_path, "wb") as f:
        f.write(await image.read())

    # Формируем объект новости
    news_item = {
        "id": news_id,
        "text": text,
        "image": f"/uploads/{image_path}"  # Путь для доступа через HTTP
    }
    
    news_list.insert(0, news_item)
    save_news(news_list)

    # Возвращаем HTML для HTMX
    html_content = f"""
        <div class="news-item" data-id="{news_item['id']}">
            <div>
                <p class="text-gray-700">{news_item['text']}</p>
                <img src="{news_item['image']}" alt="Новость" 
                     onerror="this.style.display='none'; this.nextSibling.style.display='block'">
                <span style="display:none; color:#666">Изображение не загрузилось</span>
            </div>
            <button class="bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition mt-2"
                    hx-delete="/news/{news_item['id']}" 
                    hx-target="closest .news-item" 
                    hx-swap="outerHTML"
                    hx-confirm="Вы уверены, что хотите удалить эту новость?">
                Удалить
            </button>
        </div>
    """
    return HTMLResponse(html_content)

# === Удалить новость ===
@router.delete("/{news_id}", response_class=HTMLResponse)
async def delete_news(news_id: int):
    logger.info(f"DELETE /news/{news_id} called")
    news_list = load_news()
    news_to_delete = next((n for n in news_list if n["id"] == news_id), None)
    if news_to_delete:
        news_list = [n for n in news_list if n["id"] != news_id]
        save_news(news_list)
        return HTMLResponse("")  # Возвращаем пустой HTML, чтобы элемент удалился из DOM
    return HTMLResponse('<p class="text-red-600">Новость не найдена!</p>')

# === Очистить все новости ===
@router.delete("/", response_class=HTMLResponse)
async def clear_news():
    logger.info("DELETE /news/ called")
    save_news([])
    return HTMLResponse("")  # Возвращаем пустой HTML, чтобы очистить список