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
    print("DB created")

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
    if level <= 5: return "Novice"
    elif level <= 10: return "Underground"
    elif level <= 15: return "Hip-Hoper"
    elif level <= 20: return "Breakthrough"
    elif level <= 25: return "Famous"
    elif level <= 30: return "Popular"
    elif level <= 35: return "Top Chart"
    elif level <= 40: return "Platinum"
    elif level <= 45: return "Diamond"
    else: return "Music Legend"

BUSINESSES = [
    {"id": 1, "name": "Bitmaker", "price": 50000, "income": 5000},
    {"id": 2, "name": "Sound Studio", "price": 120000, "income": 10000},
    {"id": 3, "name": "Music Shop", "price": 300000, "income": 22000},
    {"id": 4, "name": "Rap Battle", "price": 600000, "income": 40000},
    {"id": 5, "name": "Record Studio", "price": 1200000, "income": 80000},
    {"id": 6, "name": "Recording Studio", "price": 3000000, "income": 200000},
    {"id": 7, "name": "Production", "price": 6000000, "income": 400000},
    {"id": 8, "name": "Night Club", "price": 15000000, "income": 950000},
    {"id": 9, "name": "Radio", "price": 30000000, "income": 1900000},
    {"id": 10, "name": "Clip Maker", "price": 60000000, "income": 3800000},
    {"id": 11, "name": "TV Channel", "price": 120000000, "income": 7500000},
    {"id": 12, "name": "Media Empire", "price": 300000000, "income": 18000000}
]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.from_user.username or "no_username"
    register_user(user_id, username)
    user = get_user(user_id)

    if not user["group_name"]:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("Rappers", callback_data="group_Rappers"),
            telebot.types.InlineKeyboardButton("Rockers", callback_data="group_Rockers")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("Melomans", callback_data="group_Melomans"),
            telebot.types.InlineKeyboardButton("Clubbers", callback_data="group_Clubbers")
        )
        bot.send_message(message.chat.id, "Welcome! Choose your group:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Welcome back! Group: {user['group_name']}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(f"You chose: {group_name}!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['earn'])
def earn(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return
    if not user["group_name"]:
        bot.send_message(message.chat.id, "Choose group via /start")
        return

    income = random.randint(1000, 5000)
    xp_gain = random.randint(10, 25)
    update_money(user_id, income)
    leveled_up, new_level = add_xp(user_id, xp_gain)
    user = get_user(user_id)

    msg = f"Earned: {income} coins\nXP: +{xp_gain}\nTotal: {user['money']} coins"
    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\n\nLEVEL UP! Level: {new_level} ({rank})"
        if new_level % 10 == 0:
            msg += f"\nIncome bonus: +{new_level // 2}%"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    group = user["group_name"] or "not chosen"
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

    msg = f"Profile:\nPlayer: {user['username']}\nGroup: {group}\nLevel: {user['level']} ({rank})\nXP: {user['xp']}/{xp_for_next}\nCoins: {user['money']}\nIncome: {total_income} coins/h"
    if level_bonus > 0:
        msg += f"\nLevel bonus: +{level_bonus}%"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['business'])
def show_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    msg = "BUSINESS SHOP:\n\n"
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "OWN" if owned else "NO"
        msg += f"{b['id']}. {b['name']} - {b['price']} coins, {b['income']}/h [{status}]\n"
    msg += "\nWrite: /buy N"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['buy'])
def buy_business_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    try:
        business_id = int(message.text.split()[1])
    except:
        bot.send_message(message.chat.id, "Format: /buy N")
        return

    if business_id < 1 or business_id > len(BUSINESSES):
        bot.send_message(message.chat.id, "No such business!")
        return

    if get_business_level(user_id, business_id) > 0:
        bot.send_message(message.chat.id, "You already own this business!")
        return

    b = BUSINESSES[business_id - 1]
    if user["money"] < b["price"]:
        bot.send_message(message.chat.id, f"Need {b['price']} coins!")
        return

    update_money(user_id, -b["price"])
    buy_business(user_id, business_id)
    add_xp(user_id, 50)
    bot.send_message(message.chat.id, f"Bought: {b['name']}! +50 XP")

@bot.message_handler(commands=['mybusiness'])
def my_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    businesses = get_user_businesses(user_id)
    if not businesses:
        bot.send_message(message.chat.id, "You have no businesses!")
        return

    level_bonus = (user["level"] // 10) * 5
    msg = "MY BUSINESSES:\n\n"
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        income = int(income * (1 + level_bonus / 100))
        total_income += income
        msg += f"{biz['name']} (lvl.{b['level']}) - {income} coins/h\n"
    msg += f"\nTotal income: {total_income} coins/h"
    if level_bonus > 0:
        msg += f"\nLevel bonus: +{level_bonus}%"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
        "COMMANDS:\n"
        "/start - Register\n"
        "/earn - Earn coins and XP\n"
        "/profile - Your stats\n"
        "/business - Shop\n"
        "/buy N - Buy business N\n"
        "/mybusiness - Your businesses\n"
        "/help - This menu")

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Unknown command. Type /help")

if __name__ == "__main__":
    init_db()
    print("BOT STARTED!")
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
