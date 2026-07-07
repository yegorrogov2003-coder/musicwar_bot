import time

# --- НАСТРОЙКИ ЭКОНОМИКИ ---
KVTIRNIK_COOLDOWN_SECONDS = 90  # КД: 90 секунд (1.5 минуты) - идеально для удержания

# Список бизнесов: цена покупки, доход в час, макс. уровень, цена за уровень
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 1800, "income": 400, "max_level": 10, "cost_per_level": 1200},
    {"id": 2, "name": "Студия звука", "price": 8000, "income": 1500, "max_level": 8, "cost_per_level": 6000},
    {"id": 3, "name": "Музыкальный магазин", "price": 25000, "income": 4500, "max_level": 7, "cost_per_level": 18000},
    {"id": 4, "name": "Рэп-баттл", "price": 70000, "income": 11000, "max_level": 6, "cost_per_level": 50000},
]

RANKS = [
    "🎧 Начинающий", "🎤 Андеграунд", "🎵 Хип-хопер", "🏆 Прорыв", "📀 Известный",
    "💿 Популярный", "🎶 Топ-чарт", "👑 Платиновый", "⭐ Бриллиантовый", "💎 Music Legend"
]

# База данных в памяти (для бесплатного старта без SQL)
# В формате: { user_id: { money, xp, level, businesses: {biz_id: level}, last_kvartirnik_time, last_income_time } }
users_db = {}

def get_user(user_id):
    """Получает данные пользователя или создает нового."""
    if user_id not in users_db:
        users_db[user_id] = {
            "user_id": user_id,
            "money": 1500,          # Стартовый капитал
            "xp": 0,
            "level": 1,
            "businesses": {},       # Купленные бизнесы: {id_бизнеса: уровень}
            "last_kvartirnik_time": 0, # Время последнего квартирника
            "last_income_time": time.time() # Время последнего начисления дохода
        }
    return users_db[user_id]

def save_user(user):
    """Сохраняет изменения (в памяти)."""
    users_db[user["user_id"]] = user

def can_do_kvartirnik(user):
    """Проверяет, прошел ли КД на квартирник."""
    now = time.time()
    time_since_last = now - user["last_kvartirnik_time"]
    
    if time_since_last >= KVTIRNIK_COOLDOWN_SECONDS:
        return True, 0  # Можно делать
    else:
        time_left = KVTIRNIK_COOLDOWN_SECONDS - time_since_last
        return False, int(time_left)

def do_kvartirnik(user):
    """Проводит квартирник: дает деньги и опыт."""
    reward = 800 + (user["level"] * 50)  # Награда растет с уровнем
    xp_gain = 10 + user["level"]
    
    user["money"] += reward
    user["xp"] += xp_gain
    user["last_kvartirnik_time"] = time.time()
    
    # Проверка на ап уровня
    leveled_up = False
    while user["level"] < 50 and user["xp"] >= user["level"] * 80:
        user["xp"] -= user["level"] * 80
        user["level"] += 1
        leveled_up = True
    
    save_user(user)
    return reward, xp_gain, leveled_up

def buy_business(user, biz_id):
    """Покупка бизнеса."""
    biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
    if not biz:
        return False, "Бизнес не найден."
    
    current_level = user["businesses"].get(biz_id, 0)
    if current_level >= biz["max_level"]:
        return False, f"У тебя уже максимальный уровень ({current_level}) у {biz['name']}!"
    
    price = biz["cost_per_level"] * (current_level + 1)
    
    if user["money"] >= price:
        user["money"] -= price
        user["businesses"][biz_id] = current_level + 1
        save_user(user)
        return True, f"✅ Купил уровень {current_level + 1} для {biz['name']} за {price} 💰"
    else:
        return False, f"❌ Не хватает денег! Нужно {price}, а у тебя {user['money']}."

def calculate_passive_income(user):
    """Считает пассивный доход за прошедшее время."""
    now = time.time()
    elapsed_hours = int((now - user["last_income_time"]) // 3600)
    
    if elapsed_hours < 1:
        return 0
    
    total_income = 0
    for biz_id, biz_level in user["businesses"].items():
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if biz:
            # Доход растет с уровнем бизнеса: базовый доход * (1 + 0.3 * уровень)
            income_multiplier = 1 + (0.3 * biz_level)
            total_income += biz["income"] * income_multiplier * elapsed_hours
    
    # Бонус за уровень игрока
    bonus_mult = 0.05 * min(user["level"], 10) # До +50% бонуса на 10 уровне
    total_income = int(total_income * (1 + bonus_mult))
    
    user["money"] += total_income
    user["last_income_time"] = now
    save_user(user)
    return total_income

def get_profile_text(user):
    """Формирует текст профиля."""
    rank = RANKS[min(user["level"] - 1, len(RANKS) - 1)]
    
    biz_text = ""
    if not user["businesses"]:
        biz_text = "Пока нет бизнесов 😕"
    else:
        for biz_id, lvl in user["businesses"].items():
            biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
            if biz:
                biz_text += f"🏢 {biz['name']} (Lvl {lvl})\n"
    
    can_kvt, time_left = can_do_kvartirnik(user)
    kvt_status = "✅ Готов к квартирнику!" if can_kvt else f"⏳ Жди еще {time_left} сек."
    
    text = (
        f"👤 Профиль: {user.get('username', 'Аноним')}\n"
        f"💰 Баланс: {user['money']}\n"
        f"⭐ Ранг: {rank} (Уровень {user['level']})\n\n"
        f"{biz_text}\n"
        f"🎤 Квартирник: {kvt_status}\n"
        f"⚡ Пассивный доход начисляется автоматически."
    )
    return text
  
