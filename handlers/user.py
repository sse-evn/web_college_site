import logging
import re
from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime
from typing import Dict, Any

from states import RequestStates
import keyboards as kb
import texts as txt
import json_storage as db
import config
from utils import escape_html

router = Router()
logger = logging.getLogger(__name__)

def escape_html(text: str) -> str:
    if text is None:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not db.is_teacher_allowed(user_id):
        await message.reply(txt.ACCESS_DENIED_TEACHER)
        await state.clear()
        return

    await message.reply(txt.START_MESSAGE, reply_markup=kb.get_request_types_kb())
    await state.set_state(RequestStates.waiting_for_type)

@router.message(Command("new_request"))
async def handle_new_request(message: types.Message, state: FSMContext):
    await handle_start(message, state)

@router.message(RequestStates.waiting_for_type)
async def process_request_type(message: types.Message, state: FSMContext):
    if message.text:
        if message.text == "❌ Отмена":
            await state.clear()
            await message.reply(txt.CANCEL_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
            return

        expected_types = ["💻 ПК", "🖨️ Принтер", "📽️ Проектор", "🖥️ Интерактивная доска", "🔄 Другое"]

        if message.text in expected_types:
            await state.update_data(request_type=message.text)
            await message.reply(txt.LOCATION_PROMPT, reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(RequestStates.waiting_for_location)
            return

    await message.reply("Пожалуйста, выберите тип из предложенных кнопок.", reply_markup=kb.get_request_types_kb())

@router.message(RequestStates.waiting_for_location)
async def process_request_location(message: types.Message, state: FSMContext):
    if not message.text:
        await message.reply("Пожалуйста, введите номер кабинета или местоположение текстом.")
        return

    await state.update_data(location=message.text)
    await message.reply(txt.NAME_PROMPT)
    await state.set_state(RequestStates.waiting_for_name)

@router.message(RequestStates.waiting_for_name)
async def process_request_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.reply("Пожалуйста, введите ваше имя текстом.")
        return

    await state.update_data(contact_name=message.text)
    await message.reply(txt.DESCRIPTION_PROMPT)
    await state.set_state(RequestStates.waiting_for_description)

@router.message(RequestStates.waiting_for_description)
async def process_request_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not db.is_teacher_allowed(user_id):
        await state.clear()
        await message.reply(txt.ACCESS_DENIED_TEACHER)
        return

    if not message.text:
        await message.reply("Пожалуйста, опишите проблему текстом.")
        return

    await state.update_data(description=message.text)

    user_data = await state.get_data()
    request_type = user_data.get('request_type')
    location = user_data.get('location')
    contact_name = user_data.get('contact_name')
    description = user_data.get('description')

    confirmation_text = txt.CONFIRMATION_TEXT_TEMPLATE.format(
        request_type=escape_html(request_type),
        location=escape_html(location),
        contact_name=escape_html(contact_name),
        description=escape_html(description)
    )

    await message.reply(confirmation_text, reply_markup=kb.get_confirm_request_kb(), parse_mode=ParseMode.HTML)
    await state.set_state(RequestStates.confirm_request)

@router.callback_query(RequestStates.confirm_request, F.data == "confirm_request_yes")
async def confirm_request_yes(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id

    if not db.is_teacher_allowed(user_id):
        await state.clear()
        await callback_query.message.edit_text(txt.ACCESS_DENIED_TEACHER)
        await callback_query.answer()
        return

    user_data = await state.get_data()
    teacher_username = callback_query.from_user.username
    teacher_fullname = callback_query.from_user.full_name

    request_type = user_data.get('request_type')
    location = user_data.get('location')
    contact_name = user_data.get('contact_name')
    description = user_data.get('description')

    request_id = db.add_request(user_id, teacher_username, teacher_fullname,
                                 request_type, description, location, contact_name)

    await callback_query.message.edit_text(txt.REQUEST_ACCEPTED_MESSAGE)

    username_mention = f', @{escape_html(teacher_username)}' if teacher_username else ''
    admin_notification_text = txt.ADMIN_NEW_REQUEST_NOTIFICATION_TEMPLATE.format(
        request_id=request_id,
        teacher_fullname=escape_html(teacher_fullname),
        teacher_id=user_id,
        username_mention=username_mention,
        contact_name=escape_html(contact_name),
        request_type=escape_html(request_type),
        location=escape_html(location),
        description=escape_html(description),
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    try:
        await bot.send_message(
            config.ADMIN_NOTIFICATION_CHAT_ID,
            admin_notification_text,
            reply_markup=kb.get_request_details_kb(request_id, 'open', user_role='admin'),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление администратору {config.ADMIN_NOTIFICATION_CHAT_ID}: {e}")

    await state.clear()
    await callback_query.answer()

@router.callback_query(RequestStates.confirm_request, F.data == "confirm_request_no")
async def confirm_request_no(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(txt.CANCEL_MESSAGE)
    await callback_query.answer()

@router.callback_query(F.data.startswith("rate_"))
async def process_rating_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback_query.data.split("_")
        request_id = int(parts[1])
        rating = int(parts[2])

        if 1 <= rating <= 10:
            success = db.set_request_rating(request_id, rating)

            if success:
                await callback_query.message.edit_text(txt.TEACHER_RATING_THANK_YOU)
                await callback_query.answer(txt.TEACHER_RATING_THANK_YOU)
            else:
                await callback_query.answer(txt.TEACHER_RATING_INVALID_REQUEST, show_alert=True)
        else:
            await callback_query.answer("Некорректная оценка.", show_alert=True)

    except (ValueError, IndexError) as e:
        logger.error(f"Invalid callback data for rating: {callback_query.data} - {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)
    except Exception as e:
        logger.error(f"Error processing rating callback {callback_query.data}: {e}")
        await callback_query.answer(txt.ADMIN_ACTION_ERROR, show_alert=True)
