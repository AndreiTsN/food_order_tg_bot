import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))
SUMMARY_ADMINS = list(map(int, os.getenv("SUMMARY_ADMINS", "").split(",")))

RECIPES_FILE = os.getenv("RECIPES_FILE", "app/data/recipes.json")
MENU_FILE = os.getenv("MENU_FILE", "app/data/menu.json")

GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "app/google_creds.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

##########################
BOT_NAME = os.getenv("BOT_NAME")

BOT_HELLO_MSG = f"Привет! Это {BOT_NAME}. Чтобы начать работу нажми /start "

# set_bot_commands() descriptions
START_DESCR = "Начать работу"
MENU_DESCR = "Показать меню"
ORDER_DESCR = "Оформить заказ"

# show_menu() start message
MENU_START_TXT = "📋 *Меню на сегодня:*\n\n"
