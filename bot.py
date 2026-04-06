from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ai_logic import get_recommendations
import os

TOKEN = os.getenv("BOT_TOKEN")


# /start
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Помощь", callback_data="help")],
        [InlineKeyboardButton("Случайный совет", callback_data="random")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Привет! Я стиль‑бот 👕\n\n"
        "Напиши три слова: стиль, погода, событие.\n"
        "Например:\n"
        "гранж холодно вечеринка\n\n"
        "И я соберу образ.",
        reply_markup=reply_markup,
    )


# /help
def help_command(update, context):
    update.message.reply_text(
        "Как пользоваться ботом:\n\n"
        "1) Стиль: гранж, спорт, кэжуал, классика\n"
        "2) Погода: жарко, тепло, прохладно, холодно\n"
        "3) Событие: прогулка, вечеринка, работа, свидание\n\n"
        "Пример:\n"
        "спорт прохладно прогулка"
    )


# Обработка кнопок
def button_handler(update, context):
    query = update.callback_query
    data = query.data

    if data == "help":
        query.edit_message_text(
            "Напиши три слова: стиль, погода, событие.\n"
            "Например: гранж холодно вечеринка"
        )
    elif data == "random":
        query.edit_message_text("Совет: если сомневаешься — надевай чёрное 😎")


# Основной обработчик текста
def handle_message(update, context):
    text = update.message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        update.message.reply_text(
            "Напиши: стиль погода событие\nНапример: гранж холодно вечеринка"
        )
        return

    style, weather, event = parts[0], parts[1], parts[2]
    result = get_recommendations(style, weather, event)
    update.message.reply_text(result)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot started on Railway!")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

