# handlers/admin.py
import logging
import re
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime
from typing import Dict, Any
# <-- Добавляем импорт InlineKeyboardMarkup и InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states import AdminStates
import keyboards as kb
import texts as txt
import json_storage as db
import config

router = Router()
logger = logging.getLogger(__name__)

# ... Остальной код handlers/admin.py без изменений ...


# --- Вспомогательная функция для экранирования HTML ---
def escape_html(text: str) -> str:
    """Экранирует специальные символы HTML (<, >, &)."""
    if text is None:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# --- Декораторы для проверки прав админа ---
def admin_required(func):
    """Декоратор для проверки прав администратора."""
    async def wrapper(event: types.Message, **kwargs: Dict[str, Any]):
        data = kwargs.get('data', {})
        bot_instance = kwargs.get('bot')
        if bot_instance and 'bot' not in data:
             data['bot'] = bot_instance
        state_instance = kwargs.get('state')
        if state_instance and 'state' not in data:
             data['state'] = state_instance

        # --- Отладочное логирование в декораторе ---
        logger.debug(f"admin_required wrapper triggered for {func.__name__}")
        user_id = event.from_user.id
        is_admin_status = db.is_admin(user_id)
        logger.debug(f"User ID: {user_id}, Is Admin: {is_admin_status}")
        # --- Конец отладочного логирования ---


        if not is_admin_status:
            logger.warning(f"Access denied for user {user_id} trying to access {func.__name__}")
            await event.reply(txt.ACCESS_DENIED_ADMIN)
            return

        logger.debug(f"Access granted for user {user_id} to {func.__name__}. Calling handler.")
        try:
             return await func(event, **data)
        except TypeError as e:
             logger.error(f"Error calling handler {func.__name__} inside admin_required with event and **data: {e}")
             pass

    wrapper.__wrapped__ = func
    return wrapper


def admin_callback_required(func):
    """Декоратор для проверки прав администратора в callback_query."""
    async def wrapper(event: types.CallbackQuery, **kwargs: Dict[str, Any]):
        data = kwargs.get('data', {})
        bot_instance = kwargs.get('bot')
        if bot_instance and 'bot' not in data:
             data['bot'] = bot_instance
        state_instance = kwargs.get('state')
        if state_instance and 'state' not in data:
             data['state'] = state_instance

        # --- Отладочное логирование в декораторе ---
        logger.debug(f"admin_callback_required wrapper triggered for {func.__name__}")
        user_id = event.from_user.id
        is_admin_status = db.is_admin(user_id)
        logger.debug(f"User ID: {user_id}, Is Admin: {is_admin_status}")
        logger.debug(f"Callback data: {event.data}")
        # --- Конец отладочного логирования ---


        if not is_admin_status:
            logger.warning(f"Access denied for user {user_id} trying to access {func.__name__} via callback.")
            await event.answer(txt.ACCESS_DENIED_ADMIN, show_alert=True)
            return

        logger.debug(f"Access granted for user {user_id} to {func.__name__} via callback. Calling handler.")
        try:
             return await func(event, **data)
        except TypeError as e:
             logger.error(f"Error calling handler {func.__name__} inside admin_callback_required with event and **data: {e}")
             pass

    wrapper.__wrapped__ = func
    return wrapper

# --- Админские команды ---

@router.message(Command("admin"))
@admin_required
async def handle_admin_command(message: types.Message):
    """Обработчик команды /admin. Показывает админ-панель."""
    await message.reply(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())

# Хэндлер для callback_data="admin" - Должен обрабатывать кнопку "Назад в админ-панель"
@router.callback_query(F.data == "admin")
@admin_callback_required
async def handle_admin_callback(callback_query: types.CallbackQuery):
    """Показывает главное админ-меню по колбэку."""
    # --- Отладочное логирование в хэндлере ---
    logger.info("Admin main menu callback handler triggered.")
    # --- Конец отладочного логирования ---
    await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
    await callback_query.answer()


# --- Хэндлеры для просмотра и управления заявками ---

@router.callback_query(F.data == "admin_view_open_requests")
@admin_callback_required
async def admin_view_open_requests(callback_query: types.CallbackQuery):
    """Показывает список открытых заявок."""
    requests = db.get_requests_by_status('open')

    if not requests:
        # Возвращаемся в главное меню, если нет открытых
        await callback_query.message.edit_text(txt.ADMIN_NO_OPEN_REQUESTS, reply_markup=kb.get_admin_menu_kb())
        await callback_query.answer()
        return

    text = txt.ADMIN_OPEN_REQUESTS_LIST_TEMPLATE

    for req in requests:
        req_id = req.get("id", "N/A")
        contact_name = req.get("contact_name", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        created_at = req.get("created_at", "N/A")

        text += f"№{req_id}: {escape_html(req_type)} в {escape_html(location)} от {escape_html(contact_name)} ({created_at})\n"

    # Используем build_requests_list_kb, которая теперь включает кнопку "Назад в админ-панель"
    requests_kb = kb.build_requests_list_kb(requests)

    await callback_query.message.edit_text(
        text,
        reply_markup=requests_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("view_request_"))
@admin_callback_required
async def admin_view_request_details(callback_query: types.CallbackQuery):
    """Показывает детали конкретной заявки и кнопки действий."""
    request_id = int(callback_query.data.split("_")[2])
    request = db.get_request_details(request_id)

    if not request:
        await callback_query.answer(txt.ADMIN_REQUEST_NOT_FOUND, show_alert=True)
        # После ошибки показа деталей, возвращаемся к списку открытых
        await admin_view_open_requests(callback_query)
        return

    req_id = request.get("id", "N/A")
    teacher_id = request.get("teacher_id", "N/A")
    teacher_username = request.get("teacher_username")
    teacher_fullname = request.get("teacher_fullname", "Не указано")
    req_type = request.get("request_type", "Неизвестно")
    description = request.get("description", "Нет описания")
    location = request.get("location", "Не указано")
    contact_name = request.get("contact_name", "Не указано")
    status = request.get("status", "N/A")
    created_at = request.get("created_at", "N/A")
    completed_at = request.get("completed_at")


    username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
    completed_at_formatted = completed_at if completed_at else 'еще нет'
    status_ru = txt.STATUS_MAP_RU.get(status, status)

    text = txt.ADMIN_REQUEST_DETAILS_TEMPLATE.format(
        request_id=req_id,
        status_ru=status_ru,
        teacher_fullname=escape_html(teacher_fullname),
        teacher_id=teacher_id,
        username_mention=username_mention,
        contact_name=escape_html(contact_name),
        request_type=escape_html(req_type),
        location=escape_html(location),
        description=escape_html(description),
        created_at=created_at,
        completed_at=completed_at_formatted
    )

    details_kb = kb.get_request_details_kb(req_id, status)

    await callback_query.message.edit_text(
        text,
        reply_markup=details_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("update_status_"))
@admin_callback_required
async def admin_update_request_status(callback_query: types.CallbackQuery, bot: Bot):
    """Обновляет статус заявки по кнопке из админки."""
    try:
        parts = callback_query.data.split("_")
        request_id = int(parts[2])
        new_status = parts[3]

        db.update_request_status(request_id, new_status)

        request = db.get_request_details(request_id)
        if request:
            req_id = request.get("id", "N/A")
            teacher_id = request.get("teacher_id", "N/A")
            req_type = request.get("request_type", "Неизвестно")
            location = request.get("location", "Не указано")
            status = request.get("status", "N/A")

            status_ru = txt.STATUS_MAP_RU.get(status, status)
            await callback_query.answer(txt.ADMIN_STATUS_UPDATED_ANSWER_TEMPLATE.format(request_id=req_id, status_ru=status_ru))

            try:
                await bot.send_message(
                    teacher_id,
                    txt.ADMIN_NOTIFY_TEACHER_STATUS_TEMPLATE.format(
                        request_id=req_id,
                        request_type=escape_html(req_type),
                        location=escape_html(location),
                        status_ru=status_ru
                    ),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить учителя {teacher_id} о смене статуса заявки {req_id}: {e}")


            # После смены статуса, обновляем детали заявки
            await admin_view_request_details(callback_query)

        else:
            await callback_query.answer(txt.ADMIN_REQUEST_NOT_FOUND, show_alert=True)
            # После ошибки обновления, возвращаемся к списку открытых
            await admin_view_open_requests(callback_query)

    except Exception as e:
         logger.error(f"Ошибка при смене статуса заявки: {e}")
         await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)


# --- Хэндлеры для управления администраторами ---

@router.callback_query(F.data == "admin_manage_admins")
@admin_callback_required
async def admin_manage_admins(callback_query: types.CallbackQuery):
    """Показывает список администраторов и кнопки управления."""
    admins_ids = db.get_admins()

    text = txt.ADMIN_LIST_ADMINS_TEMPLATE
    if not admins_ids:
        text += txt.ADMIN_ADMINS_NOT_FOUND
    else:
        for user_id in admins_ids:
            text += txt.ADMIN_TEACHER_INFO_TEMPLATE.format(user_id=user_id) + "\n"

    await callback_query.message.edit_text(text, reply_markup=kb.get_admin_manage_kb(), parse_mode=ParseMode.HTML)
    await callback_query.answer()


@router.callback_query(F.data == "admin_add_start")
@admin_callback_required
async def admin_add_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинает процесс добавления администратора."""
    await callback_query.message.edit_text(txt.ADMIN_ADD_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_admin_id_to_add)
    await callback_query.answer()


@router.message(AdminStates.waiting_for_admin_id_to_add)
@admin_required
async def admin_add_process(message: types.Message, state: FSMContext, bot: Bot):
    """Обрабатывает ввод User ID для добавления админа."""
    try:
        user_id_to_add = int(message.text.strip())
        success = db.add_admin_user(user_id_to_add)

        feedback_text = ""
        if success:
            feedback_text = txt.ADMIN_ADD_ADMIN_SUCCESS_TEMPLATE.format(user_id=user_id_to_add)
        else:
            feedback_text = txt.ADMIN_ADD_ADMIN_ALREADY_ADMIN_TEMPLATE.format(user_id=user_id_to_add)

        await state.clear()

        await message.answer(feedback_text)

        await message.answer(
            txt.ADMIN_PANEL_MESSAGE,
            reply_markup=kb.get_admin_manage_kb(),
            parse_mode=ParseMode.HTML
        )


    except ValueError:
        await message.answer(txt.ADMIN_INVALID_ID)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при добавлении админа: {e}")
        await message.answer(txt.ADMIN_ACTION_ERROR)
        await state.clear()


@router.callback_query(F.data == "admin_remove_start")
@admin_callback_required
async def admin_remove_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинает процесс удаления администратора."""
    await callback_query.message.edit_text(txt.ADMIN_REMOVE_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_admin_id_to_remove)
    await callback_query.answer()


@router.message(AdminStates.waiting_for_admin_id_to_remove)
@admin_required
async def admin_remove_process(message: types.Message, state: FSMContext, bot: Bot):
    """Обрабатывает ввод User ID для удаления админа."""
    try:
        user_id_to_remove = int(message.text.strip())

        if user_id_to_remove == message.from_user.id:
             await message.answer(txt.ADMIN_REMOVE_ADMIN_SELF)
             await state.clear()
             return

        success, error_message = db.remove_admin_user(user_id_to_remove)

        feedback_text = ""
        if success:
            feedback_text = txt.ADMIN_REMOVE_ADMIN_SUCCESS_TEMPLATE.format(user_id=user_id_to_remove)
        else:
            feedback_text = error_message if error_message else txt.ADMIN_REMOVE_ADMIN_NOT_FOUND_TEMPLATE.format(user_id=user_id_to_remove)

        await state.clear()

        await message.answer(feedback_text)

        await message.answer(
            txt.ADMIN_PANEL_MESSAGE,
            reply_markup=kb.get_admin_manage_kb(),
            parse_mode=ParseMode.HTML
        )


    except ValueError:
        await message.answer(txt.ADMIN_INVALID_ID)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при удалении админа: {e}")
        await message.answer(txt.ADMIN_ACTION_ERROR)
        await state.clear()

# --- Хэндлеры для управления учителями ---

@router.callback_query(F.data == "admin_manage_teachers")
@admin_callback_required
async def admin_manage_teachers(callback_query: types.CallbackQuery):
    """Показывает список разрешенных учителей и кнопки управления."""
    teacher_ids = db.get_allowed_teachers()

    text = txt.ADMIN_LIST_TEACHERS_TEMPLATE
    if not teacher_ids:
        text += txt.ADMIN_TEACHERS_NOT_FOUND
    else:
        for user_id in teacher_ids:
            text += txt.ADMIN_TEACHER_INFO_TEMPLATE.format(user_id=user_id) + "\n"

    await callback_query.message.edit_text(text, reply_markup=kb.get_teacher_manage_kb(), parse_mode=ParseMode.HTML)
    await callback_query.answer()


@router.callback_query(F.data == "teacher_add_start")
@admin_callback_required
async def teacher_add_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинает процесс добавления разрешенного учителя."""
    await callback_query.message.edit_text(txt.ADMIN_ADD_TEACHER_PROMPT)
    await state.set_state(AdminStates.waiting_for_teacher_id_to_add)
    await callback_query.answer()


@router.message(AdminStates.waiting_for_teacher_id_to_add)
@admin_required
async def teacher_add_process(message: types.Message, state: FSMContext, bot: Bot):
    """Обрабатывает ввод User ID для добавления учителя."""
    try:
        user_id_to_add = int(message.text.strip())
        success = db.add_allowed_teacher(user_id_to_add)

        feedback_text = ""
        if success:
            feedback_text = txt.ADMIN_ADD_TEACHER_SUCCESS_TEMPLATE.format(user_id=user_id_to_add)
        else:
            feedback_text = txt.ADMIN_ADD_TEACHER_ALREADY_ALLOWED_TEMPLATE.format(user_id=user_id_to_add)

        await state.clear()

        await message.answer(feedback_text)

        await message.answer(
             txt.ADMIN_PANEL_MESSAGE,
             reply_markup=kb.get_teacher_manage_kb(),
             parse_mode=ParseMode.HTML
        )


    except ValueError:
        await message.answer(txt.ADMIN_INVALID_ID)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при добавлении учителя: {e}")
        await message.answer(txt.ADMIN_ACTION_ERROR)
        await state.clear()

@router.callback_query(F.data == "teacher_remove_start")
@admin_callback_required
async def teacher_remove_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Начинает процесс удаления разрешенного учителя."""
    await callback_query.message.edit_text(txt.ADMIN_REMOVE_TEACHER_PROMPT)
    await state.set_state(AdminStates.waiting_for_teacher_id_to_remove)
    await callback_query.answer()


@router.message(AdminStates.waiting_for_teacher_id_to_remove)
@admin_required
async def teacher_remove_process(message: types.Message, state: FSMContext, bot: Bot):
    """Обрабатывает ввод User ID для удаления учителя."""
    try:
        user_id_to_remove = int(message.text.strip())
        success = db.remove_allowed_teacher(user_id_to_remove)

        feedback_text = ""
        if success:
            feedback_text = txt.ADMIN_REMOVE_TEACHER_SUCCESS_TEMPLATE.format(user_id=user_id_to_remove)
        else:
            feedback_text = txt.ADMIN_REMOVE_TEACHER_NOT_FOUND_TEMPLATE.format(user_id=user_id_to_remove)

        await state.clear()

        await message.answer(feedback_text)

        await message.answer(
            txt.ADMIN_PANEL_MESSAGE,
            reply_markup=kb.get_teacher_manage_kb(),
            parse_mode=ParseMode.HTML
        )


    except ValueError:
        await message.answer(txt.ADMIN_INVALID_ID)
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при удалении учителя: {e}")
        await message.answer(txt.ADMIN_ACTION_ERROR)
        await state.clear()

# --- НОВЫЕ Хэндлеры для просмотра завершенных и всех заявок ---

@router.callback_query(F.data == "admin_view_completed_requests")
@admin_callback_required
async def admin_view_completed_requests(callback_query: types.CallbackQuery):
    """Показывает список завершенных заявок."""
    requests = db.get_requests_by_status('completed')

    if not requests:
        await callback_query.message.edit_text(txt.ADMIN_NO_COMPLETED_REQUESTS, reply_markup=kb.get_admin_menu_kb())
        await callback_query.answer()
        return

    text = txt.ADMIN_COMPLETED_REQUESTS_LIST_TEMPLATE

    for req in requests:
        req_id = req.get("id", "N/A")
        contact_name = req.get("contact_name", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        created_at = req.get("created_at", "N/A")
        text += f"№{req_id}: {escape_html(req_type)} в {escape_html(location)} от {escape_html(contact_name)} (Создана: {created_at})\n"


    # Используем build_requests_list_kb, которая теперь включает кнопку "Назад в админ-панель"
    completed_requests_kb = kb.build_requests_list_kb(requests)

    await callback_query.message.edit_text(
        text,
        reply_markup=completed_requests_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()


@router.callback_query(F.data == "admin_view_all_requests")
@admin_callback_required
async def admin_view_all_requests(callback_query: types.CallbackQuery):
    """Показывает историю всех заявок."""
    requests = db.get_all_requests()

    if not requests:
        await callback_query.message.edit_text(txt.ADMIN_NO_REQUESTS_HISTORY, reply_markup=kb.get_admin_menu_kb())
        await callback_query.answer()
        return

    text = txt.ADMIN_ALL_REQUESTS_LIST_TEMPLATE

    for req in requests:
        req_id = req.get("id", "N/A")
        teacher_id = req.get("teacher_id", "N/A")
        teacher_username = req.get("teacher_username")
        teacher_fullname = req.get("teacher_fullname", "Не указано")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        status = req.get("status", "N/A")
        created_at = req.get("created_at", "N/A")
        completed_at = req.get("completed_at")

        username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
        completed_at_formatted = completed_at if completed_at else 'еще нет'
        status_ru = txt.STATUS_MAP_RU.get(status, status)

        text += txt.ADMIN_HISTORY_ITEM_TEMPLATE.format(
             request_id=req_id,
             request_type=escape_html(req_type),
             location=escape_html(location),
             teacher_fullname=escape_html(teacher_fullname),
             teacher_id=teacher_id,
             username_mention=username_mention,
             status_ru=status_ru,
             created_at=created_at,
             completed_at_formatted=completed_at_formatted
        ) + "\n---\n"

    # Создаем отдельную Inline-клавиатуру только с кнопкой "Назад в админ-панель" для истории
    history_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в админ-панель", callback_data="admin")]
        ]
    )

    await callback_query.message.edit_text(
        text,
        reply_markup=history_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()
