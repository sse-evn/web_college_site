import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
import json_storage as db
from handlers import user, admin, support_staff


async def main():
    logging.basicConfig(
        level=logging.getLevelName(config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logger = logging.getLogger(__name__)

    db.init_storage()
    logger.info("Storage initialized.")

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(support_staff.router)
    dp.include_router(user.router)


    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
    except Exception:
        logging.exception("Bot stopped with an error:")
