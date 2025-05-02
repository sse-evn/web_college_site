import logging
import re
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime
from typing import Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from io import BytesIO

from states import AdminStates, TeacherRatingState
import keyboards as kb
import texts as txt
import json_storage as db
import config
from utils import escape_html

router = Router()
logger = logging.getLogger(__name__)

def admin_required(func):
    async def wrapper(event: types.Message, **kwargs: Dict[str, Any]):
        data = kwargs.get('data', {})
        bot_instance = kwargs.get('bot')
        if bot_instance and 'bot' not in data:
             data['bot'] = bot_instance
        state_instance = kwargs.get('state')
        if state_instance and 'state' not in data:
             data['state'] = state_instance

        user_id = event.from_user.id
        is_admin_status = db.is_admin(user_id)

        if not is_admin_status:
            await event.reply(txt.ACCESS_DENIED_ADMIN)
            return

        try:
             return await func(event, **data)
        except TypeError as e:
             logger.error(f"Error calling handler {func.__name__} inside admin_required with event and **data: {e}")
             pass

    wrapper.__wrapped__ = func
    return wrapper

def admin_callback_required(func):
    async def wrapper(event: types.CallbackQuery, **kwargs: Dict[str, Any]):
        data = kwargs.get('data', {})
        bot_instance = kwargs.get('bot')
        if bot_instance and 'bot' not in data:
             data['bot'] = bot_instance
        state_instance = kwargs.get('state')
        if state_instance and 'state' not in data:
             data['state'] = state_instance

        user_id = event.from_user.id
        is_admin_status = db.is_admin(user_id)

        if not is_admin_status:
            await event.answer(txt.ACCESS_DENIED_ADMIN, show_alert=True)
            return

        try:
             return await func(event, **data)
        except TypeError as e:
             logger.error(f"Error calling handler {func.__name__} inside admin_callback_required with event and **data: {e}")
             pass

    wrapper.__wrapped__ = func
    return wrapper

@router.message(Command("admin"))
@admin_required
async def handle_admin_command(message: types.Message):
    await message.reply(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())

@router.callback_query(F.data == "admin")
@admin_callback_required
async def handle_admin_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
    await callback_query.answer()

@router.callback_query(F.data == "admin_view_open_requests")
@admin_callback_required
async def admin_view_open_requests(callback_query: types.CallbackQuery):
    requests = db.get_requests_by_status('open')

    if not requests:
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
    request_id = int(callback_query.data.split("_")[2])
    request = db.get_request_details(request_id)

    if not request:
        await callback_query.answer(txt.ADMIN_REQUEST_NOT_FOUND, show_alert=True)
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
    taken_by_id = request.get("taken_by_id")
    taken_by_username = request.get("taken_by_username")
    taken_by_fullname = request.get("taken_by_fullname", "Неизвестно")

    username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
    completed_at_formatted = completed_at if completed_at else 'еще нет'
    status_ru = txt.STATUS_MAP_RU.get(status, status)

    taken_by_info = ""
    if taken_by_id:
         taken_by_username_mention = f', @{escape_html(taken_by_username)}' if taken_by_username else ''
         taken_by_info = txt.ADMIN_TAKEN_BY_TEMPLATE.format(
              admin_fullname=escape_html(taken_by_fullname),
              admin_id=taken_by_id,
              username_mention=taken_by_username_mention
         )

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
    ) + taken_by_info


    details_kb = kb.get_request_details_kb(req_id, status)

    await callback_query.message.edit_text(
        text,
        reply_markup=details_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("update_status_"))
@admin_callback_required
async def admin_update_request_status(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        parts = callback_query.data.split("_")
        request_id = int(parts[2])
        new_status = parts[3]

        current_request_details = db.get_request_details(request_id)
        if not current_request_details:
             await callback_query.answer(txt.ADMIN_REQUEST_NOT_FOUND, show_alert=True)
             await admin_view_open_requests(callback_query)
             return

        teacher_id = current_request_details.get("teacher_id")
        req_type = current_request_details.get("request_type", "Неизвестно")
        location = current_request_details.get("location", "Не указано")

        admin_user_id = callback_query.from_user.id
        admin_username = callback_query.from_user.username
        admin_fullname = callback_query.from_user.full_name

        db.update_request_status(request_id, new_status, admin_user_id, admin_username, admin_fullname)

        updated_request_details = db.get_request_details(request_id)
        if updated_request_details:
            req_id = updated_request_details.get("id", "N/A")
            status = updated_request_details.get("status", "N/A")

            status_ru = txt.STATUS_MAP_RU.get(status, status)
            await callback_query.answer(txt.ADMIN_STATUS_UPDATED_ANSWER_TEMPLATE.format(request_id=req_id, status_ru=status_ru))

            if teacher_id:
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

                    if new_status == 'completed':
                         rating_message_text = txt.TEACHER_RATING_REQUEST_TEMPLATE.format(
                             request_id=req_id,
                             request_type=escape_html(req_type),
                             location=escape_html(location)
                         )
                         rating_keyboard = kb.get_rating_keyboard(req_id)

                         await bot.send_message(
                             teacher_id,
                             rating_message_text,
                             reply_markup=rating_keyboard,
                             parse_mode=ParseMode.HTML
                         )

                except Exception as e:
                    logger.error(f"Не удалось уведомить учителя {teacher_id} или запросить оценку для заявки {req_id}: {e}")

            await admin_view_request_details(callback_query)

        else:
            await callback_query.answer(txt.ADMIN_REQUEST_NOT_FOUND, show_alert=True)
            await admin_view_open_requests(callback_query)

    except Exception as e:
         logger.error(f"Ошибка при смене статуса заявки: {e}")
         await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)

@router.callback_query(F.data == "admin_manage_admins")
@admin_callback_required
async def admin_manage_admins(callback_query: types.CallbackQuery):
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
    await callback_query.message.edit_text(txt.ADMIN_ADD_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_admin_id_to_add)
    await callback_query.answer()

@router.message(AdminStates.waiting_for_admin_id_to_add)
@admin_required
async def admin_add_process(message: types.Message, state: FSMContext, bot: Bot):
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
    await callback_query.message.edit_text(txt.ADMIN_REMOVE_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_admin_id_to_remove)
    await callback_query.answer()

@router.message(AdminStates.waiting_for_admin_id_to_remove)
@admin_required
async def admin_remove_process(message: types.Message, state: FSMContext, bot: Bot):
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

@router.callback_query(F.data == "admin_manage_teachers")
@admin_callback_required
async def admin_manage_teachers(callback_query: types.CallbackQuery):
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
    await callback_query.message.edit_text(txt.ADMIN_ADD_TEACHER_PROMPT)
    await state.set_state(AdminStates.waiting_for_teacher_id_to_add)
    await callback_query.answer()

@router.message(AdminStates.waiting_for_teacher_id_to_add)
@admin_required
async def teacher_add_process(message: types.Message, state: FSMContext, bot: Bot):
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
    await callback_query.message.edit_text(txt.ADMIN_REMOVE_TEACHER_PROMPT)
    await state.set_state(AdminStates.waiting_for_teacher_id_to_remove)
    await callback_query.answer()

@router.message(AdminStates.waiting_for_teacher_id_to_remove)
@admin_required
async def teacher_remove_process(message: types.Message, state: FSMContext, bot: Bot):
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

@router.callback_query(F.data == "admin_view_completed_requests")
@admin_callback_required
async def admin_view_completed_requests(callback_query: types.CallbackQuery):
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

    requests_kb = kb.build_requests_list_kb(requests)

    await callback_query.message.edit_text(
        text,
        reply_markup=requests_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()

@router.callback_query(F.data == "admin_view_all_requests")
@admin_callback_required
async def admin_view_all_requests(callback_query: types.CallbackQuery):
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
        taken_by_id = req.get("taken_by_id")
        taken_by_username = req.get("taken_by_username")
        taken_by_fullname = req.get("taken_by_fullname", "Неизвестно")


        username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
        completed_at_formatted = completed_at if completed_at else 'еще нет'
        status_ru = txt.STATUS_MAP_RU.get(status, status)

        taken_by_info = ""
        if taken_by_id:
             taken_by_username_mention = f', @{escape_html(taken_by_username)}' if taken_by_username else ''
             taken_by_info = txt.ADMIN_TAKEN_BY_TEMPLATE.format(
                  admin_fullname=escape_html(taken_by_fullname),
                  admin_id=taken_by_id,
                  username_mention=taken_by_username_mention
             )


        history_text = txt.ADMIN_HISTORY_ITEM_TEMPLATE.format(
             request_id=req_id,
             request_type=escape_html(req_type),
             location=escape_html(location),
             teacher_fullname=escape_html(teacher_fullname),
             teacher_id=teacher_id,
             username_mention=username_mention,
             status_ru=status_ru,
             created_at=created_at,
             completed_at_formatted=completed_at_formatted
        )
        text += history_text + taken_by_info + "\n---\n"


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

@router.callback_query(F.data == "admin_clear_history_start")
@admin_callback_required
async def admin_clear_history_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not db.get_all_requests():
         await callback_query.message.edit_text(txt.ADMIN_CLEAR_HISTORY_NO_DATA, reply_markup=kb.get_admin_menu_kb())
         await callback_query.answer()
         return

    await callback_query.message.edit_text(
        txt.ADMIN_CLEAR_HISTORY_CONFIRM_PROMPT,
        reply_markup=kb.get_clear_history_confirmation_kb()
    )
    await state.set_state(AdminStates.waiting_for_clear_history_confirmation)
    await callback_query.answer()

@router.callback_query(AdminStates.waiting_for_clear_history_confirmation, F.data == "admin_clear_history_confirm_yes")
@admin_callback_required
async def admin_clear_history_confirm_yes(callback_query: types.CallbackQuery, state: FSMContext):
    count_removed = db.clear_all_requests()
    await state.clear()

    await callback_query.message.edit_text(
        txt.ADMIN_CLEAR_HISTORY_SUCCESS,
        reply_markup=kb.get_admin_menu_kb()
    )
    await callback_query.answer("История очищена.")

@router.callback_query(AdminStates.waiting_for_clear_history_confirmation, F.data == "admin_clear_history_confirm_no")
@admin_callback_required
async def admin_clear_history_confirm_no(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback_query.message.edit_text(
        txt.ADMIN_CLEAR_HISTORY_CANCELLED,
        reply_markup=kb.get_admin_menu_kb()
    )
    await callback_query.answer("Очистка отменена.")

@router.callback_query(F.data == "admin_export_history")
@admin_callback_required
async def admin_export_history(callback_query: types.CallbackQuery, bot: Bot):
    formatted_history = db.get_all_requests_formatted()

    if formatted_history == txt.ADMIN_EXPORT_HISTORY_NO_DATA or not formatted_history.strip():
         await callback_query.message.edit_text(txt.ADMIN_EXPORT_HISTORY_NO_DATA, reply_markup=kb.get_admin_menu_kb())
         await callback_query.answer()
         return

    await callback_query.answer("Подготовка файла...", show_alert=True)

    file_content = formatted_history.encode('utf-8')
    file_io = BytesIO(file_content)
    file_io.name = f"{txt.ADMIN_EXPORT_HISTORY_FILE_TITLE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    try:
         await bot.send_document(
             chat_id=callback_query.message.chat.id,
             document=BufferedInputFile(file_io.getvalue(), filename=file_io.name)
         )
         await callback_query.message.edit_text(
             f"📥 История заявок экспортирована в файл `{escape_html(file_io.name)}`.",
             reply_markup=kb.get_admin_menu_kb(),
             parse_mode=ParseMode.HTML
         )

    except Exception as e:
         logger.error(f"Ошибка при экспорте истории: {e}")
         await callback_query.message.edit_text(txt.ADMIN_ACTION_ERROR, reply_markup=kb.get_admin_menu_kb())

@router.callback_query(F.data.startswith("manual_status_start_"))
@admin_callback_required
async def admin_manual_status_start(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        request_id = int(callback_query.data.split("_")[3])
        request = db.get_request_details(request_id)

        if not request:
            await callback_query.answer(txt.ADMIN_MANUAL_STATUS_REQUEST_NOT_FOUND.format(request_id=request_id), show_alert=True)
            await admin_view_open_requests(callback_query)
            return

        await state.update_data(manual_status_request_id=request_id)
        await state.set_state(AdminStates.waiting_for_manual_status_selection)

        await callback_query.message.edit_text(
            txt.ADMIN_MANUAL_STATUS_PROMPT.format(request_id=request_id),
            reply_markup=kb.get_manual_status_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()

    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for manual status start: {callback_query.data} - {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)
    except Exception as e:
        logger.error(f"Error starting manual status change for callback {callback_query.data}: {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)


@router.callback_query(AdminStates.waiting_for_manual_status_selection, F.data.startswith("manual_status_"))
@admin_callback_required
async def admin_manual_status_process(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback_query.data.split("_")
        if len(parts) != 3:
             raise ValueError("Invalid manual status callback data format")

        new_status = parts[2]

        valid_statuses = ['open', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status selected: {new_status}")

        user_data = await state.get_data()
        request_id = user_data.get('manual_status_request_id')

        if request_id is None:
             logger.error("Manual status state data missing request_id")
             await state.clear()
             await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)
             await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
             return

        admin_user_id = callback_query.from_user.id
        admin_username = callback_query.from_user.username
        admin_fullname = callback_query.from_user.full_name

        db.update_request_status(request_id, new_status, admin_user_id, admin_username, admin_fullname)

        updated_request = db.get_request_details(request_id)
        status_ru = txt.STATUS_MAP_RU.get(new_status, new_status)

        await state.clear()

        if updated_request:
             confirm_text = txt.ADMIN_MANUAL_STATUS_SUCCESS_TEMPLATE.format(
                 request_id=request_id,
                 status_ru=status_ru
             )
             await callback_query.message.edit_text(
                  f"{confirm_text}\n\n{txt.ADMIN_PANEL_MESSAGE}",
                  reply_markup=kb.get_admin_menu_kb(),
                  parse_mode=ParseMode.HTML
             )
             await callback_query.answer(f"Статус изменен на '{status_ru}'", show_alert=True)

             if new_status == 'completed':
                 teacher_id = updated_request.get("teacher_id")
                 if teacher_id:
                     try:
                         rating_message_text = txt.TEACHER_RATING_REQUEST_TEMPLATE.format(
                             request_id=request_id,
                             request_type=escape_html(updated_request.get("request_type", "Неизвестно")),
                             location=escape_html(updated_request.get("location", "Не указано"))
                         )
                         rating_keyboard = kb.get_rating_keyboard(request_id)
                         await bot.send_message(
                             teacher_id,
                             rating_message_text,
                             reply_markup=rating_keyboard,
                             parse_mode=ParseMode.HTML
                         )
                     except Exception as e:
                         logger.error(f"Failed to send rating request to teacher {teacher_id} after manual completion of request {request_id}: {e}")

        else:
             await callback_query.answer(txt.ADMIN_MANUAL_STATUS_REQUEST_NOT_FOUND.format(request_id=request_id), show_alert=True)
             await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for manual status process: {callback_query.data} - {e}")
        await state.clear()
        await callback_query.answer("Некорректный выбор статуса.", show_alert=True)
        await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
    except Exception as e:
        logger.error(f"Error processing manual status change for callback {callback_query.data}: {e}")
        await state.clear()
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)
        await callback_query.message.edit_text(txt.ADMIN_PANEL_MESSAGE, reply_markup=kb.get_admin_menu_kb())
