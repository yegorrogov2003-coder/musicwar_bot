import telebot
import random
import sqlite3
import os
import time

TOKEN = "8824209793:AAGCrt3y9wLDDE70jP9Mr5rem5bx_574pm4"
bot = telebot.TeleBot(TOKEN)

DB_PATH = "musicwar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            group_name TEXT DEFAULT '',
            money INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            user_id INTEGER,
            business_id INTEGER,
            level INTEGER DEFAULT 0,
            owned INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, business_id)
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных создана")

def register_user(user_id, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, xp, level) VALUES (?, ?, 1000, 0, 1)", (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def update_money(user_id, amount):
    conn = get_db()
    conn.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def set_group(user_id, group_name):
    conn = get_db()
    conn.execute("UPDATE users SET group_name = ? WHERE user_id = ?", (group_name, user_id))
    conn.commit()
    conn.close()

def get_user_businesses(user_id):
    conn = get_db()
    businesses = conn.execute("SELECT * FROM businesses WHERE user_id = ? AND owned = 1", (user_id,)).fetchall()
    conn.close()
    return businesses

def buy_business(user_id, business_id):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO businesses (user_id, business_id, owned, level) VALUES (?, ?, 1, 0)", (user_id, business_id))
    conn.commit()
    conn.close()

def get_business_level(user_id, business_id):
    conn = get_db()
    result = conn.execute("SELECT level FROM businesses WHERE user_id = ? AND business_id = ?", (user_id, business_id)).fetchone()
    conn.close()
    return result["level"] if result else 0

def add_xp(user_id, amount):
    conn = get_db()
    user = conn.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if user:
        new_xp = user["xp"] + amount
        current_level = user["level"]
        leveled_up = False
        while new_xp >= current_level * 100:
            new_xp -= current_level * 100
            current_level += 1
            leveled_up = True
        conn.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, current_level, user_id))
        conn.commit()
        conn.close()
        return leveled_up, current_level
    conn.close()
    return False, 1

def get_rank(level):
    if level <= 5: return "Новичок"
    elif level <= 10: return "Андеграунд"
    elif level <= 15: return "Хип-хопер"
    elif level <= 20: return "Прорыв"
    elif level <= 25: return "Известный"
    elif level <= 30: return "Популярный"
    elif level <= 35: return "Топ-чарт"
    elif level <= 40: return "Платиновый"
    elif level <= 45: return "Бриллиантовый"
    else: return "Music Legend"

BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 50000, "income": 5000},
    {"id": 2, "name": "Студия звука", "price": 120000, "income": 10000},
    {"id": 3, "name": "Музыкальный магазин", "price": 300000, "income": 22000},
    {"id": 4, "name": "Рэп-баттл", "price": 600000, "income": 40000},
    {"id": 5, "name": "Студия записи", "price": 1200000, "income": 80000},
    {"id": 6, "name": "Звукозаписывающая студия", "price": 3000000, "income": 200000},
    {"id": 7, "name": "Продакшн", "price": 6000000, "income": 400000},
    {"id": 8, "name": "Ночной клуб", "price": 15000000, "income": 950000},
    {"id": 9, "name": "Радио", "price": 30000000, "income": 1900000},
    {"id": 10, "name": "Клипмейкер", "price": 60000000, "income": 3800000},
    {"id": 11, "name": "ТВ-канал", "price": 120000000, "income": 7500000},
    {"id": 12, "name": "Медиаимперия", "price": 300000000, "income": 18000000}
]

@bot.message_handler(commands=['start'])
def start_cmd(message):
    start(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["старт", "/start"])
def start_rus(message):
    start(message)

def start(message):
    user_id = message.chat.id
    username = message.from_user.username or "без_юзернейма"
    register_user(user_id, username)
    user = get_user(user_id)

    if not user["group_name"]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("Реперы", callback_data="group_Реперы"),
            telebot.types.InlineKeyboardButton("Рокеры", callback_data="group_Рокеры")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("Меломаны", callback_data="group_Меломаны"),
            telebot.types.InlineKeyboardButton("Клубмены", callback_data="group_Клубмены")
        )
        bot.send_message(message.chat.id, "Добро пожаловать! Выбери свою группировку:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"С возвращением! Группировка: {user['group_name']}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(f"Ты выбрал группировку: {group_name}!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['квартирник'])
def attack_cmd(message):
    attack(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["квартирник"])
def attack_rus(message):
    attack(message)

def attack(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return
    if not user["group_name"]:
        bot.send_message(message.chat.id, "Выбери группировку через /start")
        return

    income = random.randint(1000, 5000)
    xp_gain = random.randint(10, 25)
    update_money(user_id, income)
    leveled_up, new_level = add_xp(user_id, xp_gain)
    user = get_user(user_id)

    msg = f"Ты заработал {income} монет!\nОпыт: +{xp_gain}\nВсего монет: {user['money']}"

    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\n\nУРОВЕНЬ ПОВЫШЕН! Уровень: {new_level} ({rank})"
        if new_level % 10 == 0:
            msg += f"\nБонус к доходу: +{new_level // 2}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['профиль'])
def profile_cmd(message):
    profile(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["профиль"])
def profile_rus(message):
    profile(message)

def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    group = user["group_name"] or "не выбрана"
    businesses = get_user_businesses(user_id)
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        total_income += income

    level_bonus = (user["level"] // 10) * 5
    total_income = int(total_income * (1 + level_bonus / 100))
    rank = get_rank(user["level"])
    xp_for_next = user["level"] * 100

    msg = f"=== ПРОФИЛЬ ===\n\n"
    msg += f"Игрок: {user['username']}\n"
    msg += f"Группировка: {group}\n"
    msg += f"Уровень: {user['level']} ({rank})\n"
    msg += f"Опыт: {user['xp']}/{xp_for_next}\n"
    msg += f"Монет: {user['money']}\n"
    msg += f"Доход: {total_income} монет/час"
    if level_bonus > 0:
        msg += f"\nБонус уровня: +{level_bonus}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['бизнесы'])
def businesses_cmd(message):
    businesses(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["бизнесы"])
def businesses_rus(message):
    businesses(message)

def businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    msg = "=== МАГАЗИН БИЗНЕСОВ ===\n\n"
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "ВЛАДЕЕШЬ" if owned else "НЕТ"
        msg += f"{b['id']}. {b['name']}\n"
        msg += f"   Цена: {b['price']} | Доход: {b['income']}/ч [{status}]\n\n"
    msg += "Напиши: /купить N"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['купить'])
def buy_cmd(message):
    buy(message)

@bot.message_handler(func=lambda message: message.text.lower().startswith("купить бизнес"))
def buy_rus(message):
    buy(message)

def buy(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Формат: /купить N или Купить бизнес N")
            return
        business_id = int(parts[-1])
    except:
        bot.send_message(message.chat.id, "Формат: /купить N или Купить бизнес N")
        return

    if business_id < 1 or business_id > len(BUSINESSES):
        bot.send_message(message.chat.id, "Нет такого бизнеса!")
        return

    if get_business_level(user_id, business_id) > 0:
        bot.send_message(message.chat.id, "У тебя уже есть этот бизнес!")
        return

    b = BUSINESSES[business_id - 1]
    if user["money"] < b["price"]:
        bot.send_message(message.chat.id, f"Нужно {b['price']} монет!")
        return

    update_money(user_id, -b["price"])
    buy_business(user_id, business_id)
    add_xp(user_id, 50)
    bot.send_message(message.chat.id, f"Куплен: {b['name']}! +50 XP")

@bot.message_handler(commands=['моибизнесы'])
def mybusiness_cmd(message):
    mybusiness(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["мои бизнесы"])
def mybusiness_rus(message):
    mybusiness(message)

def mybusiness(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    businesses = get_user_businesses(user_id)
    if not businesses:
        bot.send_message(message.chat.id, "У тебя нет бизнесов!")
        return

    level_bonus = (user["level"] // 10) * 5
    msg = "=== МОИ БИЗНЕСЫ ===\n\n"
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        income = int(income * (1 + level_bonus / 100))
        total_income += income
        msg += f"{biz['name']} (ур.{b['level']}) — {income} монет/час\n"
    msg += f"\nОбщий доход: {total_income} монет/час"
    if level_bonus > 0:
        msg += f"\nБонус уровня: +{level_bonus}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['помощь'])
def help_cmd(message):
    help_msg(message)

@bot.message_handler(func=lambda message: message.text.lower() in ["помощь"])
def help_rus(message):
    help_msg(message)

def help_msg(message):
    bot.send_message(message.chat.id,
        "=== ПОМОЩЬ ===\n\n"
        "/start или старт — регистрация\n"
        "/квартирник или квартирник — заработать монеты\n"
        "/профиль или профиль — статистика\n"
        "/бизнесы или бизнесы — магазин\n"
        "/купить N или купить бизнес N — купить бизнес\n"
        "/моибизнесы или мои бизнесы — твои бизнесы\n"
        "/помощь или помощь — это меню")

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Неизвестная команда. Напиши /помощь")

if __name__ == "__main__":
    init_db()
    print("БОТ ЗАПУЩЕН!")
    print("MusicWar Bot готов к работе!")

    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
