import telebot
import random
import sqlite3
import os
import time
import bands

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
            band_id INTEGER DEFAULT 0,
            band_role TEXT DEFAULT 'member'
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
            members TEXT DEFAULT '',
            slots INTEGER DEFAULT 5,
            fund INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных создана!")

def register_user(user_id, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, xp, level, band_id, band_role) VALUES (?, ?, 1000, 0, 1, 0, 'member')", (user_id, username))
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
    if level <= 5: return "🎧 Начинающий"
    elif level <= 10: return "🎤 Андеграунд"
    elif level <= 15: return "🎵 Хип-хопер"
    elif level <= 20: return "🏆 Прорыв"
    elif level <= 25: return "📀 Известный"
    elif level <= 30: return "💿 Популярный"
    elif level <= 35: return "🎶 Топ-чарт"
    elif level <= 40: return "👑 Платиновый"
    elif level <= 45: return "⭐ Бриллиантовый"
    else: return "💎 Music Legend"

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
            telebot.types.InlineKeyboardButton("🎤 Реперы", callback_data="group_Реперы"),
            telebot.types.InlineKeyboardButton("🎸 Рокеры", callback_data="group_Рокеры")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("🎵 Меломаны", callback_data="group_Меломаны"),
            telebot.types.InlineKeyboardButton("🎧 Клубмены", callback_data="group_Клубмены")
        )
        bot.send_message(message.chat.id,
            "⚔️═══════════════⚔️\n"
            "   🎵 MUSICWAR 🎵\n"
            "⚔️═══════════════⚔️\n\n"
            "🎵 Добро пожаловать!\n"
            "Выбери свою группировку:",
            reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
            f"⚔️═══════════════⚔️\n"
            f"   🎵 MUSICWAR 🎵\n"
            f"⚔️═══════════════⚔️\n\n"
            f"🎵 С возвращением!\n"
            f"🎵 Группировка: {user['group_name']}",
            reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(
        f"✅ Ты выбрал группировку: {group_name}!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.send_message(call.message.chat.id,
        "🎵 Используй кнопки внизу:",
        reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in ["🎤 Квартирник", "Квартирник"])
def attack(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return
    if not user["group_name"]:
        bot.send_message(message.chat.id, "❌ Выбери группировку через /start")
        return

    income = random.randint(1000, 5000)
    xp_gain = random.randint(10, 25)
    update_money(user_id, income)
    leveled_up, new_level = add_xp(user_id, xp_gain)
    user = get_user(user_id)

    msg = f"💰 Ты заработал {income} монет!\n"
    msg += f"✨ +{xp_gain} опыта\n"
    msg += f"💵 Всего монет: {user['money']}\n"

    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\n🎉 УРОВЕНЬ ПОВЫШЕН!\n"
        msg += f"⭐ Ты достиг {new_level} уровня!\n"
        msg += f"🏆 Новое звание: {rank}!"
        if new_level % 10 == 0:
            msg += f"\n💰 Бонус к доходу: +{new_level // 2}%!"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in ["👤 Профиль", "Профиль"])
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return

    group = user["group_name"] or "не выбрана"
    band_name = "Нет"
    if user["band_id"] != 0:
        band = bands.get_band(user["band_id"])
        if band:
            band_name = band["name"]

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

    msg = "⚔️═══════════════⚔️\n"
    msg += "   🎵 MUSICWAR 🎵\n"
    msg += "⚔️═══════════════⚔️\n\n"
    msg += f"👤 Игрок: {user['username']}\n"
    msg += f"🎵 Группировка: {group}\n"
    msg += f"🏷️ Лейбл: {band_name}\n\n"
    msg += f"⭐ Уровень: {user['level']} ({rank})\n"
    msg += f"📈 Опыт: {user['xp']}/{xp_for_next} XP\n"
    msg += f"💰 Монет: {user['money']:,}\n"
    msg += f"📈 Доход: {total_income:,} монет/час\n"
    if level_bonus > 0:
        msg += f"🎯 Бонус уровня: +{level_bonus}%"
    msg += "\n⚔️═══════════════⚔️"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in ["🏢 Бизнесы", "Бизнесы"])
def show_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return

    response = "⚔️═══════════════⚔️\n"
    response += "   🏢 БИЗНЕСЫ\n"
    response += "⚔️═══════════════⚔️\n\n"
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "✅" if owned else "❌"
        response += f"{b['id']}. {b['name']}\n"
        response += f"   💰 {b['price']:,} | 📈 {b['income']:,}/ч {status}\n\n"
    response += "📌 Напиши: *Купить бизнес N*"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text.lower().startswith("купить бизнес"))
def buy_business_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return

    try:
        business_id = int(message.text.split()[-1])
    except:
        bot.send_message(message.chat.id, "❌ Формат: Купить бизнес N")
        return

    if business_id < 1 or business_id > len(BUSINESSES):
        bot.send_message(message.chat.id, "❌ Нет такого бизнеса!")
        return

    if get_business_level(user_id, business_id) > 0:
        bot.send_message(message.chat.id, "❌ У тебя уже есть этот бизнес!")
        return

    b = BUSINESSES[business_id - 1]
    if user["money"] < b["price"]:
        bot.send_message(message.chat.id, f"❌ Нужно {b['price']:,} монет!")
        return

    update_money(user_id, -b["price"])
    buy_business(user_id, business_id)
    add_xp(user_id, 50)
    bot.send_message(message.chat.id, f"✅ Ты купил {b['name']}! +50 XP")

@bot.message_handler(func=lambda message: message.text in ["📊 Мои бизнесы", "Мои бизнесы"])
def my_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return

    businesses = get_user_businesses(user_id)
    if not businesses:
        bot.send_message(message.chat.id, "📊 У тебя нет бизнесов!")
        return

    level_bonus = (user["level"] // 10) * 5

    response = "⚔️═══════════════⚔️\n"
    response += "   📊 МОИ БИЗНЕСЫ\n"
    response += "⚔️═══════════════⚔️\n\n"
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        income = int(income * (1 + level_bonus / 100))
        total_income += income
        response += f"• {biz['name']} (ур.{b['level']})\n"
        response += f"  📈 {income:,} монет/час\n\n"
    response += "⚔️═══════════════⚔️\n"
    response += f"💰 Общий доход: {total_income:,} монет/час"
    if level_bonus > 0:
        response += f"\n🎯 Бонус уровня: +{level_bonus}%"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text in ["🎵 Группировка", "Группировка"])
def group_menu(message):
    start(message)

@bot.message_handler(func=lambda message: message.text in ["🏷️ Лейбл", "Лейбл"])
def band_menu(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ Напиши /start")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    if user["band_id"] == 0:
        markup.add(telebot.types.InlineKeyboardButton("📝 Создать лейбл", callback_data="band_create"))
        markup.add(telebot.types.InlineKeyboardButton("🔍 Найти лейбл", callback_data="band_find"))
        bot.send_message(message.chat.id,
            "⚔️═══════════════⚔️\n"
            "   🏷️ ЛЕЙБЛ\n"
            "⚔️═══════════════⚔️\n\n"
            "Ты не состоишь в лейбле.\n"
            "Выбери действие:",
            reply_markup=markup)
    else:
        band = bands.get_band(user["band_id"])
        if not band:
            bot.send_message(message.chat.id, "❌ Лейбл не найден!")
            return
        members = bands.get_band_members(user["band_id"])
        msg = "⚔️═══════════════⚔️\n"
        msg += f"   🏷️ {band['name']}\n"
        msg += "⚔️═══════════════⚔️\n\n"
        msg += f"👥 Участников: {len(members)}/{band['slots']}\n"
        msg += f"💰 Фонд: {band['fund']:,} монет\n"
        msg += f"🎯 Роль: {user['band_role']}\n"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📊 Участники", callback_data="band_members"))
        if user["band_role"] == "leader":
            markup.add(telebot.types.InlineKeyboardButton("⚙️ Управление", callback_data="band_manage"))
        markup.add(telebot.types.InlineKeyboardButton("🚪 Выйти из лейбла", callback_data="band_leave_confirm"))
        bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "band_create")
def band_create(call):
    bot.send_message(call.message.chat.id,
        "⚔️═══════════════⚔️\n"
        "   📝 СОЗДАНИЕ ЛЕЙБЛА\n"
        "⚔️═══════════════⚔️\n\n"
        "Введи название лейбла (от 3 до 20 символов)\n"
        "💰 Стоимость: 75,000 монет")
    bot.register_next_step_handler(call.message, band_create_name)
    bot.answer_callback_query(call.id)

def band_create_name(message):
    user_id = message.chat.id
    name = message.text.strip()
    user = get_user(user_id)

    if len(name) < 3 or len(name) > 20:
        bot.send_message(message.chat.id, "❌ Название должно быть от 3 до 20 символов!")
        return

    if bands.get_band_by_name(name):
        bot.send_message(message.chat.id, "❌ Лейбл с таким названием уже существует!")
        return

    if user["money"] < 75000:
        bot.send_message(message.chat.id, f"❌ Нужно 75,000 монет! У тебя {user['money']:,}")
        return

    update_money(user_id, -75000)
    band_id = bands.create_band(user_id, name)
    if band_id:
        add_xp(user_id, 100)
        bot.send_message(message.chat.id, f"✅ Лейбл '{name}' создан! +100 XP")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при создании лейбла!")

@bot.callback_query_handler(func=lambda call: call.data == "band_find")
def band_find(call):
    bot.send_message(call.message.chat.id,
        "⚔️═══════════════⚔️\n"
        "   🔍 ПОИСК ЛЕЙБЛА\n"
        "⚔️═══════════════⚔️\n\n"
        "Введи название лейбла для поиска:")
    bot.register_next_step_handler(call.message, band_find_name)
    bot.answer_callback_query(call.id)

def band_find_name(message):
    name = message.text.strip()
    band = bands.get_band_by_name(name)
    if not band:
        bot.send_message(message.chat.id, "❌ Лейбл не найден!")
        return

    members = bands.get_band_members(band["band_id"])
    msg = "⚔️═══════════════⚔️\n"
    msg += f"   🏷️ {band['name']}\n"
    msg += "⚔️═══════════════⚔️\n\n"
    msg += f"👥 Участников: {len(members)}/{band['slots']}\n"
    msg += f"💰 Фонд: {band['fund']:,} монет\n"

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📝 Вступить", callback_data=f"band_join_{band['band_id']}"))
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("band_join_"))
def band_join(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    band_id = int(call.data.split("_")[2])
    band = bands.get_band(band_id)

    if user["band_id"] != 0:
        bot.answer_callback_query(call.id, "❌ Ты уже в лейбле!")
        return

    if bands.get_band_members_count(band_id) >= band["slots"]:
        bot.answer_callback_query(call.id, "❌ Лейбл полон!")
        return

    bands.add_member(band_id, user_id)
    add_xp(user_id, 25)
    bot.answer_callback_query(call.id, "✅ Ты вступил в лейбл! +25 XP")
    bot.edit_message_text(f"✅ Ты вступил в лейбл {band['name']}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "band_members")
def band_members(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user or user["band_id"] == 0:
        bot.answer_callback_query(call.id, "❌ Ты не в лейбле!")
        return

    members = bands.get_band_members(user["band_id"])
    band = bands.get_band(user["band_id"])

    msg = "⚔️═══════════════⚔️\n"
    msg += f"   👥 {band['name']}\n"
    msg += "⚔️═══════════════⚔️\n\n"
    for m in members:
        member = get_user(int(m))
        if member:
            role = member["band_role"]
            msg += f"• {member['username']} ({role})\n"
    bot.edit_message_text(msg,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "band_leave_confirm")
def band_leave_confirm(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ ДА, ВЫЙТИ", callback_data="band_leave_yes"),
        telebot.types.InlineKeyboardButton("❌ НЕТ, ОСТАТЬСЯ", callback_data="band_leave_no")
    )
    bot.edit_message_text(
        "⚔️═══════════════⚔️\n"
        "   🚪 ВЫХОД ИЗ ЛЕЙБЛА\n"
        "⚔️═══════════════⚔️\n\n"
        "⚠️ Ты уверен, что хочешь покинуть лейбл?\n\n"
        "📌 После выхода:\n"
        "• Ты потеряешь доступ к казне\n"
        "• Вступить обратно можно через 24 часа\n\n"
        "❓ Подтверди действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "band_leave_yes")
def band_leave_yes(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user["band_role"] == "leader":
        if bands.get_band_members_count(user["band_id"]) > 1:
            bot.answer_callback_query(call.id, "❌ Передай лидерство или распусти лейбл!")
            return

    bands.remove_member(user["band_id"], user_id)
    bot.answer_callback_query(call.id, "✅ Ты вышел из лейбла!")
    bot.edit_message_text("✅ Ты вышел из лейбла.\nВступить в другой можно через 24 часа.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "band_leave_no")
def band_leave_no(call):
    bot.answer_callback_query(call.id, "✅ Отлично, остаёшься!")
    bot.dele
