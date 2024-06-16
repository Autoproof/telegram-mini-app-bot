import os


class Settings:

    @staticmethod
    def admin_telegram_id():
        return os.environ.get(f"ADMIN_ID", default=75771603)

    @staticmethod
    def rotate_log_file():
        return os.environ.get(f"BOT_ROTATE_LOG_FILE", default="/var/log/ap-bot.log")

    @staticmethod
    def bot_token():
        return os.environ.get(f"BOT_TOKEN")

    @staticmethod
    def bot_web_app_link():
        return os.environ.get(f"BOT_WEB_APP_LINK", "https://autoproof.dev")
