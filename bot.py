import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from ai_logic import get_recommendations

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "SG161222/Realistic_Vision_V6.0_B1_noVAE"  # стабильная модель


# -------------------------------
# Промпт-конструктор
# -------------------------------
def build_prompt(description: str) -> str:
    return (
        "Fashion photoshoot, Pinterest aesthetic, realistic model, stylish outfit, "
        "soft lighting, high detail, modern look, full body, " + description
    )


# -------------------------------
# Генерация изображения
# -------------------------------
def generate_image(description: str):
    if not HF_TOKEN:
        return None

    prompt = build_prompt(description)

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
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


# -------------------------------
# Команда /image
# -------------------------------
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Напиши описание образа. Например:\n/image кожаная куртка, мартинсы, цепи"
        )
        return

    description = " ".join(context.args)
    await update.message.reply_text("Генерирую образ...")

    img = generate_image(description)
    if img:
        await update.message.reply_photo(img)
    else:
        await update.message.reply_text("Не удалось создать изображение. Попробуй другое описание.")


# -------------------------------
# Авто-режим
# -------------------------------
async def auto_image_or_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").lower().strip()

    # Авто-генерация по фразе "сделай образ"
    if text.startswith("сделай образ"):
        description = text.replace("сделай образ", "", 1).strip()
        if not description:
            await update.message.reply_text(
                "Опиши образ. Например:\nсделай образ кожаная куртка, мартинсы, цепи"
            )
            return

        await update.message.reply_text("Генерирую образ...")

        img = generate_image(description)
        if img:
            await update.message.reply_photo(img)
        else:
            await update.message.reply_text("Не удалось создать изображение.")
        return

    # Обычные рекомендации
    parts = text.split()
    if len(parts) >= 3:
        style, weather, event = parts[0], parts[1], parts[2]
        result = get_recommendations(style, weather, event)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(
            "Напиши: стиль погода событие\nНапример: гранж холодно вечеринка"
        )


# -------------------------------
# Кнопка
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Сгенерировать образ"]]
    await update.message.reply_text(
        "Привет! Я твой fashion-ассистент.\n\n"
        "Напиши:\n"
        "• стиль погода событие\n"
        "• или /image описание\n"
        "• или «сделай образ ...»",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").lower()
    if "сгенерировать образ" in text:
        await update.message.reply_text("Опиши образ, и я создам картинку.")
        return

    await auto_image_or_text(update, context)


# -------------------------------
# MAIN
# -------------------------------
def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN не задан в переменных окружения")

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
