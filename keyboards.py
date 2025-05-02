from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any, Tuple

# --- Клавиатуры для пользователя ---

def get_request_types_kb() -> ReplyKeyboardMarkup:
    """Возвращает Reply-клавиатуру для выбора типа заявки с эмодзи."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💻 ПК")],
            [KeyboardButton(text="🖨️ Принтер")],
            [KeyboardButton(text="📽️ Проектор")],
            [KeyboardButton(text="🖥️ Интерактивная доска")],
            [KeyboardButton(text="🔄 Другое")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_confirm_request_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для подтверждения заявки."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, отправить", callback_data="confirm_request_yes"),
                InlineKeyboardButton(text="Нет, отменить", callback_data="confirm_request_no")
            ]
        ]
    )

# --- Клавиатуры для админа ---

def get_admin_menu_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру главного меню админа."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть открытые заявки", callback_data="admin_view_open_requests")],
            [InlineKeyboardButton(text="Посмотреть завершенные заявки", callback_data="admin_view_completed_requests")], # <-- Новая кнопка
            [InlineKeyboardButton(text="История всех заявок", callback_data="admin_view_all_requests")], # <-- Новая кнопка
            [InlineKeyboardButton(text="Управление администраторами", callback_data="admin_manage_admins")],
            [InlineKeyboardButton(text="Управление учителями", callback_data="admin_manage_teachers")]
        ]
    )

# Функция для построения клавиатуры со списком заявок (используется для открытых и завершенных)
def build_requests_list_kb(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру со списком заявок для админа."""
    builder = InlineKeyboardBuilder()
    for req in requests:
        req_id = req.get("id", "N/A")
        contact_name = req.get("contact_name", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        created_at = req.get("created_at", "N/A")

        button_text = f"№{req_id} - {req_type} в {location} от {contact_name}"
        # Кнопка ведет на просмотр деталей, используя существующий хэндлер
        builder.add(InlineKeyboardButton(text=button_text[:60], callback_data=f"view_request_{req_id}"))

    builder.adjust(1)
    # Добавим кнопку "Назад в админ-панель" в конце списков заявок
    builder.row(InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin"))

    return builder.as_markup()


def get_request_details_kb(request_id: int, status: str) -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру с действиями для конкретной заявки."""
    builder = InlineKeyboardBuilder()

    if status == 'open':
        builder.add(InlineKeyboardButton(text="Взять в работу", callback_data=f"update_status_{request_id}_in_progress"))
    elif status == 'in_progress':
         builder.add(InlineKeyboardButton(text="Завершить", callback_data=f"update_status_{request_id}_completed"))
         builder.add(InlineKeyboardButton(text="Вернуть в открытые", callback_data=f"update_status_{request_id}_open"))

    if status != 'completed' and status != 'cancelled':
         builder.add(InlineKeyboardButton(text="Отменить", callback_data=f"update_status_{request_id}_cancelled"))

    # Кнопка "Назад к открытым"
    builder.add(InlineKeyboardButton(text="Назад к открытым", callback_data="admin_view_open_requests"))
    builder.adjust(1)
    return builder.as_markup()


def get_admin_manage_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления администраторами (добавить/удалить)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить администратора", callback_data="admin_add_start"),
                InlineKeyboardButton(text="Удалить администратора", callback_data="admin_remove_start")
            ],
            [InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin")]
        ]
    )

def get_teacher_manage_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления учителями (добавить/удалить)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить учителя", callback_data="teacher_add_start"),
                InlineKeyboardButton(text="Удалить учителя", callback_data="teacher_remove_start")
            ],
            [InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin")]
        ]
    )
