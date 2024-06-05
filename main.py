import asyncio
import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import Any
from aiogram.handlers import ErrorHandler
from aiogram.methods import PinChatMessage

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton

from settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('logs/conf-bot.log', maxBytes=100000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

TOKEN = Settings.bot_token()
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        logger.info(f'Received message from {message.from_user.username}: {message.text}')
        keyboard = [[InlineKeyboardButton(text="Open Autoproof 📃 34,521",
                                          web_app=WebAppInfo(url="https://loon-holy-noticeably.ngrok-free.app"))]]
        keyboard = InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=keyboard)

        new_message = await message.reply("Push the button below to start", reply_markup=keyboard)
        try:
            await message.bot(PinChatMessage(chat_id=message.chat.id, message_id=new_message.message_id))
        except Exception as e:
            pass

    except TypeError as e:
        await message.answer(f"Something went wrong")


@dp.errors()
class ConfbotErrorsHandler(ErrorHandler):
    async def handle(self) -> Any:
        logger.error(f'Update "{self.exception_name}" caused error: {self.exception_message}')
        try:
            await self.bot.send_message(Settings.admin_telegram_id(), f'Error: {self.exception_message}')
            await self.bot.send_message(Settings.admin_telegram_id(), f'{traceback.format_exc()}')
        except Exception as e:
            await self.bot.send_message(Settings.admin_telegram_id(), f'Error: {e}')
            logger.error(f'Failed to send error message: {e}')


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
