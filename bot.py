import telebot
import time
import random
import sqlite3
import os
import bands

TOKEN = "8824209793:AAGCrt3y9wLDDE70jP9Mr5rem5bx_574pm4"
bot = telebot.TeleBot(TOKEN)

DB_PATH = "musicwar.db"
if not os.path.exists(DB_PATH):
    open(DB_PATH, "w").close()

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
            cash INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            boost_end INTEGER DEFAULT 0,
            vip_end INTEGER DEFAULT 0,
            band_id INTEGER DEFAULT 0,
            band_role TEXT DEFAULT 'member',
            leave_band_time INTEGER DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS bands (
            band_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            leader_id INTEGER,
            deputy_id INTEGER DEFAULT 0,
            members TEXT DEFAULT '',
            slots INTEGER DEFAULT 5,
            fund INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных создана!")

def register_user(user_id, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, cash) VALUES (?, ?, 0, 0)", (user_id, username))
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

def update_cash(user_id, amount):
    conn = get_db()
    conn.execute("UPDATE users SET cash = cash + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def update_exp(user_id, exp_gain):
    conn = get_db()
    conn.execute("UPDATE users SET exp = exp + ? WHERE user_id = ?", (exp_gain, user_id))
    conn.commit()
    conn.close()

def update_level(user_id, new_level):
    conn = get_db()
    conn.execute("UPDATE users SET level = ? WHERE user_id = ?", (new_level, user_id))
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

def upgrade_business(user_id, business_id):
    conn = get_db()
    conn.execute("UPDATE businesses SET level = level + 1 WHERE user_id = ? AND business_id = ?", (user_id, business_id))
    conn.commit()
    conn.close()

BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 50000, "income": 5000},
    {"id": 2, "name": "Студия звука", "price": 120000, "income": 10000},
    {"id": 3, "name": "Музыкальный магаз", "price": 300000, "income": 22000},
    {"id": 4, "name": "Рэп-баттл", "price": 600000, "income": 40000},
    {"id": 5, "name": "Звукозапись", "price": 1200000, "income": 80000},
    {"id": 6, "name": "Лейбл", "price": 3000000, "income": 200000},
    {"id": 7, "name": "Продакшн", "price": 6000000, "income": 400000},
    {"id": 8, "name": "Ночной клуб", "price": 15000000, "income": 950000},
    {"id": 9, "name": "Радио", "price": 30000000, "income": 1900000},
    {"id": 10, "name": "Клипмейкер", "price": 60000000, "income": 3800000},
    {"id": 11, "name": "ТВ-канал", "price": 120000000, "income": 7500000},
    {"id": 12, "name": "Медиаимперия", "price": 300000000, "income": 18000000}
]

ADMIN_IDS = [692843306, 8824209793]

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎤 Квартирник", "👤 Профиль")
    markup.row("🏢 Бизнесы", "📊 Мои бизнесы")
    markup.row("🎵 Группировка", "🏷️ Лейбл")
    markup.row("💰 Донат", "📖 Помощь")
    return markup

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
        bot.send_message(message.chat.id, "Добро пожаловать в MusicWar! Выбери группировку:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "С возвращением! Используй кнопки внизу:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    bot.edit_message_text("Ты выбрал группировку: " + group_name, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Используй кнопки внизу:", reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in ["Лейбл", "🏷️ Лейбл"])
def band_menu(message):
    user_id = message.chat.id
    user = get_user(user_id)
    
    markup = telebot.types.InlineKeyboardMarkup()
    if user["band_id"] == 0:
        markup.add(telebot.types.InlineKeyboardButton("Создать лейбл", callback_data="band_create"))
        markup.add(telebot.types.InlineKeyboardButton("Найти лейбл", callback_data="band_find"))
        bot.send_message(message.chat.id, "Ты не состоишь в лейбле. Выбери действие:", reply_markup=markup)
    else:
        band = bands.get_band(user["band_id"])
        if not band:
            bot.send_message(message.chat.id, "Лейбл не найден!")
            return
        members = bands.get_band_members(user["band_id"])
        msg = "Лейбл: " + band["name"] + "\n"
        msg = msg + "Участников: " + str(len(members)) + "/" + str(band["slots"]) + "\n"
        msg = msg + "Фонд: " + str(band["fund"]) + " монет\n"
        msg = msg + "Твоя роль: " + user["band_role"] + "\n"
        
        markup.add(telebot.types.InlineKeyboardButton("Участники", callback_data="band_members"))
        if user["band_role"] == "leader":
            markup.add(telebot.types.InlineKeyboardButton("Управление", callback_data="band_manage"))
        markup.add(telebot.types.InlineKeyboardButton("Выйти из лейбла", callback_data="band_leave"))
        bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "band_create")
def band_create(call):
    bot.send_message(call.message.chat.id, "Введи название лейбла (от 3 до 20 символов, стоимость 75000 монет)")
    bot.register_next_step_handler(call.message, band_create_name)
    bot.answer_callback_query(call.id)

def band_create_name(message):
    user_id = message.chat.id
    name = message.text.strip()
    user = get_user(user_id)
    
    if len(name) < 3 or len(name) > 20:
        bot.send_message(message.chat.id, "Название должно быть от 3 до 20 символов!")
        return
    
    if bands.get_band_by_name(name):
        bot.send_message(message.chat.id, "Лейбл с таким названием уже существует!")
        return
    
    if user["money"] < 75000:
        bot.send_message(message.chat.id, "Не хватает монет! Нужно 75 000, у тебя " + str(user["money"]))
        return
    
    update_money(user_id, -75000)
    band_id = bands.create_band(user_id, name)
    if band_id:
        bot.send_message(message.chat.id, "Лейбл " + name + " создан! Ты стал лидером.")
    else:
        bot.send_message(message.chat.id, "Ошибка при создании лейбла!")

@bot.callback_query_handler(func=lambda call: call.data == "band_find")
def band_find(call):
    bot.send_message(call.message.chat.id, "Введи название лейбла для поиска")
    bot.register_next_step_handler(call.message, band_find_name)
    bot.answer_callback_query(call.id)

def band_find_name(message):
    name = message.text.strip()
    band = bands.get_band_by_name(name)
    if not band:
        bot.send_message(message.chat.id, "Лейбл не найден!")
        return
    
    members = bands.get_band_members(band["band_id"])
    msg = "Лейбл: " + band["name"] + "\n"
    msg = msg + "Участников: " + str(len(members)) + "/" + str(band["slots"]) + "\n"
    msg = msg + "Фонд: " + str(band["fund"]) + " монет\n"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Вступить", callback_data="band_join_" + str(band["band_id"])))
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("band_join_"))
def band_join(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    band_id = int(call.data.split("_")[2])
    band = bands.get_band(band_id)
    
    if user["band_id"] != 0:
        bot.answer_callback_query(call.id, "Ты уже в лейбле!")
        return
    
    if user["leave_band_time"] > time.time():
        bot.answer_callback_query(call.id, "Ты недавно вышел из лейбла! Подожди 24 часа.")
        return
    
    members = bands.get_band_members(band_id)
    if len(members) >= band["slots"]:
        bot.answer_callback_query(call.id, "Лейбл полон!")
        return
    
    bands.add_member(band_id, user_id)
    bot.answer_callback_query(call.id, "Ты вступил в лейбл!")
    bot.edit_message_text("Ты вступил в лейбл " + band["name"], chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "band_leave")
def band_leave(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if user["band_role"] == "leader":
        members = bands.get_band_members(user["band_id"])
        if len(members) > 1:
            bot.answer_callback_query(call.id, "Ты лидер! Передай лидерство или распусти лейбл!")
            return
    
    bands.remove_member(user["band_id"], user_id)
    conn = get_db()
    conn.execute("UPDATE users SET leave_band_time = ? WHERE user_id = ?", (int(time.time()) + 86400, user_id))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Ты вышел из лейбла!")
    bot.edit_message_text("Ты вышел из лейбла. Вступить в другой можно через 24 часа.", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "band_members")
def band_members(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    members = bands.get_band_members(user["band_id"])
    
    msg = "Участники лейбла:\n"
    for m in members:
        member = get_user(int(m))
        if member:
            role = member["band_role"]
            msg = msg + member["username"] + " (" + role + ")\n"
    bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "band_manage")
def band_manage(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Расширить лейбл (+5 слотов, 50к)", callback_data="band_expand"))
    bot.edit_message_text("Управление лейблом", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "band_expand")
def band_expand(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    band = bands.get_band(user["band_id"])
    
    if user["money"] < 50000:
        bot.answer_callback_query(call.id, "Нужно 50 000 монет!")
        return
    
    if band["slots"] >= 50:
        bot.answer_callback_query(call.id, "Лейбл уже максимального размера (50)!")
        return
    
    update_money(user_id, -50000)
    conn = get_db()
    conn.execute("UPDATE bands SET slots = slots + 5 WHERE band_id = ?", (band["band_id"],))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Лейбл расширен на 5 слотов!")
    bot.edit_message_text("Лейбл расширен на 5 слотов!", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    user = get_user(user_id)
    
    if not user:
        bot.send_message(message.chat.id, "Сначала напиши /start")
        return
    
    if text == "Квартирник" or text == "🎤 Квартирник":
        if not user["group_name"]:
            bot.send_message(message.chat.id, "Сначала выбери группировку через /start")
            return
        now = time.time()
        if not hasattr(handle_text, "last_attack"):
            handle_text.last_attack = {}
        if user_id in handle_text.last_attack and now - handle_text.last_attack[user_id] < 90:
            bot.send_message(message.chat.id, "Подожди 1.5 минуты!")
            return
        handle_text.last_attack[user_id] = now
        
        boost = 2 if user["boost_end"] > time.time() else 1
        income = random.randint(1000, 5000) * boost
        update_money(user_id, income)
        exp_gain = random.randint(1, 3)
        update_exp(user_id, exp_gain)
        
        user = get_user(user_id)
        while user["exp"] >= user["level"] * 100:
            update_exp(user_id, -(user["level"] * 100))
            update_level(user_id, user["level"] + 1)
            user = get_user(user_id)
        
        msg = "Ты заработал " + str(income) + " монет!"
        if boost == 2:
            msg = msg + " (x2 буст!)"
        msg = msg + "\nОпыт: +" + str(exp_gain) + "\nУровень: " + str(user["level"])
        bot.send_message(message.chat.id, msg)
    
    elif text == "Профиль" or text == "👤 Профиль":
        group = user["group_name"] or "не выбрана"
        boost_status = "Активен" if user["boost_end"] > time.time() else "Не активен"
        vip_status = "Активен" if user["vip_end"] > time.time() else "Не активен"
        band_name = "Нет"
        if user["band_id"] != 0:
            band = bands.get_band(user["band_id"])
            if band:
                band_name = band["name"]
        
        msg = "Твой профиль\n"
        msg = msg + "Группировка: " + group + "\n"
        msg = msg + "Лейбл: " + band_name + "\n"
        msg = msg + "Монет: " + str(user["money"]) + "\n"
        msg = msg + "Кэш: " + str(user["cash"]) + "\n"
        msg = msg + "Уровень: " + str(user["level"]) + "\n"
        msg = msg + "Опыт: " + str(user["exp"]) + "/" + str(user["level"] * 100) + "\n"
        msg = msg + "Буст x2: " + boost_status + "\n"
        msg = msg + "VIP: " + vip_status
        bot.send_message(message.chat.id, msg)
    
    elif text == "Бизнесы" or text == "🏢 Бизнесы" or text == "Бизнес":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Купить бизнес", callback_data="buy_biz"))
        markup.add(telebot.types.InlineKeyboardButton("Улучшить бизнес", callback_data="upgrade_biz"))
        bot.send_message(message.chat.id, "Управление бизнесами", reply_markup=markup)
    
    elif text == "Мои бизнесы" or text == "📊 Мои бизнесы":
        businesses = get_user_businesses(user_id)
        if not businesses:
            bot.send_message(message.chat.id, "У тебя нет бизнесов")
            return
        msg = "Твои бизнесы\n"
        for b in businesses:
            biz = BUSINESSES[b["business_id"] - 1]
            income = biz["income"] * (1 + b["level"] * 0.1)
            msg = msg + biz["name"] + " (ур." + str(b["level"]) + ") — " + str(int(income)) + " монет/час\n"
        bot.send_message(message.chat.id, msg)
    
    elif text == "Группировка" or text == "🎵 Группировка":
        if user["group_name"]:
            bot.send_message(message.chat.id, "Твоя группировка: " + user["group_name"])
            return
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("Реперы", callback_data="group_Реперы"),
            telebot.types.InlineKeyboardButton("Рокеры", callback_data="group_Рокеры")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("Меломаны", callback_data="group_Меломаны"),
            telebot.types.InlineKeyboardButton("Клубмены", callback_data="group_Клубмены")
        )
        bot.send_message(message.chat.id, "Выбери группировку:", reply_markup=markup)
    
    elif text == "Донат" or text == "💰 Донат":
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("10 Кэш за 5 ★", callback_data="buy_10"),
            telebot.types.InlineKeyboardButton("50 Кэш за 20 ★", callback_data="buy_50"),
            telebot.types.InlineKeyboardButton("100 Кэш за 35 ★", callback_data="buy_100"),
            telebot.types.InlineKeyboardButton("500 Кэш за 150 ★", callback_data="buy_500"),
            telebot.types.InlineKeyboardButton("Буст x2 (10 Кэш)", callback_data="buy_boost"),
            telebot.types.InlineKeyboardButton("VIP (20 Кэш)", callback_data="buy_vip"),
            telebot.types.InlineKeyboardButton("Кейс (10 Кэш)", callback_data="donate_case")
        )
        bot.send_message(message.chat.id, "Донат", reply_markup=markup)
    
    elif text == "Помощь" or text == "📖 Помощь":
        msg = "Команды MusicWar:\n"
        msg = msg + "Квартирник - заработать монеты\n"
        msg = msg + "Профиль - твоя статистика\n"
        msg = msg + "Бизнесы - управление бизнесами\n"
        msg = msg + "Мои бизнесы - твои бизнесы\n"
        msg = msg + "Группировка - выбрать группировку\n"
        msg = msg + "Лейбл - управление лейблом\n"
        msg = msg + "Донат - покупка Кэш"
        bot.send_message(message.chat.id, msg)
    
    else:
        bot.send_message(message.chat.id, "Неизвестная команда. Используй кнопки внизу.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if call.data == "buy_boost":
        if user["cash"] < 10:
            bot.answer_callback_query(call.id, "Не хватает Кэш")
            return
        update_cash(user_id, -10)
        conn = get_db()
        conn.execute("UPDATE users SET boost_end = ? WHERE user_id = ?", (int(time.time()) + 3600, user_id))
        conn.commit()
        conn.close()
        bot.edit_message_text("Буст x2 активирован на 1 час!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
