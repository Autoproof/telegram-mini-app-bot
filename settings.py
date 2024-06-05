import os


class Settings:

    @staticmethod
    def admin_telegram_id():
        return os.environ.get(f"ADMIN_ID", default=75771603)

    @staticmethod
    def bot_token():
        return os.environ.get(f"BOT_TOKEN")
