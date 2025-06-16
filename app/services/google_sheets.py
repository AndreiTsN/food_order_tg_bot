import gspread
from app.services.recipes import calculate_ingredients
from datetime import datetime
from app.config import GOOGLE_CREDS_FILE
from app.config import GOOGLE_SHEET_ID
import logging


logger = logging.getLogger(__name__)

gc = gspread.service_account(filename=GOOGLE_CREDS_FILE)
sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1

def save_order_to_sheet(order: list, total: int, contact: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    items = [f"{o['item']} × {o['quantity']}" for o in order]
    items_str = ", ".join(items)
    total_count = sum(int(o['quantity']) for o in order)

    row = [now, items_str, total_count, total, contact]
    sheet.append_row(row)

def get_all_orders():
    """
    Чтение всех заказов из Google Sheets и возврат как список словарей.
    Добавлено логирование для отладки дат.
    """
    records = sheet.get_all_records()

    for row in records:
        print("Дата из строки:", row.get("Дата и время"), type(row.get("Дата и время")))

    return records

def summarize_orders_for_range(orders, start_date, end_date):
    """
    Считает количество по каждому блюду и итоговую сумму за указанный период.
    """
    summary = {}
    total = 0

    for order in orders:
        date_str = order.get("Дата и время")
        if not date_str:
            continue
        try:
            order_date = datetime.fromisoformat(date_str).date()
        except ValueError:
            continue

        if start_date <= order_date <= end_date:
            items = order.get("Блюда", "")
            total_count = int(order.get("Кол-во", 0))
            order_sum = int(order.get("Сумма", 0))

            for item_part in items.split(","):
                if "×" in item_part:
                    name, qty = item_part.strip().split("×")
                    name = name.strip()
                    qty = int(qty.strip())
                    summary[name] = summary.get(name, 0) + qty

            total += order_sum

    return summary, total


def save_summary_to_sheet(summary: dict, total: int, start_date: datetime.date, end_date: datetime.date):
    """
    Перезаписывает лист "Summary" новой сводкой (всегда только один актуальный отчет).
    """
    # Получаем или создаём лист "Summary"
    try:
        summary_sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("Summary")
    except gspread.exceptions.WorksheetNotFound:
        summary_sheet = gc.open_by_key(GOOGLE_SHEET_ID).add_worksheet(title="Summary", rows="100", cols="20")

    # Очищаем старую сводку
    summary_sheet.clear()

    # Заголовки
    summary_sheet.append_row(["Период", "Блюдо", "Кол-во", "Сумма"])

    # Формируем строки
    period_str = f"{start_date.strftime('%Y-%m-%d')} – {end_date.strftime('%Y-%m-%d')}"

    for item, qty in summary.items():
        summary_sheet.append_row([period_str, item, qty, ""])

    # Итого
    summary_sheet.append_row([period_str, "ИТОГО", "", total])

def save_ingredients_summary(summary: dict):
    """
    Записывает расчёт ингредиентов по итогам summary в Google Sheets (лист Ingredients)
    """
    try:
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("Ingredients")
        sheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).add_worksheet(title="Ingredients", rows="100", cols="10")

    # Заголовки
    sheet.append_row(["Ингредиент", "Вес (грамм)"])

    total_ingredients = calculate_ingredients(summary)  # здесь вызываем обработку из recipes.py

    for name, grams in total_ingredients.items():
        sheet.append_row([name, grams])
