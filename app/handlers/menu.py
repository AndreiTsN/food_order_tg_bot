from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.services.menu_loader import load_menu
import logging
from app.config import MENU_START_TXT

logger = logging.getLogger(__name__)

menu_router = Router()

@menu_router.message(Command("menu"))
async def show_menu(message: Message):
    menu = load_menu()

    menu_text = MENU_START_TXT
    for item in menu:
        line = f"{item['name']} — {item['price']} zł\n_{item.get('description', '')}_\n\n"
        menu_text += line

    await message.answer(menu_text.strip(), parse_mode="Markdown")
