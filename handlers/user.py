import logging
import re
from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime
from typing import Dict, Any

from states import RequestStates # Импортируем состояния FSM
import keyboards as kb # Импортируем клавиатуры
import texts as txt # Импортируем тексты
import json_storage as db # Импортируем наше JSON хранилище
import config # Импортируем конфигурацию

# Создаем роутер для пользовательских хэндлеров
router = Router()
logger = logging.getLogger(__name__)

# --- Вспомогательная функция для экранирования HTML ---
def escape_html(text: str) -> str:
    """Экранирует специальные символы HTML (<, >, &)."""
    if text is None: # Добавим проверку на None
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# --- Хэндлеры Пользователя ---

# Хэндлер команды /start
@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext): # Добавляем state
    """Обработчик команды /start. Начинает процесс создания заявки."""
    user_id = message.from_user.id

    # Проверяем, разрешено ли этому пользователю создавать заявки
    if not db.is_teacher_allowed(user_id):
        await message.reply(txt.ACCESS_DENIED_TEACHER) # Отправляем сообщение об отсутствии прав
        await state.clear() # На всякий случай очищаем состояние
        return

    # Если разрешено, отправляем приветствие и клавиатуру выбора типа проблемы
    await message.reply(txt.START_MESSAGE, reply_markup=kb.get_request_types_kb())
    # Переводим пользователя в первое состояние FSM
    await state.set_state(RequestStates.waiting_for_type)

# Хэндлер команды /new_request - делает то же самое, что и /start
@router.message(Command("new_request"))
async def handle_new_request(message: types.Message, state: FSMContext):
     """Обработчик команды /new_request. Начинает процесс создания заявки."""
     # Просто вызываем хэндлер handle_start, он выполнит всю нужную логику
     await handle_start(message, state)


# Хэндлер для обработки выбора типа заявки (или отмены)
@router.message(RequestStates.waiting_for_type)
async def process_request_type(message: types.Message, state: FSMContext):
    """Обрабатывает выбор типа заявки."""
    # Проверяем, если сообщение содержит текст
    if message.text:
        # Проверяем, если пользователь нажал кнопку "Отмена"
        # Сравниваем с точным текстом кнопки с эмодзи
        if message.text == "❌ Отмена":
            await state.clear() # Очищаем состояние FSM
            await message.reply(txt.CANCEL_MESSAGE, reply_markup=types.ReplyKeyboardRemove()) # Отправляем сообщение об отмене и убираем Reply-клавиатуру
            return

        # Список ожидаемых текстов кнопок типов заявок (точно как на кнопках с эмодзи)
        # При сравнении можно использовать .lower() для регистронезависимости,
        # но эмодзи могут усложнить это. Сравниваем точный текст кнопки.
        expected_types = ["💻 ПК", "🖨️ Принтер", "📽️ Проектор", "🖥️ Интерактивная доска", "🔄 Другое"]

        # Проверяем, что текст сообщения соответствует одному из ожидаемых текстов кнопок
        if message.text in expected_types:
            # Сохраняем текст кнопки (который теперь включает эмодзи) как тип заявки
            await state.update_data(request_type=message.text)
            # Запрашиваем номер кабинета или местоположение и убираем Reply-клавиатуру
            await message.reply(txt.LOCATION_PROMPT, reply_markup=types.ReplyKeyboardRemove())
            # Переводим FSM в следующее состояние
            await state.set_state(RequestStates.waiting_for_location)
            return # Завершаем обработку, т.к. тип выбран корректно

    # Если введенный текст не является ни "Отмена", ни одним из ожидаемых типов, или если сообщения не было (например, стикер)
    # Просим пользователя выбрать из предложенных кнопок и показываем клавиатуру снова
    await message.reply("Пожалуйста, выберите тип из предложенных кнопок.", reply_markup=kb.get_request_types_kb())
    # Остаемся в текущем состоянии RequestStates.waiting_for_type, ожидая корректный ввод


# Хэндлер для обработки ввода местоположения
@router.message(RequestStates.waiting_for_location)
async def process_request_location(message: types.Message, state: FSMContext):
    """Обрабатывает ввод местоположения."""
    if not message.text: # Проверяем, что сообщение содержит текст
         await message.reply("Пожалуйста, введите номер кабинета или местоположение текстом.")
         return

    # Сохраняем местоположение в контекст FSM
    await state.update_data(location=message.text)
    # Запрашиваем имя контактного лица
    await message.reply(txt.NAME_PROMPT)
    # Переводим FSM в следующее состояние
    await state.set_state(RequestStates.waiting_for_name)

# Хэндлер для обработки ввода имени
@router.message(RequestStates.waiting_for_name)
async def process_request_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод имени человека."""
    if not message.text: # Проверяем, что сообщение содержит текст
         await message.reply("Пожалуйста, введите ваше имя текстом.")
         return

    # Сохраняем имя в контекст FSM
    await state.update_data(contact_name=message.text)
    # Запрашиваем подробное описание проблемы
    await message.reply(txt.DESCRIPTION_PROMPT)
    # Переводим FSM в следующее состояние
    await state.set_state(RequestStates.waiting_for_description)

# Хэндлер для обработки ввода описания проблемы
@router.message(RequestStates.waiting_for_description)
async def process_request_description(message: types.Message, state: FSMContext):
    """Обрабатывает ввод описания проблемы и переходит к подтверждению."""
    user_id = message.from_user.id # Получаем user_id здесь для повторной проверки прав

    # Повторная проверка прав перед сохранением (на всякий случай)
    if not db.is_teacher_allowed(user_id):
        await state.clear() # Очищаем состояние, т.к. прав нет
        await message.reply(txt.ACCESS_DENIED_TEACHER)
        return

    if not message.text: # Проверяем, что сообщение содержит текст
         await message.reply("Пожалуйста, опишите проблему текстом.")
         # Остаемся в этом же состоянии
         return


    # Сохраняем описание в контекст FSM
    await state.update_data(description=message.text)

    # Получаем все данные из контекста FSM для отображения в подтверждении
    user_data = await state.get_data()
    request_type = user_data.get('request_type')
    location = user_data.get('location')
    contact_name = user_data.get('contact_name')
    description = user_data.get('description')

    # Формируем текст подтверждения, экранируя данные пользователя для HTML
    confirmation_text = txt.CONFIRMATION_TEXT_TEMPLATE.format(
        request_type=escape_html(request_type),
        location=escape_html(location),
        contact_name=escape_html(contact_name),
        description=escape_html(description)
    )

    # Отправляем сообщение с собранными данными и Inline-клавиатурой для подтверждения
    await message.reply(confirmation_text, reply_markup=kb.get_confirm_request_kb(), parse_mode=ParseMode.HTML)
    # Переводим FSM в состояние ожидания подтверждения
    await state.set_state(RequestStates.confirm_request)

# Хэндлер для обработки нажатия кнопки "Да, отправить"
@router.callback_query(RequestStates.confirm_request, F.data == "confirm_request_yes")
async def confirm_request_yes(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Подтверждает и отправляет заявку."""
    user_id = callback_query.from_user.id # Получаем ID пользователя из колбэка

    # Повторно проверяем права пользователя перед сохранением заявки (на всякий случай)
    if not db.is_teacher_allowed(user_id):
        await state.clear() # Очищаем состояние
        await callback_query.message.edit_text(txt.ACCESS_DENIED_TEACHER) # Редактируем сообщение об отсутствии прав
        await callback_query.answer() # Закрываем "часики" на кнопке
        return

    # Получаем все данные заявки из контекста FSM
    user_data = await state.get_data()
    teacher_username = callback_query.from_user.username # Получаем username пользователя Telegram
    teacher_fullname = callback_query.from_user.full_name # Получаем полное имя пользователя Telegram

    request_type = user_data.get('request_type')
    location = user_data.get('location')
    contact_name = user_data.get('contact_name')
    description = user_data.get('description')

    # Добавляем заявку в хранилище JSON
    request_id = db.add_request(user_id, teacher_username, teacher_fullname, # Используем user_id
                                 request_type, description, location, contact_name)

    # Сообщаем пользователю, что заявка принята
    await callback_query.message.edit_text(txt.REQUEST_ACCEPTED_MESSAGE)

    # Формируем текст уведомления для администраторов, экранируя данные пользователя
    username_mention = f', @{escape_html(teacher_username)}' if teacher_username else '' # Экранируем username
    admin_notification_text = txt.ADMIN_NEW_REQUEST_NOTIFICATION_TEMPLATE.format(
        request_id=request_id,
        teacher_fullname=escape_html(teacher_fullname), # Экранируем Telegram ФИО
        teacher_id=user_id,
        username_mention=username_mention,
        contact_name=escape_html(contact_name), # Экранируем контактное имя
        request_type=escape_html(request_type), # Экранируем тип
        location=escape_html(location), # Экранируем местоположение
        description=escape_html(description), # Экранируем описание
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Время создания заявки
    )

    # Отправляем уведомление администраторам
    try:
        await bot.send_message(
            config.ADMIN_NOTIFICATION_CHAT_ID, # ID чата админа из config.py
            admin_notification_text,
            # Прикрепляем Inline-клавиатуру для админа, чтобы он мог сразу посмотреть детали
            reply_markup=kb.get_request_details_kb(request_id, 'open'),
            parse_mode=ParseMode.HTML # Используем HTML для разметки
        )
    except Exception as e:
        # Логируем ошибку, если уведомление не отправилось (например, неверный ID чата или админ заблокировал бота)
        logger.error(f"Не удалось отправить уведомление администратору {config.ADMIN_NOTIFICATION_CHAT_ID}: {e}")

    await state.clear() # Очищаем состояние FSM после завершения процесса
    await callback_query.answer() # Закрываем "часики" на кнопке

# Хэндлер для обработки нажатия кнопки "Нет, отменить"
@router.callback_query(RequestStates.confirm_request, F.data == "confirm_request_no")
async def confirm_request_no(callback_query: types.CallbackQuery, state: FSMContext):
    """Отменяет создание заявки."""
    await state.clear() # Очищаем состояние FSM
    await callback_query.message.edit_text(txt.CANCEL_MESSAGE) # Редактируем сообщение об отмене
    await callback_query.answer() # Закрываем "часики" на кнопке
