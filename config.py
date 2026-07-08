# [SRC-CONFIG] Все цифры, списки и настройки. Менять баланс только здесь.
# Не пиши здесь логику (if/else), только данные.

BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "base_price": 50000, "base_income": 5000, "max_level": 10},
    {"id": 2, "name": "Студия звука", "base_price": 120000, "base_income": 10000, "max_level": 10},
    {"id": 3, "name": "Музыкальный магаз", "base_price": 300000, "base_income": 22000, "max_level": 10},
    {"id": 12, "name": "Медиаимперия", "base_price": 300000000, "base_income": 18000000, "max_level": 10},
]

DISTRICTS = {
    "Бит-стрит": {"bonus_type": "xp", "value": 1.3},
    "Золотая студия": {"bonus_type": "income", "value": 1.3},
}

DONATE_PACKS = [
    {"id": 1, "name": "Бронза", "price_rub": 100, "give_game_money": 50000},
    {"id": 2, "name": "Серебро", "price_rub": 300, "give_game_money": 200000},
]

EMOJI_MAP = {
    "Битмейкер": "🎹", "Студия звука": "🎤", "Музыкальный магаз": "👕",
    "Медиаимперия": "🌐"
}
