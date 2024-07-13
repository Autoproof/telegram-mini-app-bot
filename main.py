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


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    button_text = "Open Autoproof 📃"

    try:
        text = "🌎 Global copyright protection and exclusive rights transfer – 🔐secure transactions between freelancers and clients 🤝\n\n" \
               "🚀 Invite new clients to complete deals without leaving Telegram \n\n" \
               "🧑🏻‍💻 Connect your colleagues to the new freelancer platform \n\n" \
               "PS. Earn points and receive benefits, btw"

        web_app_link = Settings.bot_web_app_link()
        args = message.text.split(' ', 1)
        try:
            if args[1]:
                action, instance_id = args[1].split('=', 1)
                if action == "copyright" and instance_id:
                    button_text = "Open to claim your rights 🤝"
                    web_app_link += "?action=open_copyright&id=" + instance_id
                    text += "\n\n\n\nNew copyright objects are available to you, to which you can claim exclusive rights now"
                if action == "referral" and instance_id:
                    button_text = "Open from referral link"
                    web_app_link += "?action=open_referral&code=" + instance_id
        except:
            pass

        logger.info(f'Received message from {message.from_user.username}: {message.text}')

        keyboard = [
            [InlineKeyboardButton(text="Legal",
                                  url="https://docs.autoproof.dev/"),
            InlineKeyboardButton(text="About",
                                  url="https://autoproof.dev/")]
        ]
        keyboard = InlineKeyboardMarkup(
            resize_keyboard=True,
            inline_keyboard=keyboard)

        await message.bot.send_video(
            chat_id=message.from_user.id, caption=text, parse_mode=ParseMode.HTML,
            video=FSInputFile("media/onboarding_video.mp4"), reply_markup=keyboard)

        new_message = await message.reply("Open the app below 👇",
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
