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
    print("База данных создана")

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

# ===== ФУНКЦИИ БАНД =====

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

# ===== МУЗЫКАЛЬНЫЕ БИЗНЕСЫ (ПРОВЕРЕНО) =====
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

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(" Квартирник ", " Профиль ")
    markup.row(" Бизнесы ", " Мои бизнесы ")
    markup.row(" Банда ", " Донат ")
    markup.row(" Помощь ", " О боте ")
    return markup

# ===== БИЗНЕСЫ С КНОПКАМИ =====

@bot.message_handler(func=lambda message: message.text in [" Бизнесы ", "Бизнесы"])
def show_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "✅" if owned else ""
        markup.add(telebot.types.InlineKeyboardButton(
            f"{b['id']}. {b['name']} {status}",
            callback_data=f"biz_{b['id']}"
        ))

    bot.send_message(message.chat.id,
        "=== МАГАЗИН БИЗНЕСОВ ===\n"
        "Нажми на бизнес для просмотра:",
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("biz_"))
def show_business_card(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    business_id = int(call.data.split("_")[1])
    biz = BUSINESSES[business_id - 1]

    owned = get_business_level(user_id, business_id) > 0
    level = get_business_level(user_id, business_id)

    msg = f"=== {biz['name']} ===\n\n"
    msg += f"💰 Цена: {biz['price']} монет\n"
    msg += f"📈 Доход: {biz['income']} монет/час\n"
    if owned:
        msg += f"📊 Уровень: {level}\n"
        msg += f"✅ Статус: ВЛАДЕЕШЬ\n"
    else:
        msg += f"❌ Статус: НЕТ\n"

    markup = telebot.types.InlineKeyboardMarkup()
    if not owned:
        markup.add(telebot.types.InlineKeyboardButton("💰 Купить", callback_data=f"buy_{business_id}"))
    markup.add(telebot.types.InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_businesses"))
    markup.add(telebot.types.InlineKeyboardButton("❌ Закрыть", callback_data="close"))

    bot.edit_message_text(
        msg,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_business_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    business_id = int(call.data.split("_")[1])
    biz = BUSINESSES[business_id - 1]

    if get_business_level(user_id, business_id) > 0:
        bot.answer_callback_query(call.id, "У тебя уже есть этот бизнес!")
        return

    if user["money"] < biz["price"]:
        bot.answer_callback_query(call.id, f"Нужно {biz['price']} монет! У тебя {user['money']}")
        return

    update_money(user_id, -biz["price"])
    buy_business(user_id, business_id)
    add_xp(user_id, 50)

    bot.answer_callback_query(call.id, f"Куплен: {biz['name']}! +50 XP")

    msg = f"=== {biz['name']} ===\n\n"
    msg += f"💰 Цена: {biz['price']} монет\n"
    msg += f"📈 Доход: {biz['income']} монет/час\n"
    msg += f"✅ Статус: ВЛАДЕЕШЬ\n"

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_businesses"))
    markup.add(telebot.types.InlineKeyboardButton("❌ Закрыть", callback_data="close"))

    bot.edit_message_text(
        msg,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_businesses")
def back_to_businesses(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user:
        bot.answer_callback_query(call.id)
        return

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "✅" if owned else ""
        markup.add(telebot.types.InlineKeyboardButton(
            f"{b['id']}. {b['name']} {status}",
            callback_data=f"biz_{b['id']}"
        ))

    bot.edit_message_text(
        "=== МАГАЗИН БИЗНЕСОВ ===\n"
        "Нажми на бизнес для просмотра:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "close")
def close_message(call):
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.answer_callback_query(call.id)

# ===== ОСТАЛЬНЫЕ ФУНКЦИИ =====

@bot.message_handler(commands=['start'])
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
        bot.send_message(message.chat.id,
            "=== MUSICWAR ===\n"
            "Добро пожаловать!\n"
            "Выбери свою группировку:",
            reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
            f"=== MUSICWAR ===\n"
            f"С возвращением!\n"
            f"Группировка: {user['group_name']}",
            reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(
        f"Ты выбрал группировку: {group_name}!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.send_message(call.message.chat.id,
        "Используй кнопки внизу:",
        reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in [" Квартирник ", "Квартирник"])
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

    msg = f"=== КВАРТИРНИК ===\n"
    msg += f"Заработано: {income} монет\n"
    msg += f"Опыт: +{xp_gain}\n"
    msg += f"Всего монет: {user['money']}"

    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\n\n=== УРОВЕНЬ ПОВЫШЕН! ===\n"
        msg += f"Уровень: {new_level}\n"
        msg += f"Звание: {rank}"
        if new_level % 10 == 0:
            msg += f"\nБонус к доходу: +{new_level // 2}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Профиль ", "Профиль"])
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    group = user["group_name"] or "не выбрана"
    gang_name = "Нет"
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

    msg = "=== ПРОФИЛЬ ===\n\n"
    msg += f"Игрок: {user['username']}\n"
    msg += f"Группировка: {group}\n"
    msg += f"Банда: {gang_name}\n"
    msg += f"Уровень: {user['level']} ({rank})\n"
    msg += f"Опыт: {user['xp']}/{xp_for_next} XP\n"
    msg += f"Монет: {user['money']}\n"
    msg += f"Доход: {total_income} монет/час"
    if level_bonus > 0:
        msg += f"\nБонус уровня: +{level_bonus}%"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in [" Мои бизнесы ", "Мои бизнесы"])
def my_businesses(message):
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

@bot.message_handler(func=lambda message: message.text in [" Банда ", "Банда"])
def gang_menu_button(message):
    gang_menu(message)

@bot.message_handler(commands=['gang'])
def gang_menu(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["gang_id"] == 0:
        bot.send_message(message.chat.id,
            "=== БАНДА ===\n\n"
            "Ты не в банде!\n\n"
            "Команды:\n"
            "/gang_create [название] — создать банду (75,000 монет)\n"
            "/gang_join [название] — вступить в банду")
    else:
        gang = get_gang(user["gang_id"])
        if gang:
            members = get_gang_members(user["gang_id"])
            msg = f"=== БАНДА ===\n\n"
            msg += f"Название: {gang['name']}\n"
            msg += f"Участников: {len(members)}\n\n"
            msg += "Команды:\n"
            msg += "/gang_leave — выйти\n"
            msg += "/gang_members — список участников"
            bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, "Банда не найдена!")

@bot.message_handler(commands=['gang_create'])
def gang_create_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["gang_id"] != 0:
        bot.send_message(message.chat.id, "Ты уже в банде!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Формат: /gang_create [название]")
        return

    name = args[1].strip()
    if len(name) < 3 or len(name) > 20:
        bot.send_message(message.chat.id, "Название от 3 до 20 символов!")
        return

    if get_gang_by_name(name):
        bot.send_message(message.chat.id, "Банда с таким названием уже существует!")
        return

    if user["money"] < 75000:
        bot.send_message(message.chat.id, f"Нужно 75,000 монет! У тебя {user['money']}")
        return

    update_money(user_id, -75000)
    gang_id = create_gang(user_id, name)
    if gang_id:
        add_xp(user_id, 100)
        bot.send_message(message.chat.id, f"Банда '{name}' создана! +100 XP")
    else:
        bot.send_message(message.chat.id, "Ошибка при создании банды!")

@bot.message_handler(commands=['gang_join'])
def gang_join_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["gang_id"] != 0:
        bot.send_message(message.chat.id, "Ты уже в банде!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Формат: /gang_join [название]")
        return

    name = args[1].strip()
    gang = get_gang_by_name(name)
    if not gang:
        bot.send_message(message.chat.id, "Банда не найдена!")
        return

    add_member(gang["gang_id"], user_id)
    add_xp(user_id, 25)
    bot.send_message(message.chat.id, f"Ты вступил в банду '{name}'! +25 XP")

