import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from ai_logic import get_recommendations

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "SG161222/Realistic_Vision_V6.0_B1_noVAE"  # стабильная модель


def build_prompt(description: str):
    return (
        "Fashion photoshoot, Pinterest aesthetic, realistic model, stylish outfit, "
        "soft lighting, high detail, modern look, full body, " + description
    )


import replicate

import requests
import os

def generate_image(description: str):
    try:
        prompt = build_prompt(description)

        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {os.getenv('REPLICATE_API_TOKEN')}",
                "Content-Type": "application/json",
            },
            json={
                "version": "db21e45d3f3f0c4c0e4f8c7b5d5b6f1f5e7f5f5f5f5f5f5f",  # SDXL версия
                "input": {
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024,
                }
            }
        )

        data = response.json()

        # Если ошибка — выводим в логи
        if "error" in data:
            print("REPLICATE ERROR:", data["error"])
            return None

        # Получаем ID предсказания
        prediction_id = data["id"]

        # Ждём результат
        while True:
            result = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers={"Authorization": f"Token {os.getenv('REPLICATE_API_TOKEN')}"}
            ).json()

            if result["status"] == "succeeded":
                image_url = result["output"][0]
                img_data = requests.get(image_url).content
                return img_data

            if result["status"] == "failed":
                print("REPLICATE FAILED:", result)
                return None

    except Exception as e:
        print("REPLICATE ERROR:", e)
        return None


def image_command(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text(
            "Напиши описание образа. Например:\n/image кожаная куртка, мартинсы, цепи"
        )
        return

    description = " ".join(context.args)
    update.message.reply_text("Генерирую образ...")

    img = generate_image(description)
    if img:
        update.message.reply_photo(img)
    else:
        update.message.reply_text("Не удалось создать изображение. Попробуй другое описание.")


def auto_image(update: Update, context: CallbackContext):
    text = update.message.text.lower().strip()

    if text.startswith("сделай образ"):
        description = text.replace("сделай образ", "", 1).strip()

        if not description:
            update.message.reply_text(
                "Опиши образ. Например:\nсделай образ кожаная куртка, мартинсы, цепи"
            )
            return

        update.message.reply_text("Генерирую образ...")

        img = generate_image(description)
        if img:
            update.message.reply_photo(img)
        else:
            update.message.reply_text("Не удалось создать изображение.")
        return

    parts = text.split()
    if len(parts) >= 3:
        style, weather, event = parts[0], parts[1], parts[2]
        result = get_recommendations(style, weather, event)
        update.message.reply_text(result)
    else:
        update.message.reply_text(
            "Напиши: стиль погода событие\nНапример: гранж холодно вечеринка"
        )


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

