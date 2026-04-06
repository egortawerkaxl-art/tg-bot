from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ai_logic import get_recommendations
import os

TOKEN = os.getenv("BOT_TOKEN")

# Этапы диалога
STYLE, WEATHER, EVENT = range(3)


# Главное меню
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Собрать образ", callback_data="make_outfit")],
        [InlineKeyboardButton("Случайный стиль", callback_data="random_style")],
        [InlineKeyboardButton("Советы по стилю", callback_data="tips")],
        [InlineKeyboardButton("Пасхалки", callback_data="eggs")],
    ])


# /start
def start(update, context):
    update.message.reply_text(
        "Привет! Я стиль‑бот 👕\n\n"
        "Я могу собрать образ, подсказать стиль, выдать советы и даже пасхалки.\n\n"
        "Выбери действие:",
        reply_markup=main_menu_keyboard(),
    )


# Обработка кнопок главного меню
def menu_handler(update, context):
    query = update.callback_query
    data = query.data

    if data == "make_outfit":
        query.edit_message_text("Выбери стиль (гранж, спорт, кэжуал, классика):")
        return STYLE

    if data == "random_style":
        query.edit_message_text("Случайный стиль: гранж 😎\nНапиши: гранж холодно вечеринка")
        return ConversationHandler.END

    if data == "tips":
        query.edit_message_text(
            "Советы по стилю:\n"
            "• Если сомневаешься — надевай чёрное.\n"
            "• Белые кроссовки подходят почти ко всему.\n"
            "• Сочетай 2–3 цвета, не больше."
        )
        return ConversationHandler.END

    if data == "eggs":
        query.edit_message_text(
            "Пасхалки:\n"
            "• Напиши: drip\n"
            "• Напиши: ego\n"
            "• Напиши: catwalk"
        )
        return ConversationHandler.END


# Диалог: стиль
def ask_weather(update, context):
    style = update.message.text.strip()
    context.user_data["style"] = style
    update.message.reply_text("Какая погода? (жарко, тепло, прохладно, холодно)")
    return WEATHER


# Диалог: погода
def ask_event(update, context):
    weather = update.message.text.strip()
    context.user_data["weather"] = weather
    update.message.reply_text("Какое событие? (прогулка, вечеринка, работа, свидание)")
    return EVENT


# Диалог: событие → финальный ответ
def finish_dialog(update, context):
    event = update.message.text.strip()
    style = context.user_data["style"]
    weather = context.user_data["weather"]

    result = get_recommendations(style, weather, event)

    update.message.reply_text(
        f"🔥 Твой образ готов!\n\n"
        f"Стиль: {style}\n"
        f"Погода: {weather}\n"
        f"Событие: {event}\n\n"
        f"{result}"
    )

    return ConversationHandler.END


# Обработка обычных сообщений
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

    # Диалоговый режим
    dialog = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_handler)],
        states={
            STYLE: [MessageHandler(Filters.text & ~Filters.command, ask_weather)],
            WEATHER: [MessageHandler(Filters.text & ~Filters.command, ask_event)],
            EVENT: [MessageHandler(Filters.text & ~Filters.command, finish_dialog)],
        },
        fallbacks=[],
    )

    dp.add_handler(dialog)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot started on Railway!")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

