import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import common, gameplay, lobby, voting
from config import settings
from game.manager import RoomManager
from game.questions import QuestionManager

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not settings.bot_token:
        logger.error(
            "BOT_TOKEN is not configured! Please set BOT_TOKEN in .env or environment variables."
        )
        sys.exit(1)

    logger.info("Initializing Polygraph Spy Game Bot...")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Shared singletons
    room_manager = RoomManager()
    question_manager = QuestionManager(assets_dir=settings.assets_dir)
    question_manager.load_all()

    # Pass dependencies via workflow context data
    dp["room_manager"] = room_manager
    dp["question_manager"] = question_manager

    # Register router handlers
    dp.include_router(common.router)
    dp.include_router(lobby.router)
    dp.include_router(gameplay.router)
    dp.include_router(voting.router)

    # Fetch bot username if not provided
    try:
        bot_info = await bot.get_me()
        logger.info(
            f"Connected to Telegram as @{bot_info.username} (ID: {bot_info.id})"
        )
        if not settings.bot_username:
            settings.bot_username = bot_info.username or ""
    except Exception as e:
        logger.warning(f"Could not fetch bot information on startup: {e}")

    logger.info("Bot started successfully. Listening for updates...")

    # Start long-polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received termination signal.")
    finally:
        logger.info("Shutting down bot session...")
        await bot.session.close()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Polygraph bot stopped.")
