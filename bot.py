import telebot
import random
import sqlite3
import os
import time
import sys

print("=== START BOT ===", file=sys.stderr)
sys.stderr.flush()

TOKEN = "8824209793:AAGCrt3y9wLDDE70jP9Mr5rem5bx_574pm4"
bot = telebot.TeleBot(TOKEN)

DB_PATH = "musicwar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("=== CREATE DB ===", file=sys.stderr)
    sys.stderr.flush()
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            group_name TEXT DEFAULT '',
            money INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            gang_id INTEGER DEFAULT 0
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS gangs (
            gang_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            leader_id INTEGER,
            members TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()
    print("=== DB CREATED ===", file=sys.stderr)
    sys.stderr.flush()

def register_user(user_id, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, xp, level, gang_id) VALUES (?, ?, 1000, 0, 1, 0)", (user_id, username))
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

# ===== GANG FUNCTIONS =====

def create_gang(leader_id, name):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO gangs (name, leader_id, members) VALUES (?, ?, ?)",
            (name, leader_id, str(leader_id))
        )
        gang_id = cursor.lastrowid
        conn.execute(
            "UPDATE users SET gang_id = ? WHERE user_id = ?",
            (gang_id, leader_id)
        )
        conn.commit()
        return gang_id
    except Exception as e:
        print(f"create_gang error: {e}")
        return None
    finally:
        conn.close()

def get_gang(gang_id):
    conn = get_db()
    gang = conn.execute("SELECT * FROM gangs WHERE gang_id = ?", (gang_id,)).fetchone()
    conn.close()
    return gang

def get_gang_by_name(name):
    conn = get_db()
    gang = conn.execute("SELECT * FROM gangs WHERE name = ?", (name,)).fetchone()
    conn.close()
    return gang

def get_gang_members(gang_id):
    conn = get_db()
    gang = conn.execute("SELECT members FROM gangs WHERE gang_id = ?", (gang_id,)).fetchone()
    conn.close()
    if gang and gang["members"]:
        return [int(m) for m in gang["members"].split(",") if m]
    return []

def get_gang_members_count(gang_id):
    return len(get_gang_members(gang_id))

def add_member(gang_id, user_id):
    conn = get_db()
    members = get_gang_members(gang_id)
    if user_id not in members:
        members.append(user_id)
        members_str = ",".join(str(m) for m in members)
        conn.execute(
            "UPDATE gangs SET members = ? WHERE gang_id = ?",
            (members_str, gang_id)
        )
        conn.execute(
            "UPDATE users SET gang_id = ? WHERE user_id = ?",
            (gang_id, user_id)
        )
        conn.commit()
    conn.close()

def remove_member(gang_id, user_id):
    conn = get_db()
    members = get_gang_members(gang_id)
    if user_id in members:
        members.remove(user_id)
        members_str = ",".join(str(m) for m in members) if members else ""
        conn.execute(
            "UPDATE gangs SET members = ? WHERE gang_id = ?",
            (members_str, gang_id)
        )
        conn.execute(
            "UPDATE users SET gang_id = 0 WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        if not members:
            conn.execute("DELETE FROM gangs WHERE gang_id = ?", (gang_id,))
            conn.commit()
    conn.close()
    return True

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

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(" Apartment ", " Profile ")
    markup.row(" Businesses ", " My businesses ")
    markup.row(" Gang ", " Donate ")
    markup.row(" Help ", " About ")
    return markup

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
        bot.send_message(message.chat.id,
            "=== MUSICWAR ===\n"
            "Welcome!\n"
            "Choose your group:",
            reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
            f"=== MUSICWAR ===\n"
            f"Welcome back!\n"
            f"Group: {user['group_name']}",
            reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(
        f"You chose: {group_name}!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.send_message(call.message.chat.id,
        "Use buttons below:",
        reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in [" Apartment ", "Apartment"])
def attack(message):
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

    msg = f"=== APARTMENT ===\n"
    msg += f"Earned: {income} coins\n"
    msg += f"XP: +{xp_gain}\n"
    msg += f"Total coins: {user['money']}"

    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\n\n=== LEVEL UP! ===\n"
        msg += f"Level: {new_level}\n"
        msg += f"Rank: {rank}"
        if new_level % 10 == 0:
            msg += f"\nIncome bonus: +{new_level // 2}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Profile ", "Profile"])
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    group = user["group_name"] or "not chosen"
    gang_name = "None"
    if user["gang_id"] != 0:
        gang = get_gang(user["gang_id"])
        if gang:
            gang_name = gang["name"]

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

    msg = "=== PROFILE ===\n\n"
    msg += f"Player: {user['username']}\n"
    msg += f"Group: {group}\n"
    msg += f"Gang: {gang_name}\n"
    msg += f"Level: {user['level']} ({rank})\n"
    msg += f"XP: {user['xp']}/{xp_for_next} XP\n"
    msg += f"Coins: {user['money']}\n"
    msg += f"Income: {total_income} coins/hour"
    if level_bonus > 0:
        msg += f"\nLevel bonus: +{level_bonus}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Businesses ", "Businesses"])
def show_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    msg = "=== BUSINESS SHOP ===\n\n"
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "OWN" if owned else "NO"
        msg += f"{b['id']}. {b['name']}\n"
        msg += f"   Price: {b['price']} | Income: {b['income']}/h [{status}]\n\n"
    msg += "Write: Buy business N"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text.lower().startswith("buy business"))
def buy_business_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    try:
        business_id = int(message.text.split()[-1])
    except:
        bot.send_message(message.chat.id, "Format: Buy business N")
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

@bot.message_handler(func=lambda message: message.text in [" My businesses ", "My businesses"])
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
    msg = "=== MY BUSINESSES ===\n\n"
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        income = int(income * (1 + level_bonus / 100))
        total_income += income
        msg += f"{biz['name']} (lvl.{b['level']}) — {income} coins/h\n"
    msg += f"\nTotal income: {total_income} coins/h"
    if level_bonus > 0:
        msg += f"\nLevel bonus: +{level_bonus}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Gang ", "Gang"])
def gang_menu_button(message):
    gang_menu(message)

@bot.message_handler(commands=['gang'])
def gang_menu(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    if user["gang_id"] == 0:
        bot.send_message(message.chat.id,
            "=== GANG ===\n\n"
            "You are not in a gang!\n\n"
            "Commands:\n"
            "/gang_create [name] — create gang (75,000 coins)\n"
            "/gang_join [name] — join gang")
    else:
        gang = get_gang(user["gang_id"])
        if gang:
            members = get_gang_members(user["gang_id"])
            msg = f"=== GANG ===\n\n"
            msg += f"Name: {gang['name']}\n"
            msg += f"Members: {len(members)}\n\n"
            msg += "Commands:\n"
            msg += "/gang_leave — leave\n"
            msg += "/gang_members — list members"
            bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, "Gang not found!")

@bot.message_handler(commands=['gang_create'])
def gang_create_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    if user["gang_id"] != 0:
        bot.send_message(message.chat.id, "You are already in a gang!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Format: /gang_create [name]")
        return

    name = args[1].strip()
    if len(name) < 3 or len(name) > 20:
        bot.send_message(message.chat.id, "Name must be 3-20 characters!")
        return

    if get_gang_by_name(name):
        bot.send_message(message.chat.id, "Gang with this name already exists!")
        return

    if user["money"] < 75000:
        bot.send_message(message.chat.id, f"Need 75,000 coins! You have {user['money']}")
        return

    update_money(user_id, -75000)
    gang_id = create_gang(user_id, name)
    if gang_id:
        add_xp(user_id, 100)
        bot.send_message(message.chat.id, f"Gang '{name}' created! +100 XP")
    else:
        bot.send_message(message.chat.id, "Error creating gang!")

@bot.message_handler(commands=['gang_join'])
def gang_join_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    if user["gang_id"] != 0:
        bot.send_message(message.chat.id, "You are already in a gang!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Format: /gang_join [name]")
        return

    name = args[1].strip()
    gang = get_gang_by_name(name)
    if not gang:
        bot.send_message(message.chat.id, "Gang not found!")
        return

    add_member(gang["gang_id"], user_id)
    add_xp(user_id, 25)
    bot.send_message(message.chat.id, f"You joined gang '{name}'! +25 XP")

@bot.message_handler(commands=['gang_leave'])
def gang_leave_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    if user["gang_id"] == 0:
        bot.send_message(message.chat.id, "You are not in a gang!")
        return

    gang = get_gang(user["gang_id"])
    if not gang:
        bot.send_message(message.chat.id, "Gang not found!")
        return

    remove_member(user["gang_id"], user_id)
    bot.send_message(message.chat.id, f"You left gang '{gang['name']}'!")

@bot.message_handler(commands=['gang_members'])
def gang_members_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Write /start")
        return

    if user["gang_id"] == 0:
        bot.send_message(message.chat.id, "You are not in a gang!")
        return

    gang = get_gang(user["gang_id"])
    if not gang:
        bot.send_message(message.chat.id, "Gang not found!")
        return

    members = get_gang_members(user["gang_id"])
    if not members:
        bot.send_message(message.chat.id, "No members in gang yet.")
        return

    msg = f"=== GANG MEMBERS ===\n\n"
    msg += f"Gang: {gang['name']}\n\n"
    for m in members:
        member = get_user(int(m))
        if member:
            msg += f"- {member['username']}\n"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Donate ", "Donate"])
def donate(message):
    bot.send_message(message.chat.id,
        "=== DONATE ===\n\n"
        "Cash - 100 coins (50 rub)\n"
        "Cash+ - 500 coins (200 rub)\n"
        "VIP - 1000 coins (400 rub)\n\n"
        "To buy contact @SupportBot")

@bot.message_handler(func=lambda message: message.text in [" Help ", "Help"])
def help_command(message):
    bot.send_message(message.chat.id,
        "=== HELP ===\n\n"
        "Apartment - earn coins and XP\n"
        "Profile - your stats\n"
        "Businesses - shop\n"
        "My businesses - your businesses\n"
        "Gang - create/join gang\n"
        "Donate - buy coins")

@bot.message_handler(func=lambda message: message.text in [" About ", "About"])
def about(message):
    bot.send_message(message.chat.id,
        "=== ABOUT ===\n\n"
        "MusicWar Bot v2.0\n"
        "50 levels\n"
        "12 businesses\n"
        "4 groups")

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Unknown command. Use buttons below or /help.")

if __name__ == "__main__":
    init_db()
    print("=== DB READY ===", file=sys.stderr)
    sys.stderr.flush()
    pr
