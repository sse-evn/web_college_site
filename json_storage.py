import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Union, Tuple

import config
import texts as txt

logger = logging.getLogger(__name__)

DEFAULT_DATA_STRUCTURE: Dict[str, Any] = {
    "admins": [],
    "allowed_teachers": [],
    "requests": [],
    "next_request_id": 1
}

def load_data() -> Dict[str, Any]:
    if not os.path.exists(config.DATA_FILE):
        return DEFAULT_DATA_STRUCTURE.copy()

    try:
        with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, default_value in DEFAULT_DATA_STRUCTURE.items():
                if key not in data:
                    data[key] = default_value
            for req in data.get("requests", []):
                 if "rating" not in req:
                      req["rating"] = None
                 if "taken_by_id" not in req:
                      req["taken_by_id"] = None
                 if "taken_by_username" not in req:
                      req["taken_by_username"] = None
                 if "taken_by_fullname" not in req:
                      req["taken_by_fullname"] = None
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from '{config.DATA_FILE}': {e}. Using default structure.")
        return DEFAULT_DATA_STRUCTURE.copy()
    except Exception as e:
        logger.error(f"Error loading data from '{config.DATA_FILE}': {e}. Using default structure.")
        return DEFAULT_DATA_STRUCTURE.copy()

def save_data(data: Dict[str, Any]):
    try:
        temp_file = config.DATA_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, config.DATA_FILE)
    except Exception as e:
        logger.error(f"Error saving data to '{config.DATA_FILE}': {e}")

def init_storage():
    data = load_data()
    for admin_id in config.INITIAL_ADMIN_IDS:
        if admin_id not in data.setdefault("admins", []):
            data["admins"].append(admin_id)
    for teacher_id in config.INITIAL_ALLOWED_TEACHER_IDS:
         if teacher_id not in data.setdefault("allowed_teachers", []):
              data["allowed_teachers"].append(teacher_id)
    save_data(data)

def is_admin(user_id: int) -> bool:
    data = load_data()
    return user_id in data.get("admins", [])

def add_admin_user(user_id: int) -> bool:
    data = load_data()
    if user_id in data.get("admins", []):
        return False
    data.setdefault("admins", []).append(user_id)
    save_data(data)
    return True

def remove_admin_user(user_id: int) -> Tuple[bool, Union[str, None]]:
    data = load_data()
    admins = data.get("admins", [])
    if user_id not in admins:
        return False, f"Пользователь с ID {user_id} не найден в списке администраторов."
    if len(admins) == 1 and user_id in admins:
        return False, "Нельзя удалить последнего администратора!"
    data["admins"].remove(user_id)
    save_data(data)
    return True, None

def get_admins() -> List[int]:
    data = load_data()
    return data.get("admins", [])

def is_teacher_allowed(user_id: int) -> bool:
    if is_admin(user_id):
        return True
    data = load_data()
    return user_id in data.get("allowed_teachers", [])

def add_allowed_teacher(user_id: int) -> bool:
    data = load_data()
    if user_id in data.get("allowed_teachers", []):
        return False
    if user_id in data.get("admins", []):
         return False
    data.setdefault("allowed_teachers", []).append(user_id)
    save_data(data)
    return True

def remove_allowed_teacher(user_id: int) -> bool:
    data = load_data()
    allowed_teachers = data.get("allowed_teachers", [])
    if user_id not in allowed_teachers:
        return False
    data["allowed_teachers"].remove(user_id)
    save_data(data)
    return True

def get_allowed_teachers() -> List[int]:
    data = load_data()
    return data.get("allowed_teachers", [])

def add_request(teacher_id: int, teacher_username: Union[str, None], teacher_fullname: Union[str, None],
                request_type: str, description: str, location: str, contact_name: str) -> int:
    data = load_data()
    request_id = data.get("next_request_id", 1)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_request: Dict[str, Any] = {
        "id": request_id,
        "teacher_id": teacher_id,
        "teacher_username": teacher_username,
        "teacher_fullname": teacher_fullname,
        "request_type": request_type,
        "description": description,
        "location": location,
        "contact_name": contact_name,
        "status": "open",
        "created_at": created_at,
        "completed_at": None,
        "rating": None,
        "taken_by_id": None,
        "taken_by_username": None,
        "taken_by_fullname": None
    }
    data.setdefault("requests", []).append(new_request)
    data["next_request_id"] = request_id + 1
    save_data(data)
    return request_id

def get_requests_by_status(status: str = 'open') -> List[Dict[str, Any]]:
    data = load_data()
    filtered_requests: List[Dict[str, Any]] = []
    for req in data.get("requests", []):
        if req.get("status") == status:
             filtered_requests.append({
                 "id": req.get("id"),
                 "contact_name": req.get("contact_name"),
                 "request_type": req.get("request_type"),
                 "location": req.get("location"),
                 "created_at": req.get("created_at"),
                 "completed_at": req.get("completed_at"),
                 "rating": req.get("rating"),
                 "taken_by_id": req.get("taken_by_id"),
                 "taken_by_username": req.get("taken_by_username"),
                 "taken_by_fullname": req.get("taken_by_fullname"),
             })

    filtered_requests.sort(key=lambda x: x.get("created_at", ""))
    return filtered_requests

def get_user_active_requests(user_id: int) -> List[Dict[str, Any]]:
    data = load_data()
    user_requests: List[Dict[str, Any]] = []
    for req in data.get("requests", []):
        if req.get("teacher_id") == user_id and req.get("status") in ("open", "in_progress"):
             user_requests.append({
                 "id": req.get("id"),
                 "request_type": req.get("request_type"),
                 "location": req.get("location"),
                 "status": req.get("status"),
                 "created_at": req.get("created_at"),
                 "taken_by_id": req.get("taken_by_id"),
                 "taken_by_username": req.get("taken_by_username"),
                 "taken_by_fullname": req.get("taken_by_fullname"),
             })
    user_requests.sort(key=lambda x: x.get("created_at", ""))
    return user_requests


def get_request_details(request_id: int) -> Dict[str, Any] | None:
    data = load_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            return req
    return None

def update_request_status(request_id: int, status: str, admin_user_id: int | None = None, admin_username: str | None = None, admin_fullname: str | None = None):
    data = load_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            req["status"] = status
            if status == 'completed':
                req["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                req["completed_at"] = None
                req["rating"] = None # Сбрасываем рейтинг, если статус не завершен

            if status == 'in_progress':
                req["taken_by_id"] = admin_user_id
                req["taken_by_username"] = admin_username
                req["taken_by_fullname"] = admin_fullname
            elif status in ('open', 'cancelled'): # Если вернули в открытые или отменили, сбрасываем "взято кем"
                req["taken_by_id"] = None
                req["taken_by_username"] = None
                req["taken_by_fullname"] = None
            # Если статус стал 'completed', оставляем информацию о том, кто взял в работу

            save_data(data)
            return

def update_request_rating(request_id: int, rating: int) -> bool:
    data = load_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            if req.get("status") == 'completed' and req.get("rating") is None:
                 req["rating"] = rating
                 save_data(data)
                 return True
            return False
    return False

def count_active_requests(user_id: int) -> int:
    data = load_data()
    count = 0
    for req in data.get("requests", []):
        if req.get("teacher_id") == user_id and req.get("status") in ("open", "in_progress"):
            count += 1
    return count

def get_all_requests() -> List[Dict[str, Any]]:
    data = load_data()
    all_requests = data.get("requests", [])
    all_requests.sort(key=lambda x: x.get("created_at", ""))
    return all_requests

def clear_all_requests() -> int:
    data = load_data()
    requests_list = data.get("requests", [])
    count_before = len(requests_list)
    data["requests"] = []
    data["next_request_id"] = 1
    save_data(data)
    return count_before

def get_all_requests_formatted() -> str:
    requests = get_all_requests()

    if not requests:
        return txt.ADMIN_EXPORT_HISTORY_NO_DATA

    formatted_text = txt.ADMIN_ALL_REQUESTS_LIST_TEMPLATE

    for req in requests:
         req_id = req.get("id", "N/A")
         teacher_id = req.get("teacher_id", "N/A")
         teacher_username = req.get("teacher_username")
         teacher_fullname = req.get("teacher_fullname", "Не указано")
         req_type = req.get("request_type", "Неизвестно")
         description = req.get("description", "Нет описания")
         location = req.get("location", "Не указано")
         status = req.get("status", "N/A")
         created_at = req.get("created_at", "N/A")
         completed_at = req.get("completed_at")
         rating = req.get("rating")
         taken_by_id = req.get("taken_by_id")
         taken_by_username = req.get("taken_by_username")
         taken_by_fullname = req.get("taken_by_fullname", "Неизвестно")

         username_mention = f', @{teacher_username}' if teacher_username else ''
         completed_at_formatted = completed_at if completed_at else 'еще нет'
         status_ru = txt.STATUS_MAP_RU.get(status, status)

         rating_info = f"Оценка: {rating}/10" if rating is not None else "Оценка: нет"

         taken_by_info = ""
         if taken_by_id:
              taken_by_username_mention = f', @{taken_by_username}' if taken_by_username else ''
              taken_by_info = txt.ADMIN_TAKEN_BY_TEMPLATE.format(
                   admin_fullname=taken_by_fullname,
                   admin_id=taken_by_id,
                   username_mention=taken_by_username_mention.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
              )


         history_text = txt.ADMIN_HISTORY_ITEM_TEMPLATE.format(
             request_id=req_id,
             request_type=req_type,
             location=location,
             teacher_fullname=teacher_fullname,
             teacher_id=teacher_id,
             username_mention=username_mention.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>'),
             status_ru=status_ru,
             created_at=created_at,
             completed_at_formatted=completed_at_formatted
         )
         formatted_text += history_text + taken_by_info + f"{rating_info}\n---\n"


    return formatted_text.strip()
