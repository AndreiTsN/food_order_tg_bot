from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta
from app.services.google_sheets import get_all_orders, summarize_orders_for_range
from app.services.google_sheets import save_summary_to_sheet
from app.services.google_sheets import save_ingredients_summary
from app.config import SUMMARY_ADMINS
from app.config import ADMIN_CHANNEL_ID as CHANNEL_ID
from app.config import GOOGLE_SHEET_URL as SHEET_URL
import logging


logger = logging.getLogger(__name__)

summary_router = Router()

@summary_router.message(Command("summary"))
async def summary_handler(message: Message, bot: Bot):
    if message.from_user.id not in SUMMARY_ADMINS:
        return await message.answer("❌ У вас нет доступа к этой команде.")

    # Определяем диапазон
    args = message.text.strip().split()
    if len(args) == 1:
        days = 1  # по умолчанию — сегодня
    elif len(args) == 2 and args[1].isdigit():
        days = int(args[1])
    elif len(args) == 2 and ":" in args[1]:
        try:
            start_str, end_str = args[1].split(":")
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_str, "%Y-%m-%d").date()
        except:
            return await bot.send_message(CHANNEL_ID, "❌ Неверный формат дат.")
    else:
        return await bot.send_message(CHANNEL_ID,
                                      "⚠️ Используйте `/summary`, `/summary 3` или `/summary 2025-04-10:2025-04-13`")

    # Получаем данные из Google Sheets
    orders = get_all_orders()

    # Определяем даты
    if "start" not in locals():
        end = datetime.now().date()
        start = end - timedelta(days=days-1)

    # Фильтруем и считаем
    summary, total = summarize_orders_for_range(orders, start, end)

    if not summary:
        return await bot.send_message(CHANNEL_ID, f"📅 Нет заказов с {start} по {end}")

    # Сохраняем в отдельный лист
    save_summary_to_sheet(summary, total, start, end)
    save_ingredients_summary(summary)  # ДОБАВЛЕНО: сохраняем продукты

    # Готовим текст отчёта
    summary_lines = [f"{item} — {qty} шт" for item, qty in summary.items()]
    period_str = f"{start.strftime('%d.%m')}–{end.strftime('%d.%m')}" if start != end else f"{start.strftime('%d.%m')}"
    report = (
            f"🧾 Сводка заказов за {period_str}:\n\n" +
            "\n".join(summary_lines) +
            f"\n\n💰 Общая сумма: {total}zl"+
            f"\n\n📄 [Открыть Google Sheet]({SHEET_URL})"
    )

    # Отправка в канал
    await bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")
