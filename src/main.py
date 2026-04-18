import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.handlers.user import user_router
from src.handlers.admin import admin_router
from src.handlers.ordering import ordering_router
from src.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot, engine):
    async with engine.begin() as conn:
        # DB jadvallarini yaratish
        # Productionda Alembic ishlatish tavsiya etiladi
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Bot ishga tushdi va DB ulandi!")

async def main():
    # DB Engine
    engine = create_async_engine(settings.DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Bot va Dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware orqali sessionni handlerlarga uzatish
    @dp.update.outer_middleware()
    async def db_session_middleware(handler, event, data):
        async with session_factory() as session:
            data["session"] = session
            return await handler(event, data)

    # Routerlarni ulash
    dp.include_router(user_router)
    dp.include_router(ordering_router)
    dp.include_router(admin_router)

    # Start
    await on_startup(bot, engine)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot to'xtatildi!")
