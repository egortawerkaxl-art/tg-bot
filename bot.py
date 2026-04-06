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


def generate_image(description: str):
    if not HF_TOKEN:
        return None

    prompt = build_prompt(description)

    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "blurry, distorted, bad quality, deformed face, extra limbs"
            }
        },
        timeout=120,
    )

    if response.status_code != 200:
        print("HF ERROR:", response.text)
        return None

    return response.content


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

