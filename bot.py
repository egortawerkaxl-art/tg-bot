
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
def set_style(update, context):
    if not context.args:
        update.message.reply_text("Напиши стиль после команды. Например:\n/setstyle гранж")
        return

    style = " ".join(context.args).lower()
    context.user_data["favorite_style"] = style
    update.message.reply_text(f"Запомнил! Твой любимый стиль: {style}")


def my_style(update, context):
    style = context.user_data.get("favorite_style")

    if not style:
        update.message.reply_text("У тебя пока нет любимого стиля. Установи так:\n/setstyle гранж")
        return

    update.message.reply_text(f"Твой любимый стиль: {style}")


def forget(update, context):
    context.user_data.clear()
    update.message.reply_text("Я всё забыл. Начнём заново!")

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Собрать образ", callback_data="make_outfit")],
        [InlineKeyboardButton("Советы по цветам", callback_data="color_tips")],
        [InlineKeyboardButton("Советы по аксессуарам", callback_data="acc_tips")],
        [InlineKeyboardButton("Случайный стиль", callback_data="random_style")],
    ])


# Меню выбора стиля
def style_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Гранж", callback_data="style_гранж")],
        [InlineKeyboardButton("Спорт", callback_data="style_спорт")],
        [InlineKeyboardButton("Кэжуал", callback_data="style_кэжуал")],
        [InlineKeyboardButton("Классика", callback_data="style_классика")],
    ])


# Меню выбора погоды
def weather_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Жарко", callback_data="weather_жарко")],
        [InlineKeyboardButton("Тепло", callback_data="weather_тепло")],
        [InlineKeyboardButton("Прохладно", callback_data="weather_прохладно")],
        [InlineKeyboardButton("Холодно", callback_data="weather_холодно")],
    ])


# Меню выбора события
def event_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Прогулка", callback_data="event_прогулка")],
        [InlineKeyboardButton("Вечеринка", callback_data="event_вечеринка")],
        [InlineKeyboardButton("Работа", callback_data="event_работа")],
        [InlineKeyboardButton("Свидание", callback_data="event_свидание")],
    ])


# /start
def start(update, context):
    update.message.reply_text(
        "Привет! Я стиль‑бот 👕\n\n"
        "Выбери действие:",
        reply_markup=main_menu_keyboard(),
    )


# Обработка кнопок меню
def menu_handler(update, context):
    query = update.callback_query
    data = query.data

    if data == "make_outfit":
        query.edit_message_text("Выбери стиль:", reply_markup=style_keyboard())
        return STYLE

    if data == "color_tips":
        query.edit_message_text(
            "Советы по цветам:\n"
            "• Чёрный сочетается со всем\n"
            "• Белый — универсальный\n"
            "• Бежевый — классика\n"
            "• Синий — спокойный и стильный"
        )
        return ConversationHandler.END

    if data == "acc_tips":
        query.edit_message_text(
            "Советы по аксессуарам:\n"
            "• Часы — всегда уместны\n"
            "• Цепи — для гранжа\n"
            "• Кепка — для спорта\n"
            "• Минимализм — для классики"
        )
        return ConversationHandler.END

    if data == "random_style":
        query.edit_message_text("Случайный стиль: гранж 😎\nНапиши: гранж холодно вечеринка")
        return ConversationHandler.END


# Выбор стиля
def style_selected(update, context):
    query = update.callback_query
    style = query.data.replace("style_", "")
    context.user_data["style"] = style

    query.edit_message_text(f"Стиль: {style}\nТеперь выбери погоду:", reply_markup=weather_keyboard())
    return WEATHER


# Выбор погоды
def weather_selected(update, context):
    query = update.callback_query
    weather = query.data.replace("weather_", "")
    context.user_data["weather"] = weather

    query.edit_message_text(f"Погода: {weather}\nТеперь выбери событие:", reply_markup=event_keyboard())
    return EVENT


# Выбор события → финальный ответ
def event_selected(update, context):
    query = update.callback_query
    event = query.data.replace("event_", "")
    context.user_data["event"] = event

    style = context.user_data["style"]
    weather = context.user_data["weather"]

    result = get_recommendations(style, weather, event)

    query.edit_message_text(
        f"🔥 Твой образ готов!\n\n"
        f"Стиль: {style}\n"
        f"Погода: {weather}\n"
        f"Событие: {event}\n\n"
        f"{result}\n\n"
        f"Хочешь собрать новый образ?",
        reply_markup=main_menu_keyboard()
    )

    return ConversationHandler.END


def handle_message(update, context):
    text = update.message.text.strip()
    parts = text.split()

    # Если пользователь написал только погоду и событие
    if len(parts) == 2:
        favorite = context.user_data.get("favorite_style")
        if favorite:
            style = favorite
            weather, event = parts[0], parts[1]
            result = get_recommendations(style, weather, event)
            update.message.reply_text(
                f"Использую твой любимый стиль: {style}\n\n{result}"
            )
            return

    # Обычный режим: стиль + погода + событие
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

    dialog = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_handler)],
        states={
            STYLE: [CallbackQueryHandler(style_selected)],
            WEATHER: [CallbackQueryHandler(weather_selected)],
            EVENT: [CallbackQueryHandler(event_selected)],
        },
        fallbacks=[],
    )

    dp.add_handler(dialog)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setstyle", set_style))
    dp.add_handler(CommandHandler("mystyle", my_style))
    dp.add_handler(CommandHandler("forget", forget))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot started on Railway!")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
