import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from typing import Dict, Any, Tuple

from states import SupportStaffStates
import keyboards as kb
import texts as txt
import json_storage as db
from utils import escape_html

router = Router()
logger = logging.getLogger(__name__)

def support_staff_required(func):
    async def wrapper(event: types.Message | types.CallbackQuery, bot: Bot, state: FSMContext, **kwargs: Dict[str, Any]):
        user_id = event.from_user.id
        is_staff = db.is_support_staff(user_id)
        is_admin = db.is_admin(user_id)

        if not is_staff and not is_admin:
            if isinstance(event, types.Message):
                await event.reply(txt.ACCESS_DENIED_SUPPORT_STAFF)
            elif isinstance(event, types.CallbackQuery):
                await event.answer(txt.ACCESS_DENIED_SUPPORT_STAFF, show_alert=True)
            return

        try:
            # Передаем все аргументы, включая те, что добавил декоратор
            # Функция func должна принимать все эти аргументы
            return await func(event, bot=bot, state=state, user_id=user_id, is_admin=is_admin, is_support_staff=is_staff, **kwargs)
        except TypeError as e:
            logger.error(f"Error calling handler {func.__name__} inside support_staff_required: {e}")
            # Проверяем, что state не None перед вызовом clear
            if state and isinstance(state, FSMContext):
                try:
                    await state.clear()
                except Exception as clear_e:
                     logger.error(f"Error clearing state in support_staff_required error handler: {clear_e}")
            try:
                if isinstance(event, types.Message):
                    await event.reply(txt.ADMIN_ACTION_ERROR) # Возможно, стоит использовать другой текст для ИТ-специалистов
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(txt.ADMIN_ACTION_ERROR, show_alert=True) # Возможно, стоит использовать другой текст
            except Exception as reply_e:
                logger.error(f"Error sending error message in support_staff_required error handler: {reply_e}")


    wrapper.__wrapped__ = func
    return wrapper


# --- Обновляем сигнатуры хэндлеров для приема аргументов от декоратора ---

@router.message(Command("it_panel"))
@support_staff_required
async def handle_support_staff_panel(message: types.Message, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    await message.reply(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())

@router.callback_query(F.data == "support_staff")
@support_staff_required
async def handle_support_staff_callback(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    await callback_query.message.edit_text(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())
    await callback_query.answer()

@router.callback_query(F.data == "support_staff_view_available")
@support_staff_required
async def support_staff_view_available_requests(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    requests = db.get_available_requests()

    if not requests:
        await callback_query.message.edit_text(txt.SUPPORT_STAFF_NO_AVAILABLE_REQUESTS, reply_markup=kb.get_back_to_support_staff_menu_kb())
        await callback_query.answer()
        return

    text = txt.SUPPORT_STAFF_AVAILABLE_REQUESTS_LIST_TEMPLATE
    for req in requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        created_at = req.get("created_at", "N/A")

        text += f"№{req_id}: {escape_html(req_type)} в {escape_html(location)} ({created_at})\n"


    requests_kb = kb.build_available_requests_kb(requests)

    await callback_query.message.edit_text(
        text,
        reply_markup=requests_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()

@router.callback_query(F.data == "support_staff_view_taken")
@support_staff_required
async def support_staff_view_taken_requests(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    requests = db.get_requests_taken_by(user_id)

    if not requests:
        await callback_query.message.edit_text(txt.SUPPORT_STAFF_NO_TAKEN_REQUESTS, reply_markup=kb.get_back_to_support_staff_menu_kb())
        await callback_query.answer()
        return

    text = txt.SUPPORT_STAFF_TAKEN_REQUESTS_LIST_TEMPLATE
    for req in requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        status = req.get("status", "N/A")
        status_ru = txt.STATUS_MAP_RU.get(status, status)
        created_at = req.get("created_at", "N/A")

        text += f"№{req_id}: {escape_html(req_type)} в {escape_html(location)} ({status_ru}, Создана: {created_at})\n"

    requests_kb = kb.build_taken_requests_kb(requests)

    await callback_query.message.edit_text(
        text,
        reply_markup=requests_kb,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("view_request_"))
@support_staff_required
async def support_staff_view_request_details(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    try:
        request_id = int(callback_query.data.split("_")[2])
        request = db.get_request_details(request_id)

        if not request:
            await callback_query.answer(txt.SUPPORT_STAFF_REQUEST_NOT_FOUND, show_alert=True)
            await callback_query.message.edit_text(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())
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
        rating = request.get("rating")

        username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
        status_ru = txt.STATUS_MAP_RU.get(status, status)

        taken_by_info = ""
        if taken_by_id:
             taken_by_username_mention = f', @{escape_html(taken_by_username)}' if taken_by_username else ''
             taken_by_info = txt.TAKEN_BY_INFO_TEMPLATE.format(
                 fullname=escape_html(taken_by_fullname),
                 user_id=taken_by_id,
                 username_mention=taken_by_username_mention
             )

        text = txt.SUPPORT_STAFF_REQUEST_DETAILS_TEMPLATE.format(
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
            completed_at=completed_at,
            taken_by_info=taken_by_info
        )
        if rating is not None:
             text += f"\nОценка: {rating}"


        details_kb = kb.get_request_details_kb(req_id, status, user_role='support_staff')

        await callback_query.message.edit_text(
            text,
            reply_markup=details_kb,
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()

    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for view_request_: {callback_query.data} - {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True) # Возможно, использовать текст для ИТ
    except Exception as e:
        logger.error(f"Error viewing request details for callback {callback_query.data}: {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True) # Возможно, использовать текст для ИТ


@router.callback_query(F.data.startswith("take_request_"))
@support_staff_required
async def support_staff_take_request(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    try:
        request_id = int(callback_query.data.split("_")[2])
        user = callback_query.from_user

        success, message = db.take_request_in_progress(request_id, user.id, user.username, user.full_name)

        if success:
            await callback_query.answer(txt.SUPPORT_STAFF_REQUEST_TAKEN_SUCCESS.format(request_id=request_id), show_alert=True)

            updated_request = db.get_request_details(request_id)
            if updated_request:
                req_id = updated_request.get("id", "N/A")
                status = updated_request.get("status", "N/A")
                status_ru = txt.STATUS_MAP_RU.get(status, status)
                taken_by_id = updated_request.get("taken_by_id")
                taken_by_username = updated_request.get("taken_by_username")
                taken_by_fullname = updated_request.get("taken_by_fullname", "Неизвестно")
                rating = updated_request.get("rating")

                taken_by_info = ""
                if taken_by_id:
                     taken_by_username_mention = f', @{escape_html(taken_by_username)}' if taken_by_username else ''
                     taken_by_info = txt.TAKEN_BY_INFO_TEMPLATE.format(
                         fullname=escape_html(taken_by_fullname),
                         user_id=taken_by_id,
                         username_mention=taken_by_username_mention
                     )

                text = txt.SUPPORT_STAFF_REQUEST_DETAILS_TEMPLATE.format(
                    request_id=req_id,
                    status_ru=status_ru,
                    teacher_fullname=escape_html(updated_request.get("teacher_fullname", "Не указано")),
                    teacher_id=updated_request.get("teacher_id", "N/A"),
                    username_mention=f', @{escape_html(updated_request.get("teacher_username"))}' if updated_request.get("teacher_username") else '',
                    contact_name=escape_html(updated_request.get("contact_name", "Не указано")),
                    request_type=escape_html(updated_request.get("request_type", "Неизвестно")),
                    location=escape_html(updated_request.get("location", "Не указано")),
                    description=escape_html(updated_request.get("description", "Нет описания")),
                    created_at=updated_request.get("created_at", "N/A"),
                    completed_at=updated_request.get("completed_at", "еще нет"),
                    taken_by_info=taken_by_info
                )
                if rating is not None:
                     text += f"\nОценка: {rating}"


                details_kb = kb.get_request_details_kb(req_id, status, user_role='support_staff')

                await callback_query.message.edit_text(
                    text,
                    reply_markup=details_kb,
                    parse_mode=ParseMode.HTML
                )
            else:
                await callback_query.message.edit_text(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())


        else:
            await callback_query.answer(message, show_alert=True)
            # После неудачной попытки взять заявку, остаемся в деталях (если были там)
            # Или возвращаемся в меню доступных, если кнопка была там
            current_request = db.get_request_details(request_id)
            if current_request and current_request.get("status") == 'open': # Если заявка еще открыта
                 await support_staff_view_request_details(callback_query, bot, state, user_id, is_admin, is_support_staff)
            else: # Иначе, возможно, она уже взята или ее статус изменился
                 await handle_support_staff_callback(callback_query, bot, state, user_id, is_admin, is_support_staff)


    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for take_request_: {callback_query.data} - {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True) # Возможно, использовать текст для ИТ
    except Exception as e:
        logger.error(f"Error taking request for callback {callback_query.data}: {e}")
        await callback_query.answer(txt.SUPPORT_STAFF_REQUEST_TAKE_ERROR.format(request_id=request_id if 'request_id' in locals() else 'N/A'), show_alert=True)


@router.callback_query(F.data.startswith("update_status_"))
@support_staff_required
async def support_staff_update_request_status(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, user_id: int, is_admin: bool, is_support_staff: bool):
    try:
        parts = callback_query.data.split("_")
        if len(parts) != 4:
             raise ValueError("Invalid callback data format for status update")

        request_id = int(parts[2])
        new_status = parts[3]

        allowed_statuses_from_inprogress = ['completed', 'cancelled']
        if new_status not in allowed_statuses_from_inprogress:
            await callback_query.answer("Недопустимый статус для изменения.", show_alert=True)
            return

        current_request_details = db.get_request_details(request_id)
        if not current_request_details:
            await callback_query.answer(txt.SUPPORT_STAFF_REQUEST_NOT_FOUND, show_alert=True)
            await callback_query.message.edit_text(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())
            return

        # Проверка, что заявка взята именно этим специалистом
        if current_request_details.get("taken_by_id") != user_id:
            await callback_query.answer(txt.SUPPORT_STAFF_STATUS_CHANGE_NOT_TAKEN, show_alert=True)
            await support_staff_view_request_details(callback_query, bot, state, user_id, is_admin, is_support_staff) # Возвращаемся в детали
            return

        # Проверка, что текущий статус - в работе
        if current_request_details.get("status") != 'in_progress':
            await callback_query.answer("Статус заявки должен быть 'В работе' для изменения.", show_alert=True)
            await support_staff_view_request_details(callback_query, bot, state, user_id, is_admin, is_support_staff) # Возвращаемся в детали
            return


        user = callback_query.from_user
        db.update_request_status(request_id, new_status, user.id, user.username, user.full_name)


        updated_request_details = db.get_request_details(request_id)
        if updated_request_details:
            req_id = updated_request_details.get("id", "N/A")
            status = updated_request_details.get("status", "N/A")
            status_ru = txt.STATUS_MAP_RU.get(status, status)

            await callback_query.answer(txt.SUPPORT_STAFF_STATUS_UPDATED_ANSWER_TEMPLATE.format(request_id=req_id, status_ru=status_ru), show_alert=True)

            # Уведомляем учителя только при завершении
            if new_status == 'completed':
                 teacher_id = updated_request_details.get("teacher_id")
                 if teacher_id:
                     try:
                         await bot.send_message(
                             teacher_id,
                             txt.ADMIN_NOTIFY_TEACHER_STATUS_TEMPLATE.format( # Используем тот же шаблон
                                 request_id=req_id,
                                 request_type=escape_html(updated_request_details.get("request_type", "Неизвестно")),
                                 location=escape_html(updated_request_details.get("location", "Не указано")),
                                 status_ru=status_ru
                             ),
                             parse_mode=ParseMode.HTML
                         )
                         # Отправляем запрос на оценку только при завершении
                         rating_message_text = txt.TEACHER_RATING_REQUEST_TEMPLATE.format(
                             request_id=req_id,
                             request_type=escape_html(updated_request_details.get("request_type", "Неизвестно")),
                             location=escape_html(updated_request_details.get("location", "Не указано"))
                         )
                         rating_keyboard = kb.get_rating_keyboard(req_id)
                         await bot.send_message(
                             teacher_id,
                             rating_message_text,
                             reply_markup=rating_keyboard,
                             parse_mode=ParseMode.HTML
                         )
                     except Exception as e:
                         logger.error(f"Не удалось уведомить учителя {teacher_id} или запросить оценку для заявки {req_id} после смены статуса эникейщиком: {e}")


            # После смены статуса, возвращаемся к деталям заявки для обновления UI
            # Если статус стал completed/cancelled, ее уже не будет в списке "В работе"
            # Возвращаемся к общему меню ИТ-специалиста
            if new_status in ['completed', 'cancelled']:
                 await handle_support_staff_callback(callback_query, bot, state, user_id, is_admin, is_support_staff)
            else: # Если статус изменился, но не на конечный, остаемся в деталях (теоретически статус может быть сменен на open админом)
                 await support_staff_view_request_details(callback_query, bot, state, user_id, is_admin, is_support_staff)


        else:
            await callback_query.answer(txt.SUPPORT_STAFF_REQUEST_NOT_FOUND, show_alert=True)
            await callback_query.message.edit_text(txt.SUPPORT_STAFF_PANEL_MESSAGE, reply_markup=kb.get_support_staff_menu_kb())


    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for update_status_: {callback_query.data} - {e}")
        await callback_query.answer("Некорректный запрос на смену статуса.", show_alert=True) # Возможно, использовать текст для ИТ
    except Exception as e:
        logger.error(f"Error updating status for callback {callback_query.data}: {e}")
        await callback_query.answer(txt.SUPPORT_STAFF_STATUS_CHANGE_ERROR.format(request_id=request_id if 'request_id' in locals() else 'N/A'), show_alert=True)
