
import random

# Расширенная база стилей
STYLE_BASE = {
    "гранж": {
        "items": ["кожаная куртка", "рваные джинсы", "грубые ботинки"],
        "colors": ["чёрный", "серый", "бордовый"],
        "accessories": ["цепи", "кольца"],
        "shoes": ["мартинсы"],
    },
    "спорт": {
        "items": ["худи", "кроссовки", "спортивные штаны"],
        "colors": ["белый", "синий", "лайм"],
        "accessories": ["кепка", "спортивные часы"],
        "shoes": ["кроссовки"],
    },
    "кэжуал": {
        "items": ["джинсы", "футболка", "кеды"],
        "colors": ["белый", "синий", "оливковый"],
        "accessories": ["браслет", "минималистичные часы"],
        "shoes": ["кеды"],
    },
    "классика": {
        "items": ["рубашка", "брюки", "пальто"],
        "colors": ["бежевый", "чёрный", "тёмно‑синий"],
        "accessories": ["часы", "ремень"],
        "shoes": ["туфли"],
    },
}

# Карта похожих стилей
STYLE_MAP = {
    "олд мани": "классика",
    "old money": "классика",
    "стритвир": "спорт",
    "streetwear": "спорт",
    "y2k": "кэжуал",
    "техно": "гранж",
    "панк": "гранж",
    "дарк академия": "классика",
    "dark academia": "классика",
    "корейский": "кэжуал",
    "милитари": "гранж",
    "барби": "кэжуал",
    "барби-кор": "кэжуал",
    "goblin core": "гранж",
    "гоблин кор": "гранж",
}

# Погода
WEATHER_BASE = {
    "жарко": ["лёгкая футболка", "шорты"],
    "тепло": ["футболка", "лёгкая рубашка"],
    "прохладно": ["свитер", "джинсовка"],
    "холодно": ["пуховик", "шарф", "тёплый свитер"],
}

# События
EVENT_BASE = {
    "прогулка": ["удобная обувь", "рюкзак"],
    "вечеринка": ["яркие акценты"],
    "работа": ["строгий верх"],
    "свидание": ["приятные цвета"],
}

# Рандомные фразы
RANDOM_PHRASES = [
    "Сегодня твой стиль на уровне 9/10 😎",
    "Если сомневаешься — надевай чёрное.",
    "Ты выглядишь лучше, чем вчера.",
    "Этот образ — прям 🔥",
]


def get_recommendations(style, weather, event):
    style = style.lower()
    weather = weather.lower()
    event = event.lower()

    result = []

    # 1. Если стиль неизвестен → ищем похожий
    if style not in STYLE_BASE:
        if style in STYLE_MAP:
            style = STYLE_MAP[style]
        else:
            # Универсальный fallback
            result.append("Стиль не найден, но вот универсальные рекомендации:")
            result.extend(["базовая футболка", "джинсы", "кроссовки"])
            result.append("Цвета: чёрный, белый, серый")
            result.append("Аксессуары: часы, минимализм")
            # продолжаем добавлять погоду и событие
    # 2. Если стиль найден → добавляем его элементы
    if style in STYLE_BASE:
        data = STYLE_BASE[style]
        result.extend(data["items"])
        result.append(f"Рекомендуемые цвета: {', '.join(data['colors'])}")
        result.append(f"Аксессуары: {', '.join(data['accessories'])}")
        result.append(f"Обувь: {', '.join(data['shoes'])}")

    # Погода
    if weather in WEATHER_BASE:
        result.extend(WEATHER_BASE[weather])

    # Событие
    if event in EVENT_BASE:
        result.extend(EVENT_BASE[event])

    phrase = random.choice(RANDOM_PHRASES)
    outfit = "\n".join(f"• {item}" for item in result)

    return f"{phrase}\n\nВот что я предлагаю:\n\n{outfit}"
