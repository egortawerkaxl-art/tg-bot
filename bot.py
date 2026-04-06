from telegram.ext import Updater, MessageHandler, Filters
from ai_logic import get_recommendations
import os

TOKEN = os.getenv("BOT_TOKEN")

def handle_message(update, context):
    text = update.message.text
    parts = text.split()

    if len(parts) < 3:
        update.message.reply_text(
            "Напиши: стиль погода событие\nНапример: гранж холодно вечеринка"
        )
        return

    user_style, weather, event = parts[0], parts[1], parts[2]
    result = get_recommendations(user_style, weather, event)
    update.message.reply_text(result)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot started on Render!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
