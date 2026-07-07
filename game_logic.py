import time
import random

# --- НАСТРОЙКИ БИЗНЕСОВ ---
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "base_price": 50000, "base_income": 5000, "max_level": 10},
    {"id": 2, "name": "Студия звука", "base_price": 120000, "base_income": 10000, "max_level": 10},
    {"id": 3, "name": "Музыкальный магаз", "base_price": 300000, "base_income": 22000, "max_level": 10},
    {"id": 4, "name": "Рэп-баттл", "base_price": 600000, "base_income": 40000, "max_level": 10},
    {"id": 5, "name": "Звукозапись", "base_price": 1200000, "base_income": 80000, "max_level": 10},
    {"id": 6, "name": "Music War Records", "base_price": 3000000, "base_income": 200000, "max_level": 10},
    {"id": 7, "name": "Продакшн", "base_price": 6000000, "base_income": 400000, "max_level": 10},
    {"id": 8, "name": "Ночной клуб", "base_price": 15000000, "base_income": 950000, "max_level": 10},
    {"id": 9, "name": "Радио", "base_price": 30000000, "base_income": 1900000, "max_level": 10},
    {"id": 10, "name": "Клипмейкер", "base_price": 60000000, "base_income": 3800000, "max_level": 10},
    {"id": 11, "name": "ТВ-канал", "base_price": 120000000, "base_income": 7500000, "max_level": 10},
    {"id": 12, "name": "Медиаимперия", "base_price": 300000000, "base_income": 18000000, "max_level": 10},
]

DISTRICTS = {
    "Бит-стрит": {"bonus_type": "xp", "value": 1.3},
    "Золотая студия": {"bonus_type": "income", "value": 1.3},
    "Бас-квартал": {"bonus_type": "raid", "value": 1.3}
}

USERS = {}

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "id": user_id,
            "balance": 10000,
            "cash": 0,
            "xp": 0,
            "level": 1,
            "businesses": {},
            "last_kvartirnik": 0,
            "last_label_show": 0,
            "gang_id": None,
            "gang_role": "none",
            "fans": 0,
            "vip_until": 0,
            "global_boost_active": False,
            "district_bonus": 1.0
        }
    return USERS[user_id]

def calculate_income_multiplier(user):
    multiplier = 1.0
    for biz_id, level in user["businesses"].items():
        multiplier *= (1 + (0.1 * level))
    
    if user["fans"] > 100000:
        multiplier *= 1.3
    elif user["fans"] > 10000:
        multiplier *= 1.2
    elif user["fans"] > 1000:
        multiplier *= 1.1
    elif user["fans"] > 100:
        multiplier *= 1.05
    
    multiplier *= user["district_bonus"]
    if user["vip_until"] > time.time():
        multiplier *= 1.2
    if user["global_boost_active"]:
        multiplier *= 2.0
    return multiplier

def calculate_passive_income(user):
    total_income = 0
    mult = calculate_income_multiplier(user)
    for biz_id, level in user["businesses"].items():
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if not biz: continue
        level_mult = 1 + (0.1 * level)
        total_income += int(biz["base_income"] * level_mult)
    return int(total_income * mult)

def get_profile_text(user):
    text = (
        f"👤 **Профиль Music War**\n\n"
        f"💰 Баланс: {user['balance']:,}\n"
        f"💎 Кэш: {user['cash']:,}\n"
        f"📈 Уровень: {user['level']} ({user['xp']} XP)\n"
    )
    if user["gang_id"]:
        text += f"🏙️ Банда: ID {user['gang_id']} | Роль: {user['gang_role']}\n"
        text += f"🛡️ Район: Бонус x{user['district_bonus']}\n"
    else:
        text += "🏙️ Банда: Не состоит\n"
    if user["fans"] > 0:
        text += f"🎸 Фанаты: {user['fans']:,}\n"
    if user["vip_until"] > time.time():
        text += f"👑 VIP активен\n"
    text += "\n🏢 Бизнесы:\n"
    if not user["businesses"]:
        text += "   (Нет бизнесов)\n"
    else:
        for biz_id, level in user["businesses"].items():
            biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
            if biz:
                text += f"   • {biz['name']} (Lvl {level})\n"
    return text

# Квартирник: КД 90 сек, награда снижена для баланса
def can_do_kvartirnik(user):
    cooldown_seconds = 90
    now = time.time()
    time_since = now - user["last_kvartirnik"]
    if time_since >= cooldown_seconds:
        return True, 0
    return False, int(cooldown_seconds - time_since)

def do_kvartirnik(user):
    user["last_kvartirnik"] = time.time()
    base_reward = 1500 + (user["level"] * 200)
    reward = int(base_reward / 4)  # снижено в 4 раза
    xp = 50 + (user["level"] * 5)
    
    if user["gang_id"] and user["district_bonus"] > 1.0:
        reward = int(reward * user["district_bonus"])
        xp = int(xp * user["district_bonus"])

    user["balance"] += reward
    user["xp"] += xp
    
    lvl_up = False
    while user["xp"] >= user["level"] * 200:
        user["level"] += 1
        lvl_up = True
    return reward, xp, lvl_up

# Лейблы (групповые выступления)
def can_do_label_show(user):
    cooldown_seconds = 3600
    now = time.time()
    time_since = now - user["last_label_show"]
    if time_since >= cooldown_seconds:
        return True, 0
    return False, int(cooldown_seconds - time_since)

def do_label_show(user):
    user["last_label_show"] = time.time()
    base_money = 50000
    base_fans = 50
    biz_bonus = 1.0
    for lvl in user["businesses"].values():
        biz_bonus += (0.05 * lvl)
    money_reward = int(base_money * biz_bonus)
    fans_reward = int(base_fans * biz_bonus)
    user["balance"] += money_reward
    user["fans"] += fans_reward
    return money_reward, fans_reward

# Покупка/прокачка бизнеса
def buy_business(user, biz_id):
    biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
    if not biz:
        return False, "❌ Бизнес не найден."
    current_level = user["businesses"].get(biz_id, 0)
    if current_level >= biz["max_level"]:
        return False, f"🏆 {biz['name']} уже на макс. уровне!"
    next_level = current_level + 1
    price = int(biz["base_price"] * 0.1 * next_level)
    if user["balance"] < price:
        return False, f"❌ Не хватает денег! Нужно {price:,}, у тебя {user['balance']:,}."
    user["balance"] -= price
    user["businesses"][biz_id] = next_level
    return True, f"✅ Прокачан {biz['name']} до Lvl {next_level} за {price:,}!"

def get_business_display_info(user):
    info_list = []
    emoji_map = {
        "Битмейкер": "🎹", "Студия звука": "🎤", "Музыкальный магаз": "👕",
        "Рэп-баттл": "🥊", "Звукозапись": "🎙️", "Music War Records": "💿",
        "Продакшн": "🎬", "Ночной клуб": "🌃", "Радио": "📻",
        "Клипмейкер": "🎥", "ТВ-канал": "📺", "Медиаимперия": "🌐"
    }
    for biz in BUSINESSES:
        biz_id = biz["id"]
        current_lvl = user["businesses"].get(biz_id, 0)
        current_income = int(biz["base_income"] * (1 + (0.1 * current_lvl)))
        next_lvl = current_lvl + 1
        if current_lvl >= biz["max_level"]:
            price_text = "🏆 Макс. уровень"
            buy_btn_text = None
        else:
            price = int(biz["base_price"] * 0.1 * next_lvl)
            price_text = f"{price:,}$"
            buy_btn_text = f"Купить {biz['name']}"
        info_list.append({
            "name": biz["name"],
            "emoji": emoji_map.get(biz["name"], "🏢"),
            "price": price_text,
            "income": f"{current_income:,}$",
            "current_lvl": current_lvl,
            "buy_btn_text": buy_btn_text
        })
    return info_list

# Донат (Кэш)
def buy_with_cash(user, item_type):
    prices = {
        "100k_coins": {"cash": 5, "coins": 100000},
        "1m_coins": {"cash": 40, "coins": 1000000},
        "boost_2x": {"cash": 10, "type": "boost"},
        "vip_1d": {"cash": 20, "type": "vip"},
        "case": {"cash": 10, "type": "case"},
        "100_fans": {"cash": 5, "fans": 100},
        "1k_fans": {"cash": 40, "fans": 1000},
        "10k_fans": {"cash": 300, "fans": 10000},
    }
    item = prices.get(item_type)
    if not item:
        return False, "❌ Товар не найден"
    if user["cash"] < item["cash"]:
        return False, f"❌ Не хватает Кэш! Нужно {item['cash']}, у тебя {user['cash']}."
    user["cash"] -= item["cash"]
    if "coins" in item:
        user["balance"] += item["coins"]
        return True, f"✅ Получено {item['coins']:,} монет!"
    elif "fans" in item:
        user["fans"] += item["fans"]
        return True, f"✅ Получено {item['fans']:,} фанатов!"
    elif item.get("type") == "boost":
        user["global_boost_active"] = True
        return True, "✅ Активирован буст x2 на 1 час!"
    elif item.get("type") == "vip":
        user["vip_until"] = time.time() + 86400
        return True, "✅ VIP активен 24 часа!"
    elif item.get("type") == "case":
        rand = random.randint(1, 3)
        if rand == 1:
            user["balance"] += 500000
            return True, "📦 Кейс: +500,000 монет!"
        elif rand == 2:
            user["fans"] += 500
            return True, "📦 Кейс: +500 фанатов!"
        else:
            user["vip_until"] = time.time() + 3600
            return True, "📦 Кейс: VIP на 1 час!"
    return False, "Ошибка покупки"
    
