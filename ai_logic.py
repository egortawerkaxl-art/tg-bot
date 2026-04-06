import random

# ===== US-5: Продвинутая AI-логика рекомендаций =====

styles = {
    "y2k": {
        "keywords": ["яркий", "гламурный", "2000-е", "низкая посадка", "блестящий"],
        "palette": ["розовый", "металлик", "голубой", "белый"],
        "items": ["блестящий топ", "джинсы с низкой посадкой", "мини-сумка", "массивные кроссовки"],
        "accessories": ["бабочки", "стразы", "розовые очки", "чокер"],
        "weather_variants": {
            "cold": "добавьте укороченную пуховку или меховую куртку",
            "warm": "подойдёт кроп-топ и лёгкая ветровка"
        }
    },

    "soft girl": {
        "keywords": ["нежный", "пастельный", "милый", "аккуратный"],
        "palette": ["розовый", "лавандовый", "мятный", "белый"],
        "items": ["свитер оверсайз", "юбка-плиссе", "кеды", "кардиган"],
        "accessories": ["заколки", "бантики", "мини-сумка", "жемчужные серьги"],
        "weather_variants": {
            "cold": "добавьте тёплый кардиган или шарф",
            "warm": "подойдёт лёгкая блузка или топ"
        }
    },

    "old money": {
        "keywords": ["элегантный", "дорогой", "классический", "строгий"],
        "palette": ["бежевый", "белый", "тёмно-синий", "коричневый"],
        "items": ["тренч", "рубашка", "классические брюки", "лоферы"],
        "accessories": ["часы", "кожаный ремень", "минималистичные украшения"],
        "weather_variants": {
            "cold": "добавьте кашемировое пальто",
            "warm": "подойдёт лёгкий льняной пиджак"
        }
    },

    "techwear": {
        "keywords": ["функциональный", "урбан", "технологичный", "тёмный"],
        "palette": ["чёрный", "серый", "тёмно-зелёный"],
        "items": ["анорак", "карго-штаны", "высокие кроссовки", "жилет"],
        "accessories": ["стропы", "ремни", "тактическая сумка"],
        "weather_variants": {
            "cold": "добавьте утеплённую куртку или парку",
            "warm": "подойдёт лёгкая ветровка"
        }
    },

    "grunge": {
        "keywords": ["тёмный", "панк", "рваный", "гранж", "грубый"],
        "palette": ["чёрный", "серый", "бордовый"],
        "items": ["рваные джинсы", "клетчатая рубашка", "грубые ботинки", "оверсайз худи"],
        "accessories": ["цепи", "кольца", "чокер", "кожаный браслет"],
        "weather_variants": {
            "cold": "добавьте кожаную куртку или толстовку",
            "warm": "подойдёт футболка с принтом и лёгкая клетчатая рубашка"
        }
    }
}

# ===== Матрица похожести стилей =====
similarity = {
    "y2k": ["soft girl", "streetwear"],
    "soft girl": ["y2k", "old money"],
    "old money": ["soft girl", "classic"],
    "techwear": ["streetwear", "grunge"],
    "streetwear": ["y2k", "techwear"],
    "grunge": ["techwear", "streetwear"]
}
# ===== Подбор по событию =====
event_tips = {
    "school": "Сделайте образ удобным и практичным. Избегайте слишком ярких или откровенных элементов.",
    "date": "Добавьте что-то, что подчеркнёт индивидуальность: украшения, интересный аксессуар или необычную деталь.",
    "work": "Выбирайте более строгие и аккуратные элементы. Нейтральные цвета — лучший выбор.",
    "party": "Можно добавить яркие акценты, блестящие элементы или необычные аксессуары.",
    "walk": "Комфорт — главное. Подойдут кроссовки, оверсайз и лёгкие ткани.",
    "photoshoot": "Выбирайте контрастные цвета и выразительные элементы, которые хорошо смотрятся на камере."
}

# ===== Поиск похожего стиля =====
def find_similar_style(user_input):
    user_input = user_input.lower()

    # если стиль есть — возвращаем его
    if user_input in styles:
        return user_input, None

    # если нет — ищем похожий
    for style, data in styles.items():
        for kw in data["keywords"]:
            if kw in user_input:
                return style, None

    # если вообще ничего не нашли — ищем по матрице
    if user_input in similarity:
        return similarity[user_input][0], user_input

    # если совсем неизвестно
    return None, None


# ===== Генерация образа =====
def generate_outfit(style, weather="warm"):
    data = styles[style]

    base_items = random.sample(data["items"], 2)
    accessory = random.choice(data["accessories"])
    color = random.choice(data["palette"])
    weather_tip = data["weather_variants"][weather]

    outfit = (
        f"Основные элементы: {base_items[0]}, {base_items[1]}\n"
        f"Цветовая палитра: {color}\n"
        f"Аксессуар: {accessory}\n"
        f"Совет по погоде: {weather_tip}"
    )

    return outfit


# ===== Главная функция =====
def get_recommendations(user_input, weather="warm", event=None):
    style, alternative = find_similar_style(user_input)

    if style is None:
        return "Стиль не найден и похожих вариантов нет."

    if alternative:
        msg = f"Стиль '{user_input}' не найден. Похожий стиль: {style.upper()}\n\n"
    else:
        msg = f"Ваш стиль: {style.upper()}\n\n"

    data = styles[style]

    msg += "Ключевые особенности:\n"
    for kw in data["keywords"]:
        msg += f"- {kw}\n"

    msg += "\nИндивидуальный образ:\n"
    msg += generate_outfit(style, weather)

    # Добавляем совет по событию
    if event:
        event = event.lower()
        if event in event_tips:
            msg += f"\n\nСовет для события ({event}): {event_tips[event]}"
        else:
            msg += f"\n\nСобытие '{event}' не найдено. Доступные: {', '.join(event_tips.keys())}"

    return msg



# ===== Тест =====
if __name__ == "__main__":
    user_style = input("Введите стиль или описание: ")
    weather = input("Погода (warm/cold): ")
    event = input("Событие (school/date/work/party/walk/photoshoot или Enter): ")


