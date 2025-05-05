from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

import texts as txt

def get_request_types_kb() -> ReplyKeyboardMarkup:
    """Возвращает Reply-клавиатуру для выбора типа заявки."""
    keyboard = [
        [KeyboardButton(text="💻 ПК"), KeyboardButton(text="🖨️ Принтер")],
        [KeyboardButton(text="📽️ Проектор"), KeyboardButton(text="🖥️ Интерактивная доска")],
        [KeyboardButton(text="🔄 Другое")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_confirm_request_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для подтверждения отправки заявки."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да, отправить", callback_data="confirm_request_yes"),
            InlineKeyboardButton(text="❌ Нет, отменить", callback_data="confirm_request_no")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_rating_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для оценки заявки учителем."""
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate_{request_id}_{i}") for i in range(1, 11)
    ]
    keyboard = [
        buttons[:5],
        buttons[5:]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_menu_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для главного меню админ-панели."""
    keyboard = [
        [InlineKeyboardButton(text="📋 Открытые заявки", callback_data="admin_view_open_requests")],
        [InlineKeyboardButton(text="📊 Вся история заявок", callback_data="admin_view_all_requests")],
        [InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="admin_clear_history_start")],
        [InlineKeyboardButton(text="📥 Экспорт истории (TXT)", callback_data="admin_export_history")],
        [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_manage_users")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_manage_users_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления пользователями (админы, учителя, эникейщики)."""
    keyboard = [
        [InlineKeyboardButton(text="🛠️ Управление администраторами", callback_data="admin_manage_admins")],
        [InlineKeyboardButton(text="👩‍🏫 Управление учителями", callback_data="admin_manage_teachers")],
        [InlineKeyboardButton(text="👨‍💻 Управление ИТ-специалистами", callback_data="admin_manage_support_staff")],
        [InlineKeyboardButton(text="⬅️ Назад в админ-панель", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_manage_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления администраторами."""
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить администратора", callback_data="admin_add_start")],
        [InlineKeyboardButton(text="➖ Удалить администратора", callback_data="admin_remove_start")],
        [InlineKeyboardButton(text="⬅️ Назад к управлению пользователями", callback_data="admin_manage_users")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_teacher_manage_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления учителями."""
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить учителя", callback_data="teacher_add_start")],
        [InlineKeyboardButton(text="➖ Удалить учителя", callback_data="teacher_remove_start")],
        [InlineKeyboardButton(text="⬅️ Назад к управлению пользователями", callback_data="admin_manage_users")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_support_staff_manage_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для управления ИТ-специалистами."""
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить ИТ-специалиста", callback_data="support_staff_add_start")],
        [InlineKeyboardButton(text="➖ Удалить ИТ-специалиста", callback_data="support_staff_remove_start")],
        [InlineKeyboardButton(text="⬅️ Назад к управлению пользователями", callback_data="admin_manage_users")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_requests_list_kb(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру со списком заявок (для админа)."""
    keyboard = []
    for req in requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        button_text = f"№{req_id}: {req_type} в {location}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"view_request_{req_id}")])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад в админ-панель", callback_data="admin")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_available_requests_kb(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру со списком доступных заявок (для эникейщика)."""
    keyboard = []
    for req in requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")

        button_text = f"№{req_id}: {req_type} в {location}"
        keyboard.append([
            InlineKeyboardButton(text=button_text, callback_data=f"view_request_{req_id}"),
            InlineKeyboardButton(text="👨‍💻 Взять", callback_data=f"take_request_{req_id}")
        ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад в панель ИТ", callback_data="support_staff")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_taken_requests_kb(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Строит Inline-клавиатуру со списком заявок, взятых эникейщиком."""
    keyboard = []
    for req in requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        status = req.get("status", "N/A")
        status_ru = txt.STATUS_MAP_RU.get(status, status)

        button_text = f"№{req_id}: {req_type} в {location} ({status_ru})"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"view_request_{req_id}")])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад в панель ИТ", callback_data="support_staff")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_request_details_kb(request_id: int, status: str, user_role: str) -> InlineKeyboardMarkup:
    """
    Возвращает Inline-клавиатуру для деталей заявки.
    Логика кнопок зависит от статуса заявки и роли пользователя (admin/support_staff).
    """
    keyboard = []

    if user_role == 'admin':
        if status == 'open':
            keyboard.append([InlineKeyboardButton(text="▶️ Взять в работу", callback_data=f"update_status_{request_id}_in_progress")])
        elif status == 'in_progress':
            keyboard.append([
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"update_status_{request_id}_completed"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"update_status_{request_id}_cancelled")
            ])
        elif status in ['completed', 'cancelled']:
            keyboard.append([InlineKeyboardButton(text="🔄 Снова Открыть", callback_data=f"update_status_{request_id}_open")])

        keyboard.append([InlineKeyboardButton(text="🔧 Изменить статус вручную", callback_data=f"manual_status_start_{request_id}")])
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад в админ-панель", callback_data="admin")])


    elif user_role == 'support_staff':
        if status == 'open':
            keyboard.append([InlineKeyboardButton(text="👨‍💻 Взять в работу", callback_data=f"take_request_{request_id}")])
        elif status == 'in_progress':
            keyboard.append([
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"update_status_{request_id}_completed"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"update_status_{request_id}_cancelled")
            ])

        keyboard.append([InlineKeyboardButton(text="⬅️ Назад в панель ИТ", callback_data="support_staff")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_clear_history_confirmation_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для подтверждения очистки истории."""
    keyboard = [
        [
            InlineKeyboardButton(text="🔥 Да, очистить", callback_data="admin_clear_history_confirm_yes"),
            InlineKeyboardButton(text="✋ Нет, отмена", callback_data="admin_clear_history_confirm_no")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_manual_status_keyboard() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для выбора статуса вручную (для админа)."""
    keyboard = [
        [
            InlineKeyboardButton(text=txt.STATUS_MAP_RU['open'], callback_data="manual_status_open"),
            InlineKeyboardButton(text=txt.STATUS_MAP_RU['in_progress'], callback_data="manual_status_in_progress")
        ],
        [
            InlineKeyboardButton(text=txt.STATUS_MAP_RU['completed'], callback_data="manual_status_completed"),
            InlineKeyboardButton(text=txt.STATUS_MAP_RU['cancelled'], callback_data="manual_status_cancelled")
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="manual_status_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_support_staff_menu_kb() -> InlineKeyboardMarkup:
    """Возвращает кнопку 'Назад в панель ИТ'."""
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Назад в панель ИТ", callback_data="support_staff")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Добавлена отсутствующая функция get_support_staff_menu_kb
def get_support_staff_menu_kb() -> InlineKeyboardMarkup:
    """Возвращает Inline-клавиатуру для главного меню ИТ-специалиста."""
    keyboard = [
        [InlineKeyboardButton(text="📋 Доступные заявки", callback_data="support_staff_view_available")],
        [InlineKeyboardButton(text="🛠️ Мои заявки", callback_data="support_staff_view_taken")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
