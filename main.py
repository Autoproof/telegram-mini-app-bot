import asyncio
import json
import logging
import sys
import traceback
from datetime import timezone, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any

import requests
from aiogram.handlers import ErrorHandler
from aiogram.methods import PinChatMessage

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton, FSInputFile

from settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(Settings.rotate_log_file(), maxBytes=100000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


TOKEN = Settings.bot_token()
dp = Dispatcher()


async def log_analitics(message: Message):
    url = "https://api.graspil.com/v1/send-batch-update"
    api_key = ""
    tz = timezone(timedelta(0))

    payload = json.dumps([
        {
            "date": message.date.replace(tzinfo=tz).isoformat(),
            "update": {
                "message": {
                    "chat": {
                        "id": message.chat.id,
                        "type": "private",
                        "username": message.chat.username,
                        "last_name": message.chat.last_name,
                        "first_name": message.chat.first_name
                    },
                    "date": int(message.date.timestamp()),
                    "from": {
                        "id": message.from_user.id,
                        "is_bot": False,
                        "username": message.from_user.username,
                        "last_name": message.from_user.last_name,
                        "first_name": message.from_user.first_name
                    },
                    "text": message.text,
                    "message_id": message.message_id
                },
                "update_id": message.message_id
            }
        }
    ])
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': api_key,
    }
    requests.request("POST", url, headers=headers, data=payload)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    # await log_analitics(message)

    button_text = "Open the platform 👩🏻‍💻"
    try:
        welcome_text = "👋 Welcome to Autoproof.dev!\n\n" \
               "We're building the next-generation freelance platform right here in Telegram. Our mission is to provide freelancers and clients with secure, legally protected transactions using smart contracts.\n\n" \
               "What's available now:\n\n" \
               " - ✅ Secure Deals: Start using our platform today to protect your work and get paid safely. No need to leave Telegram\n\n" \
               " - 👯 Referral Program: Invite other freelancers and earn a percentage of their earnings.\n"

        news_text = "🚀 What’s coming soon:\n" \
                    " - Freelance Marketplace: A place where you can find new projects and showcase your skills\n" \
                    " - Seamless Communication: Chat directly with clients through our Telegram bot, with everything legally documented\n\n" \
                    "Start Now:\n" \
                    " - Protect your current projects\n" \
                    " - Invite other freelancers and start earning 💌\n"

        web_app_link = Settings.bot_web_app_link()
        args = message.text.split(' ', 1)
        try:
            if args[1]:
                action, instance_id = args[1].split('=', 1)
                if action == "copyright" and instance_id:
                    button_text = "Open to claim your rights 🤝"
                    web_app_link += "?action=open_copyright&id=" + instance_id
                    welcome_text += "\n\n\n\nNew copyright objects are available to you, to which you can claim exclusive rights now"
                if action == "referral" and instance_id:
                    button_text = "Open from referral link"
                    web_app_link += "?action=open_referral&code=" + instance_id
        except:
            pass

        logger.info(f'Received message from {message.from_user.username}: {message.text}')

        # Welcome message
        welcome_keyboard_buttons = [
            [InlineKeyboardButton(text="Legal",
                                  url="https://docs.autoproof.dev/"),
            InlineKeyboardButton(text="About",
                                  url="https://autoproof.dev/")]
        ]
        welcome_keyboard = InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=welcome_keyboard_buttons)

        await message.bot.send_video(
            chat_id=message.from_user.id, caption=welcome_text, parse_mode=ParseMode.HTML,
            video=FSInputFile("media/onboarding_video.mp4"), reply_markup=welcome_keyboard)

        # News message
        news_keyboard_buttons = [
            [InlineKeyboardButton(text="Join our channel",
                                  url="https://t.me/AutoproofDev")]
        ]
        news_keyboard = InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=news_keyboard_buttons)

        await message.bot.send_message(
            chat_id=message.from_user.id, text=news_text, parse_mode=ParseMode.HTML, reply_markup=news_keyboard)

        # Action message
        new_message = await message.reply("Secure a deal with a client or freelancer",
                                          reply_markup=InlineKeyboardMarkup(
                                              resize_keyboard=True,
                                              inline_keyboard=[
                                                  [InlineKeyboardButton(text=button_text,
                                                                        web_app=WebAppInfo(url=web_app_link))]
                                              ]))

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
