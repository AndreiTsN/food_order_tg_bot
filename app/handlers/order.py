from aiogram import Router, Bot
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from app.services.google_sheets import save_order_to_sheet
from app.services.menu_loader import get_menu_items, get_price_by_name, load_menu
from app.handlers.menu import show_menu
from app.config import ADMIN_CHANNEL_ID
import logging


logger = logging.getLogger(__name__)

order_router = Router()

class OrderFood(StatesGroup):
    waiting_for_item = State()
    showing_item_info = State()
    waiting_for_quantity = State()
    waiting_for_continue = State()
    waiting_for_contact = State()

def menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=item)] for item in get_menu_items()],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def continue_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить ещё")],
            [KeyboardButton(text="Отправить заказ")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@order_router.message(Command("order"))
async def start_order(message: Message, state: FSMContext):
    await message.answer("Выберите блюдо из меню:", reply_markup=menu_keyboard())
    await state.set_state(OrderFood.waiting_for_item)
    await state.update_data(order=[])

@order_router.message(OrderFood.waiting_for_item)
async def show_item_info(message: Message, state: FSMContext):
    item = message.text
    if item not in get_menu_items():
        await message.answer("Пожалуйста, выберите блюдо из меню 👇", reply_markup=menu_keyboard())
        return

    menu = load_menu()
    item_data = next((i for i in menu if i["name"] == item), None)
    description = item_data.get("description", "Описание пока не добавлено.") if item_data else "Блюдо не найдено."

    await state.update_data(current_item=item)

    await message.answer(
        f"🍽 *{item}*\n\n_{description}_",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Добавить в заказ")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )

    await state.set_state(OrderFood.showing_item_info)

@order_router.message(OrderFood.showing_item_info)
async def handle_add_or_back(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "➕ Добавить в заказ":
        await message.answer("Сколько штук?")
        await state.set_state(OrderFood.waiting_for_quantity)
    elif text == "🔙 Назад":
        await message.answer("Выберите блюдо из меню:", reply_markup=menu_keyboard())
        await state.set_state(OrderFood.waiting_for_item)
    else:
        await message.answer("Пожалуйста, выберите «➕ Добавить в заказ» или «🔙 Назад».")

@order_router.message(OrderFood.waiting_for_quantity)
async def get_quantity(message: Message, state: FSMContext):
    logger.info(f"🔢 Введено количество: {message.text!r}")

    data = await state.get_data()
    item = data["current_item"]
    quantity = message.text.strip()

    if not quantity.isdigit():
        await message.answer("Пожалуйста, введите количество цифрой (например, 2)")
        return

    order = data.get("order", [])
    order.append({"item": item, "quantity": quantity})
    await state.update_data(order=order)

    summary_lines = []
    total_price = 0
    for o in order:
        name = o["item"]
        qty = int(o["quantity"])
        price = get_price_by_name(name)
        line_total = qty * price
        total_price += line_total
        summary_lines.append(f"{name} × {qty} = {line_total}zl")

    summary_text = "\n".join(summary_lines)

    await message.answer(
        f"✅ Блюдо добавлено: {item} × {quantity}\n\n"
        f"🧾 Ваш заказ сейчас:\n"
        f"{summary_text}\n"
        f"💰 Общая сумма: {total_price}zl\n\n"
        f"Вы хотите добавить ещё что-нибудь?",
        reply_markup=continue_keyboard()
    )
    await state.set_state(OrderFood.waiting_for_continue)

@order_router.message(OrderFood.waiting_for_continue)
async def continue_or_finish(message: Message, state: FSMContext):
    logger.info(f"Пользователь ввёл: {message.text!r}")
    text = message.text.strip().lower()

    if text in ["добавить ещё", "добавить", "ещё", "➕ добавить в заказ"]:
        await message.answer("Выберите следующее блюдо:", reply_markup=menu_keyboard())
        await state.set_state(OrderFood.waiting_for_item)
    elif text in ["отправить заказ", "отправить", "заказ"]:
        await message.answer("Пожалуйста, укажите ваше имя и телефон:")
        await state.set_state(OrderFood.waiting_for_contact)
    else:
        await message.answer(
            "Пожалуйста, выберите: «Добавить ещё» или «Отправить заказ»",
            reply_markup=continue_keyboard()
        )

@order_router.message(F.text == "❌ Отмена")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Заказ отменён. Если хотите начать заново, нажмите /order.")


@order_router.message(OrderFood.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext, bot: Bot):
    logger.info(f"📞 Контакт от пользователя: {message.text!r}")

    data = await state.get_data()
    order = data.get("order", [])
    contact = message.text

    order_lines = []
    total_price = 0
    for unit in order:
        item = unit["item"]
        quantity = int(unit["quantity"])
        price = get_price_by_name(item)
        line_total = quantity * price
        total_price += line_total
        order_lines.append(f"{item} × {quantity} = {line_total}zl")

    order_text = "\n".join(order_lines)

    await message.answer(
        f"✅ Заказ принят!\n\n"
        f"{order_text}\n"
        f"💰 Общая сумма: {total_price}zl\n\n"
        f"📞 Контакт: {contact}\n\n"
        f"Скоро с вами свяжутся!"
    )
    await state.clear()

    save_order_to_sheet(order, total_price, contact)

    await bot.send_message(
        chat_id=ADMIN_CHANNEL_ID,
        text=(
            f"📦 Новый заказ:\n"
            f"{order_text}\n"
            f"💰 Сумма: {total_price}zl\n"
            f"📞 Контакт: {contact}"
        ),
        parse_mode="Markdown"
    )

    await show_menu(message)
