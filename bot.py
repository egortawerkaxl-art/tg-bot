from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from ai_logic import get_recommendations

def start(update, context):
    update.message.reply_text(
        "Привет! Я AI‑стилист.\n"
        "Напиши мне стиль или описание, например:\n"
        "• y2k\n"
        "• гранж\n"
        "• хочу что-то тёмное и технологичное\n\n"
        "И я подберу образ ✨"
    )

def handle_message(update, context):
    user_text = update.message.text

    weather = "warm"
    event = None

    if "холод" in user_text.lower() or "зима" in user_text.lower():
        weather = "cold"

    events_map = {
        "школ": "school",
        "свидан": "date",
        "работ": "work",
        "вечерин": "party",
        "гуля": "walk",
        "фото": "photoshoot"
    }

    for key, val in events_map.items():
        if key in user_text.lower():
            event = val

    response = get_recommendations(user_text, weather, event)
    update.message.reply_text(response)

def main():
    TOKEN = "8323173595:AAHlcDTcc0uM_bi3DenY7E_D7xtIRuGI0_o"

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
