from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers.menu import menu_router
from app.handlers.order import order_router
from app.handlers.summary import summary_router
import asyncio
import logging
from app.config import BOT_TOKEN
from app.config import BOT_HELLO_MSG, BOT_NAME
from app.config import START_DESCR, MENU_DESCR, ORDER_DESCR

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(menu_router)
dp.include_router(order_router)
dp.include_router(summary_router)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description=START_DESCR),
        BotCommand(command="menu", description=MENU_DESCR),
        BotCommand(command="order", description=ORDER_DESCR)
    ]
    # set Telegram's default commands in Menu button
    await bot.set_my_commands(commands)

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(BOT_HELLO_MSG)

async def main():
    print(f"Bot '{BOT_NAME}' is started")

    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

