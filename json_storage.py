import json
import os
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

import config
from utils import format_timestamp_for_display

logger = logging.getLogger(__name__)

DEFAULT_DATA_STRUCTURE: Dict[str, Any] = {
    "admins": [],
    "allowed_teachers": [],
    "support_staff": [],
    "requests": []
}

REQUEST_STATUSES = ['open', 'in_progress', 'completed', 'cancelled']

_storage_data: Dict[str, Any] = {}
_lock = False

def load_data() -> Dict[str, Any]:
    global _storage_data
    if not os.path.exists(config.DATA_FILE):
        logger.warning(f"Data file not found at {config.DATA_FILE}. Initializing empty structure.")
        _storage_data = DEFAULT_DATA_STRUCTURE.copy()
        save_data(_storage_data)
        return _storage_data

    try:
        with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, default_value in DEFAULT_DATA_STRUCTURE.items():
                if key not in data:
                    data[key] = default_value
                    logger.info(f"Added missing key '{key}' to data structure.")

            for request in data.get('requests', []):
                if 'taken_by_id' not in request:
                    request['taken_by_id'] = None
                if 'taken_by_username' not in request:
                    request['taken_by_username'] = None
                if 'taken_by_fullname' not in request:
                    request['taken_by_fullname'] = None
                if 'rating' not in request:
                    request['rating'] = None


            _storage_data = data
            logger.info(f"Data loaded successfully from {config.DATA_FILE}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {config.DATA_FILE}: {e}. Data might be corrupted.")
        _storage_data = DEFAULT_DATA_STRUCTURE.copy()
    except Exception as e:
        logger.error(f"An error occurred while loading data from {config.DATA_FILE}: {e}")
        _storage_data = DEFAULT_DATA_STRUCTURE.copy()

    return _storage_data

def save_data(data: Dict[str, Any]) -> None:
    global _lock
    if _lock:
        logger.warning("Attempted to save data while lock is active. Skipping save.")
        return

    _lock = True
    temp_filepath = f"{config.DATA_FILE}.tmp"
    try:
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_filepath, config.DATA_FILE)
        logger.debug(f"Data saved successfully to {config.DATA_FILE}")
    except Exception as e:
        logger.error(f"Error saving data to {config.DATA_FILE}: {e}")
    finally:
        _lock = False
        if os.path.exists(temp_filepath):
             try: os.remove(temp_filepath)
             except OSError: pass


def get_data() -> Dict[str, Any]:
    global _storage_data
    if not _storage_data:
        load_data()
    return _storage_data

def init_storage() -> None:
    data = get_data()

    for admin_id in config.INITIAL_ADMIN_IDS:
        if admin_id not in data.get("admins", []):
            data["admins"].append(admin_id)
            logger.info(f"Added initial admin: {admin_id}")

    for teacher_id in config.INITIAL_ALLOWED_TEACHER_IDS:
        if teacher_id not in data.get("allowed_teachers", []):
            data["allowed_teachers"].append(teacher_id)
            logger.info(f"Added initial allowed teacher: {teacher_id}")

    # Добавляем начальных эникейщиков из config.py
    # Убедитесь, что в config.py есть INITIAL_SUPPORT_STAFF_IDS
    if hasattr(config, 'INITIAL_SUPPORT_STAFF_IDS'):
        for support_staff_id in config.INITIAL_SUPPORT_STAFF_IDS:
            if support_staff_id not in data.get("support_staff", []):
                data["support_staff"].append(support_staff_id)
                logger.info(f"Added initial support staff: {support_staff_id}")


    save_data(data)

def is_admin(user_id: int) -> bool:
    return user_id in get_data().get("admins", [])

def is_teacher_allowed(user_id: int) -> bool:
    return user_id in get_data().get("allowed_teachers", []) or is_admin(user_id)

def is_support_staff(user_id: int) -> bool:
    return user_id in get_data().get("support_staff", [])

def get_admins() -> List[int]:
    return get_data().get("admins", [])

def add_admin_user(user_id: int) -> bool:
    data = get_data()
    if user_id not in data.get("admins", []):
        data["admins"].append(user_id)
        save_data(data)
        logger.info(f"User {user_id} added as admin.")
        return True
    logger.info(f"User {user_id} is already an admin.")
    return False

def remove_admin_user(user_id: int) -> Tuple[bool, str | None]:
    data = get_data()
    admins = data.get("admins", [])
    if user_id not in admins:
        logger.warning(f"Attempted to remove non-existent admin: {user_id}")
        return False, "Пользователь не найден в списке администраторов." # Убрал форматирование текста здесь
    if len(admins) <= 1:
        logger.warning(f"Attempted to remove the last admin: {user_id}")
        return False, "Нельзя удалить последнего администратора!"

    data["admins"].remove(user_id)
    save_data(data)
    logger.info(f"User {user_id} removed from admins.")
    return True, None

def get_allowed_teachers() -> List[int]:
    data = get_data()
    allowed_teachers = set(data.get("allowed_teachers", []))
    admins = set(data.get("admins", []))
    return sorted(list(allowed_teachers.union(admins)))

def add_allowed_teacher(user_id: int) -> bool:
    data = get_data()
    if user_id not in data.get("allowed_teachers", []) and user_id not in data.get("admins", []) and user_id not in data.get("support_staff", []):
        data["allowed_teachers"].append(user_id)
        save_data(data)
        logger.info(f"User {user_id} added as allowed teacher.")
        return True
    logger.info(f"User {user_id} is already allowed teacher or admin or support staff.")
    return False


def remove_allowed_teacher(user_id: int) -> bool:
    data = get_data()
    if user_id in data.get("admins", []):
        logger.warning(f"Attempted to remove admin ({user_id}) using remove_allowed_teacher.")
        return False

    if user_id in data.get("allowed_teachers", []):
        data["allowed_teachers"].remove(user_id)
        save_data(data)
        logger.info(f"User {user_id} removed from allowed teachers.")
        return True
    logger.warning(f"Attempted to remove non-existent allowed teacher: {user_id}")
    return False

def get_support_staff() -> List[int]:
    return get_data().get("support_staff", [])

def add_support_staff(user_id: int) -> bool:
    data = get_data()
    if user_id not in data.get("support_staff", []) and user_id not in data.get("admins", []):
        data["support_staff"].append(user_id)
        save_data(data)
        logger.info(f"User {user_id} added as support staff.")
        return True
    logger.info(f"User {user_id} is already support staff or admin.")
    return False

def remove_support_staff(user_id: int) -> bool:
    data = get_data()
    if user_id in data.get("support_staff", []):
        data["support_staff"].remove(user_id)
        save_data(data)
        logger.info(f"User {user_id} removed from support staff.")
        return True
    logger.warning(f"Attempted to remove non-existent support staff: {user_id}")
    return False


def get_next_request_id() -> int:
    data = get_data()
    requests = data.get("requests", [])
    if not requests:
        return 1
    return max(req.get("id", 0) for req in requests) + 1

def add_request(teacher_id: int, teacher_username: str | None, teacher_fullname: str,
              request_type: str, description: str, location: str, contact_name: str) -> int:
    data = get_data()
    request_id = get_next_request_id()
    new_request = {
        "id": request_id,
        "teacher_id": teacher_id,
        "teacher_username": teacher_username,
        "teacher_fullname": teacher_fullname,
        "request_type": request_type,
        "description": description,
        "location": location,
        "contact_name": contact_name,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "completed_at": None,
        "taken_by_id": None,
        "taken_by_username": None,
        "taken_by_fullname": None,
        "rating": None
    }
    data["requests"].append(new_request)
    save_data(data)
    logger.info(f"New request added with ID: {request_id}")
    return request_id

def update_request_status(request_id: int, new_status: str,
                          actor_id: int | None = None, actor_username: str | None = None, actor_fullname: str | None = None) -> bool:
    data = get_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            old_status = req.get("status")

            if new_status not in REQUEST_STATUSES:
                logger.warning(f"Attempted to set invalid status '{new_status}' for request {request_id}")
                return False

            req["status"] = new_status

            if new_status == 'completed' and old_status != 'completed':
                req["completed_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            elif new_status != 'completed' and old_status == 'completed':
                req["completed_at"] = None
                req["taken_by_id"] = None
                req["taken_by_username"] = None
                req["taken_by_fullname"] = None
                req["rating"] = None

            if new_status == 'in_progress' and req.get("taken_by_id") is None and actor_id is not None:
                req["taken_by_id"] = actor_id
                req["taken_by_username"] = actor_username
                req["taken_by_fullname"] = actor_fullname
                logger.info(f"Request {request_id} taken by {actor_id}.")

            if new_status == 'open' and old_status in ['in_progress', 'completed']:
                req["taken_by_id"] = None
                req["taken_by_username"] = None
                req["taken_by_fullname"] = None
                req["rating"] = None


            save_data(data)
            logger.info(f"Request {request_id} status updated to {new_status}.")
            return True
    logger.warning(f"Request with ID {request_id} not found for status update.")
    return False

def take_request_in_progress(request_id: int, support_staff_id: int, support_staff_username: str | None, support_staff_fullname: str) -> Tuple[bool, str]:
    data = get_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            if req.get("status") != 'open':
                return False, "Заявка уже не в статусе 'Открыта'."

            if req.get("taken_by_id") is not None:
                return False, "Заявка уже взята в работу другим специалистом."

            req["status"] = 'in_progress'
            req["taken_by_id"] = support_staff_id
            req["taken_by_username"] = support_staff_username
            req["taken_by_fullname"] = support_staff_fullname
            save_data(data)
            logger.info(f"Request {request_id} taken by support staff {support_staff_id}.")
            return True, "Заявка успешно взята в работу."

    return False, "Заявка не найдена."


def set_request_rating(request_id: int, rating: int) -> bool:
    data = get_data()
    for req in data.get("requests", []):
        if req.get("id") == request_id and req.get("status") == 'completed' and req.get("rating") is None:
            if 1 <= rating <= 10:
                req["rating"] = rating
                save_data(data)
                logger.info(f"Rating {rating} set for request {request_id}.")
                return True
            else:
                logger.warning(f"Attempted to set invalid rating {rating} for request {request_id}")
                return False
        elif req.get("id") == request_id and req.get("status") != 'completed':
            logger.warning(f"Attempted to set rating for non-completed request {request_id}")
            return False
        elif req.get("id") == request_id and req.get("rating") is not None:
            logger.warning(f"Attempted to set rating for already rated request {request_id}")
            return False

    logger.warning(f"Request {request_id} not found for rating.")
    return False

def get_request_details(request_id: int) -> Dict[str, Any] | None:
    for req in get_data().get("requests", []):
        if req.get("id") == request_id:
            req_copy = req.copy()
            req_copy['created_at'] = format_timestamp_for_display(req_copy.get('created_at'))
            req_copy['completed_at'] = format_timestamp_for_display(req_copy.get('completed_at'))
            req_copy['completed_at_formatted'] = req_copy['completed_at']

            return req_copy
    return None

def get_requests_by_status(status: str) -> List[Dict[str, Any]]:
    if status not in REQUEST_STATUSES:
        logger.warning(f"Attempted to get requests with invalid status: {status}")
        return []

    filtered_requests = []
    for req in get_data().get("requests", []):
        if req.get("status") == status:
            req_copy = req.copy()
            req_copy['created_at'] = format_timestamp_for_display(req_copy.get('created_at'))
            req_copy['completed_at'] = format_timestamp_for_display(req_copy.get('completed_at'))
            filtered_requests.append(req_copy)

    return sorted(filtered_requests, key=lambda x: x.get("id", 0))

def get_available_requests() -> List[Dict[str, Any]]:
    filtered_requests = []
    for req in get_data().get("requests", []):
        if req.get("status") == 'open' and req.get("taken_by_id") is None:
            req_copy = req.copy()
            req_copy['created_at'] = format_timestamp_for_display(req_copy.get('created_at'))
            filtered_requests.append(req_copy)

    return sorted(filtered_requests, key=lambda x: x.get("id", 0))

def get_requests_taken_by(support_staff_id: int) -> List[Dict[str, Any]]:
    filtered_requests = []
    for req in get_data().get("requests", []):
        if req.get("taken_by_id") == support_staff_id and req.get("status") != 'open':
            req_copy = req.copy()
            req_copy['created_at'] = format_timestamp_for_display(req_copy.get('created_at'))
            req_copy['completed_at'] = format_timestamp_for_display(req_copy.get('completed_at'))
            filtered_requests.append(req_copy)

    return sorted(filtered_requests, key=lambda x: x.get("id", 0))


def get_all_requests() -> List[Dict[str, Any]]:
    all_requests_formatted = []
    for req in get_data().get("requests", []):
        req_copy = req.copy()
        req_copy['created_at'] = format_timestamp_for_display(req_copy.get('created_at'))
        req_copy['completed_at'] = format_timestamp_for_display(req_copy.get('completed_at'))
        req_copy['completed_at_formatted'] = req_copy['completed_at']
        all_requests_formatted.append(req_copy)

    return sorted(all_requests_formatted, key=lambda x: x.get("id", 0))

def get_all_requests_formatted() -> str:
    requests = get_all_requests()

    if not requests:
        return "Нет истории для экспорта."

    text = ""
    for req in requests:
        req_id = req.get("id", "N/A")
        teacher_id = req.get("teacher_id", "N/A")
        teacher_username = req.get("teacher_username", "Не указано")
        teacher_fullname = req.get("teacher_fullname", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        status = req.get("status", "N/A")
        created_at = req.get("created_at", "N/A")
        completed_at = req.get("completed_at_formatted", "еще нет")

        taken_by_id = req.get("taken_by_id")
        taken_by_username = req.get("taken_by_username")
        taken_by_fullname = req.get("taken_by_fullname", "Неизвестно")
        rating = req.get("rating", "Нет оценки")

        taken_by_info = ""
        if taken_by_id:
             taken_by_info = f"В работе у: {taken_by_fullname} (ID: {taken_by_id}{f', @{taken_by_username}' if taken_by_username else ''})\n"

        text += (
            f"Заявка №{req_id}\n"
            f"От: {teacher_fullname} (ID: {teacher_id}{f', @{teacher_username}' if teacher_username else ''})\n"
            f"Тип: {req_type}\n"
            f"Местоположение: {location}\n"
            f"Статус: {status}\n"
            f"{taken_by_info}"
            f"Создана: {created_at}\n"
            f"Завершена: {completed_at}\n"
            f"Оценка: {rating}\n"
            "---\n"
        )

    return text


def get_active_requests_count_for_user(user_id: int) -> int:
    count = 0
    for req in get_data().get("requests", []):
        if req.get("teacher_id") == user_id and req.get("status") in ['open', 'in_progress']:
            count += 1
    return count

def clear_all_requests() -> int:
    data = get_data()
    initial_count = len(data.get("requests", []))
    data["requests"] = []
    save_data(data)
    logger.info(f"All requests cleared. {initial_count} requests removed.")
    return initial_count
