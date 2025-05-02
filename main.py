import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Импортируем конфигурацию, хранилище и роутеры хэндлеров
import config
import json_storage as db # Импортируем json_storage как db для совместимости с хэндлерами
from handlers import user, admin # Импортируем роутеры из поддиректории handlers


async def main():
    """Главная функция запуска бота."""
    # Настройка логирования. Уровень берется из config.py
    logging.basicConfig(
        level=logging.getLevelName(config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logger = logging.getLogger(__name__)

    # Инициализация хранилища JSON. Загружает данные или создает новый файл, добавляет начальных админов/учителей.
    db.init_storage()
    logger.info("Storage initialized.")

    # Инициализация бота. Используем токен из config.py
    # Настраиваем HTML парсинг по умолчанию для всех сообщений через DefaultBotProperties
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Инициализация диспетчера, который будет принимать и обрабатывать обновления
    dp = Dispatcher()

    # Включаем роутеры хэндлеров в основной диспетчер.
    # Хэндлеры из user.py будут обрабатывать пользовательские команды и FSM заявки.
    # Хэндлеры из admin.py будут обрабатывать админские команды и действия.
    dp.include_router(user.router)
    dp.include_router(admin.router)

    # Запускаем поллинг бота. Бот будет слушать обновления от Telegram.
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Точка входа при запуске скрипта
    # Запускаем асинхронную функцию main()
    try:
        asyncio.run(main())
    # Обработка стандартных сигналов прерывания (Ctrl+C)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
    # Обработка любых других исключений верхнего уровня
    except Exception:
        # Логируем подробную информацию об ошибке
        logging.exception("Bot stopped with an error:")
