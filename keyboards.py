from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any, Tuple

def get_request_types_kb() -> ReplyKeyboardMarkup:
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, отправить", callback_data="confirm_request_yes"),
                InlineKeyboardButton(text="Нет, отменить", callback_data="confirm_request_no")
            ]
        ]
    )

def get_admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть открытые заявки", callback_data="admin_view_open_requests")],
            [InlineKeyboardButton(text="Посмотреть завершенные заявки", callback_data="admin_view_completed_requests")],
            [InlineKeyboardButton(text="История всех заявок", callback_data="admin_view_all_requests")],
            [
                InlineKeyboardButton(text="🧹 Очистить историю", callback_data="admin_clear_history_start"),
                InlineKeyboardButton(text="📥 Экспортировать историю", callback_data="admin_export_history")
            ],
            [InlineKeyboardButton(text="Управление администраторами", callback_data="admin_manage_admins")],
            [InlineKeyboardButton(text="Управление учителями", callback_data="admin_manage_teachers")]
        ]
    )

def build_requests_list_kb(requests: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for req in requests:
        req_id = req.get("id", "N/A")
        contact_name = req.get("contact_name", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        created_at = req.get("created_at", "N/A")

        button_text = f"№{req_id} - {req_type} в {location} от {contact_name}"
        builder.add(InlineKeyboardButton(text=button_text[:60], callback_data=f"view_request_{req_id}"))

    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin"))

    return builder.as_markup()

def get_request_details_kb(request_id: int, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if status == 'open':
        builder.add(InlineKeyboardButton(text="Взять в работу", callback_data=f"update_status_{request_id}_in_progress"))
    elif status == 'in_progress':
         builder.add(InlineKeyboardButton(text="Завершить", callback_data=f"update_status_{request_id}_completed"))
         builder.add(InlineKeyboardButton(text="Вернуть в открытые", callback_data=f"update_status_{request_id}_open"))

    if status != 'completed' and status != 'cancelled':
         builder.add(InlineKeyboardButton(text="Отменить", callback_data=f"update_status_{request_id}_cancelled"))

    builder.add(InlineKeyboardButton(text="Изменить статус вручную", callback_data=f"manual_status_start_{request_id}"))

    builder.add(InlineKeyboardButton(text="Назад к открытым", callback_data="admin_view_open_requests"))
    builder.adjust(1)
    return builder.as_markup()

def get_admin_manage_kb() -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить учителя", callback_data="teacher_add_start"),
                InlineKeyboardButton(text="Удалить учителя", callback_data="teacher_remove_start")
            ],
            [InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin")]
        ]
    )

def get_clear_history_confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, очистить", callback_data="admin_clear_history_confirm_yes"),
                InlineKeyboardButton(text="Нет, отмена", callback_data="admin_clear_history_confirm_no")
            ]
        ]
    )

def get_rating_keyboard(request_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for rating in range(1, 11):
        builder.add(InlineKeyboardButton(text=str(rating), callback_data=f"rate_request_{request_id}_{rating}"))
    builder.adjust(5)
    return builder.as_markup()

def get_manual_status_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Открыта", callback_data="manual_status_open"))
    builder.add(InlineKeyboardButton(text="В работе", callback_data="manual_status_in_progress"))
    builder.add(InlineKeyboardButton(text="Завершена", callback_data="manual_status_completed"))
    builder.add(InlineKeyboardButton(text="Отменена", callback_data="manual_status_cancelled"))
    builder.adjust(2)
    return builder.as_markup()
