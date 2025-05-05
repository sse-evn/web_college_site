# -*- coding: utf-8 -*-

import logging
import requests
import urllib.parse # Импортируем для URL-экранирования, хотя в данном случае можно обойтись
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


# !!! Вставьте сюда свой токен бота Telegram !!!
TELEGRAM_BOT_TOKEN = "7835804770:AAFya70UvrONYGySq5VSaAgvjQVFOI4LreI"

# !!! Вставьте сюда свой токен API Clash Royale !!!
# Убедитесь, что этот токен имеет доступ к IP-адресу, с которого вы запускаете бота.
CLASH_ROYALE_API_TOKEN = "eaf342dz" # Например: "eaf342dz"

# Базовый URL API Clash Royale
CLASH_ROYALE_API_URL = "https://api.clashroyale.com/v1"

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Уменьшаем шум от библиотеки requests, используя её внутреннее логирование
# logging.getLogger("httpx").setLevel(logging.WARNING) # Если используете requests 2.28.1 или новее, он использует httpx
# Для более старых версий requests или общего случая:
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Заголовки для запросов к API Clash Royale
API_HEADERS = {
    "Authorization": "Bearer {}".format(CLASH_ROYALE_API_TOKEN)
}

# --- Функции-обработчики команд ---

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    await update.message.reply_text(
        "Привет! Я бот, который может получить статистику игрока Clash Royale.\n"
        "Используйте команду /player <тег_игрока>\n"
        "Пример: /player #ABCD123"
    )

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с помощью при команде /help."""
    await update.message.reply_text(
        "Для получения статистики игрока используйте команду:\n"
        "/player <тег_игрока>\n"
        "Пример: /player #ABCD123"
    )

# Обработчик команды /player
async def player_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получает и отправляет статистику игрока по его тегу."""
    # Получаем аргументы после команды /player
    args = context.args

    if not args:
        await update.message.reply_text(
            "Пожалуйста, укажите тег игрока после команды /player.\n"
            "Пример: /player #ABCD123"
        )
        return

    # Объединяем аргументы, чтобы получить весь тег (на случай, если он разделен пробелами)
    player_tag = "".join(args)

    # Проверяем, что тег начинается с # (добавляем, если отсутствует)
    if not player_tag.startswith("#"):
        player_tag = "#" + player_tag

    # URL для запроса статистики игрока
    # Тег нужно URL-экранировать. Символ '#' экранируется как %23.
    # Остальную часть тега (после #) тоже нужно экранировать на всякий случай.
    encoded_tag_part = urllib.parse.quote(player_tag[1:])
    player_url = "{}/players/%23{}".format(CLASH_ROYALE_API_URL, encoded_tag_part)


    logger.info("Запрос статистики для игрока: {}".format(player_tag)) # И здесь тоже .format()

    try:
        # Отправляем GET-запрос к API Clash Royale
        response = requests.get(player_url, headers=API_HEADERS)
        response.raise_for_status() # Вызовет исключение для плохих статусов ответа (4xx или 5xx)

        player_data = response.json()

        # --- Форматирование ответа ---
        # Используем форматирование через .format() вместо f-строк
        name = player_data.get("name", "Неизвестно")
        tag = player_data.get("tag", "Неизвестно")
        trophies = player_data.get("trophies", 0)
        best_trophies = player_data.get("bestTrophies", 0)
        level = player_data.get("expLevel", 1)
        arena = player_data.get("arena", {}).get("name", "Неизвестно")
        total_donations = player_data.get("totalDonations", 0)
        wins = player_data.get("wins", 0)
        losses = player_data.get("losses", 0)
        battles = wins + losses
        win_rate = (wins / battles * 100) if battles > 0 else 0

        clan_info = player_data.get("clan")
        clan_name = clan_info.get("name", "Нет клана") if clan_info else "Нет клана"

        reply_text = (
            "📊 **Статистика игрока:**\n"
            "👤 Имя: {}\n"
            "🏷️ Тег: `{}`\n"
            "🏆 Кубки: {} (Рекорд: {})\n"
            "👑 Уровень: {}\n"
            "🏟️ Арена: {}\n"
            "⚔️ Боев сыграно: {}\n"
            "✅ Побед: {}\n"
            "❌ Поражений: {}\n"
            "📊 Процент побед: {:.2f}%\n" # Форматирование числа с плавающей точкой внутри format
            "🤝 Всего пожертвоний: {}\n"
            "🏠 Клан: {}".format(
                name,
                tag,
                trophies,
                best_trophies,
                level,
                arena,
                battles,
                wins,
                losses,
                win_rate,
                total_donations,
                clan_name
            )
        )


        await update.message.reply_text(reply_text, parse_mode="Markdown")

    except requests.exceptions.HTTPError as e:
        # Обработка ошибок HTTP (например, 404 Not Found, 403 Forbidden)
        status_code = response.status_code if 'response' in locals() else 'Неизвестно'
        if status_code == 404:
            await update.message.reply_text("Игрок с тегом `{}` не найден.".format(player_tag)) # И здесь .format()
        elif status_code == 403:
             await update.message.reply_text(
                 "Ошибка доступа к API. Проверьте ваш токен ({}). ".format(status_code) +
                 "Возможно, IP-адрес, с которого вы запускаете бота, не привязан к токену на сайте Supercell Developer."
             )
        elif status_code == 429:
             await update.message.reply_text(
                 "Превышен лимит запросов к API. Попробуйте позже ({}).".format(status_code)
             )
        else:
            await update.message.reply_text("Произошла ошибка при запросе к API ({}): {}".format(status_code, e))
        logger.error("HTTP ошибка для игрока {}: {}".format(player_tag, e)) # И здесь .format()

    except requests.exceptions.RequestException as e:
        # Обработка других ошибок запроса (например, проблемы с сетью)
        await update.message.reply_text("Произошла ошибка при подключении к API: {}".format(e)) # И здесь .format()
        logger.error("Ошибка запроса для игрока {}: {}".format(player_tag, e)) # И здесь .format()

    except Exception as e:
        # Обработка любых других неожиданных ошибок
        await update.message.reply_text("Произошла внутренняя ошибка: {}".format(e)) # И здесь .format()
        logger.error("Неожиданная ошибка для игрока {}: {}".format(player_tag, e)) # И здесь .format()


# Обработчик любых других сообщений (опционально)
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отвечает на неизвестные команды."""
    await update.message.reply_text(
        "Извините, я не понимаю эту команду. "
        "Используйте /help для списка доступных команд."
    )

# --- Основная функция запуска бота ---
def main() -> None:
    """Запускает бота."""
    # Создаем экземпляр Application и передаем токен бота
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("player", player_stats_command))

    # Добавляем обработчик для неизвестных команд (должен быть последним)
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(poll_interval=3) # Проверяем обновления каждые 3 секунды

# Запускаем главную функцию
if __name__ == "__main__":
    main()
