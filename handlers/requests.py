# handlers/requests.py
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from typing import List, Dict, Any

import keyboards as kb
import texts as txt
import json_storage as db
import config
from utils import escape_html # <-- Вот эта строка должна быть такой

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list"))
async def handle_list(message: types.Message):
    user_id = message.from_user.id

    if not db.is_teacher_allowed(user_id):
        await message.reply(txt.ACCESS_DENIED_TEACHER)
        return

    active_requests = db.get_user_active_requests(user_id)

    if not active_requests:
        await message.reply(txt.TEACHER_NO_ACTIVE_REQUESTS)
        return

    text = txt.TEACHER_ACTIVE_REQUESTS_LIST_TEMPLATE

    for req in active_requests:
        req_id = req.get("id", "N/A")
        req_type = req.get("request_type", "Неизвестно")
        location = req.get("location", "Не указано")
        status = req.get("status", "N/A")
        created_at = req.get("created_at", "N/A")

        status_ru = txt.STATUS_MAP_RU.get(status, status)

        text += f"№{req_id}: {escape_html(req_type)} в {escape_html(location)}\n"
        text += f"Статус: *{status_ru}*\n"
        text += f"Создана: {created_at}\n---\n"

    await message.reply(text.strip(), parse_mode=ParseMode.HTML)
