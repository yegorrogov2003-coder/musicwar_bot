import time

# --- НАСТРОЙКИ БИЗНЕСОВ (твои названия и логика сохранены) ---
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "income": 400, "cost_per_level": 1800, "max_level": 10},
    {"id": 2, "name": "Студия звука", "income": 1200, "cost_per_level": 5500, "max_level": 10},
    {"id": 3, "name": "Лейбл", "income": 3500, "cost_per_level": 18000, "max_level": 10},
    {"id": 4, "name": "Концертный зал", "income": 9000, "cost_per_level": 45000, "max_level": 10},
]

# Хранилище пользователей (в памяти для примера; позже заменим на SQLite)
USERS = {}

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "id": user_id,
            "balance": 5000,
            "xp": 0,
            "level": 1,
            "businesses": {},  # {business_id: level}
            "last_kvartirnik": 0,
        }
    return USERS[user_id]

def calculate_passive_income(user):
    total_income = 0
    for biz_id, level in user["businesses"].items():
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if not biz:
            continue
        # Доход растет на 30% за каждый уровень
        multiplier = 1 + (0.3 * level)
        total_income += int(biz["income"] * multiplier)
    return total_income

def get_profile_text(user):
    text = (
        f"👤 **Профиль**\n\n"
        f"💰 Баланс: {user['balance']:,}\n"
        f"📈 Уровень: {user['level']} ({user['xp']} XP)\n"
        f"🏢 Бизнесы: {len(user['businesses'])}\n"
    )
    if user["businesses"]:
        text += "\n💼 Твои бизнесы:\n"
        for biz_id, level in user["businesses"].items():
            biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
            if biz:
                text += f"   • {biz['name']} — Уровень {level}\n"
    return text

def can_do_kvartirnik(user):
    cooldown_seconds = 1800  # 30 минут
    now = time.time()
    time_since = now - user["last_kvartirnik"]
    if time_since >= cooldown_seconds:
        return True, 0
    time_left = int(cooldown_seconds - time_since)
    return False, time_left

def do_kvartirnik(user):
    user["last_kvartirnik"] = time.time()
    reward = 1500 + (user["level"] * 200)
    xp = 50 + (user["level"] * 5)
    user["balance"] += reward
    user["xp"] += xp
    lvl_up = False
    # Простая система уровней: каждые 200 XP
    while user["xp"] >= user["level"] * 200:
        user["level"] += 1
        lvl_up = True
    return reward, xp, lvl_up

def buy_business(user, biz_id):
    biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
    if not biz:
        return False, "❌ Бизнес не найден."
    
    current_level = user["businesses"].get(biz_id, 0)
    if current_level >= biz["max_level"]:
        return False, f"🏆 {biz['name']} уже на максимальном уровне!"
    
    next_level = current_level + 1
    price = biz["cost_per_level"] * next_level
    
    if user["balance"] < price:
        return False, f"❌ Не хватает денег! Нужно {price:,}, у тебя {user['balance']:,}."
    
    user["balance"] -= price
    user["businesses"][biz_id] = next_level
    return True, f"✅ Ты купил уровень {next_level} для {biz['name']} за {price:,}!"

def get_business_display_info(user):
    """
    Формирует список бизнесов для красивого вывода (как на скрине):
    Эмодзи Название — Цена → Доход
    """
    info_list = []
    
    # Подбери эмодзи под свои названия (можно поменять на любые)
    emoji_map = {
        "Битмейкер": "🎹",
        "Студия звука": "🎤",
        "Лейбл": "🎛️",
        "Концертный зал": "🗣️",
    }
    
    for biz in BUSINESSES:
        biz_id = biz["id"]
        current_lvl = user["businesses"].get(biz_id, 0)
        
        # Считаем доход на текущем уровне
        income_multiplier = 1 + (0.3 * current_lvl)
        current_income = int(biz["income"] * income_multiplier)
        
        # Считаем цену следующего уровня (если не макс)
        next_lvl = current_lvl + 1
        if current_lvl >= biz["max_level"]:
            price_text = "🏆 Макс. уровень"
            buy_btn_text = None
        else:
            price = biz["cost_per_level"] * next_lvl
            price_text = f"{price:,}\$"
            buy_btn_text = f"Купить {biz['name']}"
        
        info_list.append({
            "name": biz["name"],
            "emoji": emoji_map.get(biz["name"], "🏢"),
            "price": price_text,
            "income": f"{current_income:,}\$",
            "current_lvl": current_lvl,
            "buy_btn_text": buy_btn_text
        })
    
    return info_list
    
