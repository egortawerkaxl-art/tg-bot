import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from ai_logic import get_recommendations

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "black-forest-labs/FLUX.1-dev"  # универсальная модель для реалистичных fashion-образов

# -------------------------------
# Промпт-конструктор
# -------------------------------
def build_prompt(description: str):
    return (
        f"Fashion photoshoot, Pinterest aesthetic, realistic model, stylish outfit, "
        f"soft lighting, high detail, modern look, full body, {description}"
    )

# -------------------------------
# Генерация изображения
# -------------------------------
def generate_image(description: str):
    prompt = build_prompt(description)

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt},
    )

    if response.status_code != 200:
        return None

    return response.content

# -------------------------------
# Команда /image
# -------------------------------
def image_command(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Напиши описание образа. Например:\n/image кожаная куртка, мартинсы, цепи")
        return

    description = " ".join(context.args)
    update.message.reply_text("Генерирую образ...")

    img = generate_image(description)
    if img:
        update.message.reply_photo(img)
    else:
        update.message.reply_text("Не удалось создать изображение. Попробуй другое описание.")

# -------------------------------
# Авто-режим: если текст начинается с «сделай образ»
# -------------------------------
def auto_image(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if text.startswith("сделай образ"):
        description = text.replace("сделай образ", "").strip()
        if not description:
            update.message.reply_text("Опиши образ. Например:\nсделай образ кожаная куртка, мартинсы, цепи")
            return

        update.message.reply_text("Генерирую образ...")

        img = generate_image(description)
        if img:
            update.message.reply_photo(img)
        else:
            update.message.reply_text("Не удалось создать изображение.")
        return

    # если это не запрос на картинку — обычная логика
    parts = text.split()
    if len(parts) >= 3:
        style, weather, event = parts[0], parts[1], parts[2]
        result = get_recommendations(style, weather, event)
        update.message.reply_text(result)
    else:
        update.message.reply_text("Напиши: стиль погода событие\nНапример: гранж холодно вечеринка")

# -------------------------------
# Кнопка «Сгенерировать образ»
# -------------------------------
def start(update: Update, context: CallbackContext):
    keyboard = [["Сгенерировать образ"]]
    update.message.reply_text(
        "Привет! Я твой fashion-ассистент.\n\n"
        "Напиши:\n"
        "• стиль погода событие\n"
        "• или /image описание\n"
        "• или «сделай образ ...»",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

def button_handler(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if "сгенерировать образ" in text:
        update.message.reply_text("Опиши образ, и я создам картинку.")
        return

    auto_image(update, context)

# -------------------------------
# MAIN
# -------------------------------
def main():
    updater = Updater(os.getenv("BOT_TOKEN"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("image", image_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

