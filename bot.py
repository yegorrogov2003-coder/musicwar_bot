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
            band_id INTEGER DEFAULT 0
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
            members TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных создана!")

def register_user(user_id, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, xp, level, band_id) VALUES (?, ?, 1000, 0, 1, 0)", (user_id, username))
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
    if level <= 5: return "Начинающий"
    elif level <= 10: return "Андеграунд"
    elif level <= 15: return "Хип-хопер"
    elif level <= 20: return "Прорыв"
    elif level <= 25: return "Известный"
    elif level <= 30: return "Популярный"
    elif level <= 35: return "Топ-чарт"
    elif level <= 40: return "Платиновый"
    elif level <= 45: return "Бриллиантовый"
    else: return "Music Legend"

# ===== ФУНКЦИИ ЛЕЙБЛОВ =====

def create_band(leader_id, name):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO bands (name, leader_id, members) VALUES (?, ?, ?)",
            (name, leader_id, str(leader_id))
        )
        band_id = cursor.lastrowid
        conn.execute(
            "UPDATE users SET band_id = ? WHERE user_id = ?",
            (band_id, leader_id)
        )
        conn.commit()
        return band_id
    except Exception as e:
        print(f"Ошибка create_band: {e}")
        return None
    finally:
        conn.close()

def get_band(band_id):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE band_id = ?", (band_id,)).fetchone()
    conn.close()
    return band

def get_band_by_name(name):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE name = ?", (name,)).fetchone()
    conn.close()
    return band

def get_band_members(band_id):
    conn = get_db()
    band = conn.execute("SELECT members FROM bands WHERE band_id = ?", (band_id,)).fetchone()
    conn.close()
    if band and band["members"]:
        return [int(m) for m in band["members"].split(",") if m]
    return []

def get_band_members_count(band_id):
    return len(get_band_members(band_id))

def add_member(band_id, user_id):
    conn = get_db()
    members = get_band_members(band_id)
    if user_id not in members:
        members.append(user_id)
        members_str = ",".join(str(m) for m in members)
        conn.execute(
            "UPDATE bands SET members = ? WHERE band_id = ?",
            (members_str, band_id)
        )
        conn.execute(
            "UPDATE users SET band_id = ? WHERE user_id = ?",
            (band_id, user_id)
        )
        conn.commit()
    conn.close()

def remove_member(band_id, user_id):
    conn = get_db()
    members = get_band_members(band_id)
    if user_id in members:
        members.remove(user_id)
        members_str = ",".join(str(m) for m in members) if members else ""
        conn.execute(
            "UPDATE bands SET members = ? WHERE band_id = ?",
            (members_str, band_id)
        )
        conn.execute(
            "UPDATE users SET band_id = 0 WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        if not members:
            conn.execute("DELETE FROM bands WHERE band_id = ?", (band_id,))
            conn.commit()
    conn.close()
    return True

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
    markup.row("Квартирник", "Профиль")
    markup.row("Бизнесы", "Мои бизнесы")
    markup.row("Группировка", "Донат")
    markup.row("Помощь", "О боте")
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
        bot.send_message(message.chat.id, "Добро пожаловать! Выбери группировку:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"С возвращением! Группировка: {user['group_name']}", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group_callback(call):
    group_name = call.data.split("_")[1]
    set_group(call.from_user.id, group_name)
    add_xp(call.from_user.id, 15)
    bot.edit_message_text(f"Ты выбрал группировку: {group_name}!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Используй кнопки внизу:", reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text in ["Квартирник"])
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

    msg = f"Ты заработал {income} монет!\n+{xp_gain} опыта\nВсего монет: {user['money']}"

    if leveled_up:
        rank = get_rank(new_level)
        msg += f"\nУРОВЕНЬ ПОВЫШЕН! Ты достиг {new_level} уровня! Новое звание: {rank}!"
        if new_level % 10 == 0:
            msg += f"\nБонус к доходу: +{new_level // 2}%!"

    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in ["Профиль"])
def profile(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    group = user["group_name"] or "не выбрана"
    band_name = "Нет"
    if user["band_id"] != 0:
        band = get_band(user["band_id"])
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

    msg = f"Профиль:\nИгрок: {user['username']}\nГруппировка: {group}\nЛейбл: {band_name}\nУровень: {user['level']} ({rank})\nОпыт: {user['xp']}/{xp_for_next} XP\nМонет: {user['money']}\nДоход: {total_income} монет/час"
    if level_bonus > 0:
        msg += f"\nБонус уровня: +{level_bonus}%"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda message: message.text in ["Бизнесы"])
def show_businesses(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    response = "Магазин бизнесов:\n"
    for b in BUSINESSES:
        owned = get_business_level(user_id, b["id"]) > 0
        status = "Владеешь" if owned else "Нет"
        response += f"{b['id']}. {b['name']} — {b['price']} монет, доход {b['income']}/ч ({status})\n"
    response += "Напиши: Купить бизнес N"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text.lower().startswith("купить бизнес"))
def buy_business_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    try:
        business_id = int(message.text.split()[-1])
    except:
        bot.send_message(message.chat.id, "Формат: Купить бизнес N")
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
    bot.send_message(message.chat.id, f"Купил {b['name']}! +50 XP")

@bot.message_handler(func=lambda message: message.text in ["Мои бизнесы"])
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

    response = "Мои бизнесы:\n"
    total_income = 0
    for b in businesses:
        biz = BUSINESSES[b["business_id"] - 1]
        income = biz["income"] * (1 + b["level"] * 0.1)
        income = int(income * (1 + level_bonus / 100))
        total_income += income
        response += f"{biz['name']} (ур.{b['level']}) — {income} монет/час\n"
    response += f"Общий доход: {total_income} монет/час"
    if level_bonus > 0:
        response += f"\nБонус уровня: +{level_bonus}%"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text in ["Группировка"])
def group_menu(message):
    start(message)

@bot.message_handler(func=lambda message: message.text in ["Донат"])
def donate(message):
    bot.send_message(message.chat.id, "Донат:\nКэш — 100 монет (50₽)\nКэш+ — 500 монет (200₽)\nVIP — 1000 монет (400₽)\nДля покупки напиши @SupportBot")

@bot.message_handler(func=lambda message: message.text in ["Помощь"])
def help_command(message):
    bot.send_message(message.chat.id, "Помощь:\nКвартирник — заработать монеты и опыт\nПрофиль — твоя статистика\nБизнесы — магазин бизнесов\nМои бизнесы — твои бизнесы\nГруппировка — выбрать группировку\nДонат — покупка Кэш")

@bot.message_handler(func=lambda message: message.text in ["О боте"])
def about(message):
    bot.send_message(message.chat.id, "MusicWar Bot v2.0\n50 уровней\n12 бизнесов\n4 группировки")

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Неизвестная команда. Используй кнопки внизу или напиши /help.")

# ===== ОБРАБОТЧИКИ КОМАНД ЛЕЙБЛОВ =====

@bot.message_handler(commands=['band'])
def band_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["band_id"] == 0:
        bot.send_message(message.chat.id, "Ты не в лейбле!\nКоманды:\n/band_create [название] — создать лейбл (75,000 монет)\n/band_join [название] — вступить в лейбл")
    else:
        band = get_band(user["band_id"])
        if band:
            members = get_band_members(user["band_id"])
            msg = f"Лейбл: {band['name']}\nУчастников: {len(members)}\nКоманды:\n/band_leave — выйти\n/band_members — список участников"
            bot.send_message(message.chat.id, msg)
        else:
            bot.send_message(message.chat.id, "Лейбл не найден!")

@bot.message_handler(commands=['band_create'])
def band_create_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["band_id"] != 0:
        bot.send_message(message.chat.id, "Ты уже в лейбле!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Формат: /band_create [название]")
        return

    name = args[1].strip()
    if len(name) < 3 or len(name) > 20:
        bot.send_message(message.chat.id, "Название должно быть от 3 до 20 символов!")
        return

    if get_band_by_name(name):
        bot.send_message(message.chat.id, "Лейбл с таким названием уже существует!")
        return

    if user["money"] < 75000:
        bot.send_message(message.chat.id, f"Нужно 75,000 монет! У тебя {user['money']}")
        return

    update_money(user_id, -75000)
    band_id = create_band(user_id, name)
    if band_id:
        add_xp(user_id, 100)
        bot.send_message(message.chat.id, f"Лейбл {name} создан! +100 XP")
    else:
        bot.send_message(message.chat.id, "Ошибка при создании лейбла!")

@bot.message_handler(commands=['band_join'])
def band_join_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["band_id"] != 0:
        bot.send_message(message.chat.id, "Ты уже в лейбле!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Формат: /band_join [название]")
        return

    name = args[1].strip()
    band = get_band_by_name(name)
    if not band:
        bot.send_message(message.chat.id, "Лейбл не найден!")
        return

    add_member(band["band_id"], user_id)
    add_xp(user_id, 25)
    bot.send_message(message.chat.id, f"Ты вступил в лейбл {name}! +25 XP")

@bot.message_handler(commands=['band_leave'])
def band_leave_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["band_id"] == 0:
        bot.send_message(message.chat.id, "Ты не в лейбле!")
        return

    band = get_band(user["band_id"])
    if not band:
        bot.send_message(message.chat.id, "Лейбл не найден!")
        return

    remove_member(user["band_id"], user_id)
    bot.send_message(message.chat.id, f"Ты вышел из лейбла {band['name']}!")

@bot.message_handler(commands=['band_members'])
def band_members_command(message):
    user_id = message.chat.id
    user = get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "Напиши /start")
        return

    if user["band_id"] == 0:
        bot.send_message(message.chat.id, "Ты не в лейбле!")
        return

    band = get_band(user["band_id"])
    if not band:
        bot.send_message(message.chat.id, "Лейбл не найден!")
        return

    members = get_band_members(user["band_id"])
    if not members:
        bot.send_message(message.chat.id, "В лейбле пока нет участников.")
        return

    msg = f"Участники лейбла {band['name']}:\n"
    for m in members:
        member = get_user(int(m))
        if member:
            msg += f"- {member['username']}\n"
    bot.send_message(message.chat.id, msg)

if __name__ == "__main__":
    init_db()
    print("БОТ ЗАПУЩЕН!")
    print("MusicWar Bot готов к работе!")
    print("Загружено 12 бизнесов")
    print("Система уровней: 50 уровней")
    print("Команды лейблов загружены!")

    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            print("Перезапуск через 5 секунд...")
            time.sleep(5)
