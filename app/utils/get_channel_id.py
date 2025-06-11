"""
Script to retrieve a Telegram channel's chat_id

How to use:
   > python utils/get_channel_id.py

The channel must be temporarily public and have a username (e.g., @your_channel_name)
"""


import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)

async def main():
    chat = await bot.get_chat("@your_channel_name")  # <--- set channel username here
    print(f"ID канала: {chat.id} — {chat.title}")

if __name__ == "__main__":
    asyncio.run(main())
