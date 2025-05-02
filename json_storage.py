import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Union, Tuple

import config

logger = logging.getLogger(__name__)

DEFAULT_DATA_STRUCTURE: Dict[str, Any] = {
    "admins": [],
    "allowed_teachers": [],
    "requests": [],
    "next_request_id": 1
}

def load_data() -> Dict[str, Any]:
    """Загружает данные из JSON файла."""
    if not os.path.exists(config.DATA_FILE):
        logger.info(f"Data file '{config.DATA_FILE}' not found. Initializing with default structure.")
        return DEFAULT_DATA_STRUCTURE.copy()

    try:
        with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, default_value in DEFAULT_DATA_STRUCTURE.items():
                if key not in data:
                    data[key] = default_value
                    logger.warning(f"Added missing key '{key}' to data structure during load.")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from '{config.DATA_FILE}': {e}. Using default structure.")
        return DEFAULT_DATA_STRUCTURE.copy()
    except Exception as e:
        logger.error(f"Error loading data from '{config.DATA_FILE}': {e}. Using default structure.")
        return DEFAULT_DATA_STRUCTURE.copy()


def save_data(data: Dict[str, Any]):
    """Сохраняет данные в JSON файл."""
    try:
        temp_file = config.DATA_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, config.DATA_FILE)
        logger.debug(f"Data successfully saved to '{config.DATA_FILE}'")
    except Exception as e:
        logger.error(f"Error saving data to '{config.DATA_FILE}': {e}")


def init_storage():
    """Инициализация хранилища: загрузка данных и добавление начальных админов/учителей."""
    data = load_data()

    for admin_id in config.INITIAL_ADMIN_IDS:
        if admin_id not in data.setdefault("admins", []):
            data["admins"].append(admin_id)
            logger.info(f"Added initial admin {admin_id} to storage.")

    for teacher_id in config.INITIAL_ALLOWED_TEACHER_IDS:
         if teacher_id not in data.setdefault("allowed_teachers", []):
              data["allowed_teachers"].append(teacher_id)
              logger.info(f"Added initial allowed teacher {teacher_id} to storage.")

    save_data(data)


# --- Функции для работы с данными ---

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    data = load_data()
    return user_id in data.get("admins", [])

def add_admin_user(user_id: int) -> bool:
    """Добавляет пользователя в список администраторов. Возвращает True при успехе, False если уже админ."""
    data = load_data()
    if user_id in data.get("admins", []):
        return False
    data.setdefault("admins", []).append(user_id)
    save_data(data)
    logger.info(f"Added admin user: {user_id}")
    return True

def remove_admin_user(user_id: int) -> Tuple[bool, Union[str, None]]:
    """Удаляет пользователя из списка администраторов. Возвращает (успех, сообщение об ошибке)."""
    data = load_data()
    admins = data.get("admins", [])

    if user_id not in admins:
        return False, f"Пользователь с ID {user_id} не найден в списке администраторов."

    if len(admins) == 1 and user_id in admins:
        return False, "Нельзя удалить последнего администратора!"

    data["admins"].remove(user_id)
    save_data(data)
    logger.info(f"Removed admin user: {user_id}")
    return True, None

def get_admins() -> List[int]:
    """Возвращает список user_id всех администраторов."""
    data = load_data()
    return data.get("admins", [])

def is_teacher_allowed(user_id: int) -> bool:
    """Проверяет, разрешено ли учителю создавать заявки. Админам разрешено всегда."""
    if is_admin(user_id):
        return True
    data = load_data()
    return user_id in data.get("allowed_teachers", [])

def add_allowed_teacher(user_id: int) -> bool:
    """Добавляет пользователя в список разрешенных учителей. Возвращает True при успехе, False если уже в списке или админ."""
    data = load_data()
    if user_id in data.get("allowed_teachers", []) or user_id in data.get("admins", []):
        return False
    data.setdefault("allowed_teachers", []).append(user_id)
    save_data(data)
    logger.info(f"Added allowed teacher: {user_id}")
    return True

def remove_allowed_teacher(user_id: int) -> bool:
    """Удаляет пользователя из списка разрешенных учителей. Возвращает True при успехе, False если не найден."""
    data = load_data()
    allowed_teachers = data.get("allowed_teachers", [])

    if user_id not in allowed_teachers:
        return False

    data["allowed_teachers"].remove(user_id)
    save_data(data)
    logger.info(f"Removed allowed teacher: {user_id}")
    return True

def get_allowed_teachers() -> List[int]:
    """Возвращает список user_id разрешенных учителей."""
    data = load_data()
    return data.get("allowed_teachers", [])


def add_request(teacher_id: int, teacher_username: Union[str, None], teacher_fullname: Union[str, None],
                request_type: str, description: str, location: str, contact_name: str) -> int:
    """Добавляет новую заявку в хранилище."""
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
        "completed_at": None
    }
    data.setdefault("requests", []).append(new_request)
    data["next_request_id"] = request_id + 1
    save_data(data)
    logger.info(f"Added new request: {request_id}")
    return request_id


def get_requests_by_status(status: str = 'open') -> List[Dict[str, Any]]:
    """Возвращает список заявок (словарей) по заданному статусу."""
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
                 # Добавляем completed_at для завершенных, хотя в списке оно может не отображаться
                 "completed_at": req.get("completed_at")
             })

    filtered_requests.sort(key=lambda x: x.get("created_at", ""))

    return filtered_requests

def get_request_details(request_id: int) -> Dict[str, Any] | None:
    """Возвращает полный словарь данных заявки по ее ID."""
    data = load_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            return req
    return None


def update_request_status(request_id: int, status: str):
    """Обновляет статус заявки по ее ID."""
    data = load_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            req["status"] = status
            if status == 'completed':
                req["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                req["completed_at"] = None
            save_data(data)
            logger.info(f"Updated request {request_id} status to: {status}")
            return

    logger.warning(f"Attempted to update status for non-existent request ID: {request_id}")


def count_active_requests(user_id: int) -> int:
    """Считает количество открытых ('open') или в работе ('in_progress') заявок для заданного пользователя."""
    data = load_data()
    count = 0
    for req in data.get("requests", []):
        if req.get("teacher_id") == user_id and req.get("status") in ("open", "in_progress"):
            count += 1
    return count


def get_all_requests() -> List[Dict[str, Any]]:
    """Возвращает список всех заявок (словарей), отсортированных по дате создания."""
    data = load_data()
    all_requests = data.get("requests", [])
    all_requests.sort(key=lambda x: x.get("created_at", ""))
    return all_requests
