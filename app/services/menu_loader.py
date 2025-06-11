import json
import logging
from app.config import MENU_FILE


logger = logging.getLogger(__name__)

def load_menu():
    try:
        with open(MENU_FILE, encoding="utf-8") as f:
            menu = json.load(f)
            logger.info(f"Menu successfully loaded from {MENU_FILE}")
            return menu
    except Exception as e:
        logger.error(f"Error while loading the menu: {e}")
        return []

def get_menu_items():
    return [item["name"] for item in load_menu()]

def get_price_by_name(name: str) -> int:
    for item in load_menu():
        if item["name"] == name:
            return int(item.get("price", 0))
    logger.warning(f"Price not found for the dish: {name}")
    return 0

def get_description_by_name(name: str) -> str:
    for item in load_menu():
        if item["name"] == name:
            return item.get("description", "")
    return ""
