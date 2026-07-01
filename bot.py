import telebot
import time
import random
import sqlite3
import os

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
            vip_end INTEGER DEFAULT 0
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
    markup.row("🎵 Группировка", "💰 Донат")
    markup.row("📖 Помощь")
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
        
        msg = "Твой профиль\n"
        msg = msg + "Группировка: " + group + "\n"
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
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "buy_vip":
        if user["cash"] < 20:
            bot.answer_callback_query(call.id, "Не хватает Кэш")
            return
        update_cash(user_id, -20)
        conn = get_db()
        conn.execute("UPDATE users SET vip_end = ? WHERE user_id = ?", (int(time.time()) + 86400, user_id))
        conn.commit()
        conn.close()
        bot.edit_message_text("VIP активирован на 1 день!", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "donate_case":
        if user["cash"] < 10:
            bot.answer_callback_query(call.id, "Не хватает Кэш")
            return
        update_cash(user_id, -10)
        prizes = [
            (random.randint(50000, 200000), "монет"),
            (random.randint(500000, 3000000), "монет"),
            ("Буст x2", "буст"),
            ("VIP (1 день)", "VIP")
        ]
        prize = random.choice(prizes)
        if prize[1] == "монет":
            update_money(user_id, prize[0])
        elif prize[1] == "буст":
            conn = get_db()
            conn.execute("UPDATE users SET boost_end = ? WHERE user_id = ?", (int(time.time()) + 3600, user_id))
            conn.commit()
            conn.close()
        elif prize[1] == "VIP":
            conn = get_db()
            conn.execute("UPDATE users SET vip_end = ? WHERE user_id = ?", (int(time.time()) + 86400, user_id))
            conn.commit()
            conn.close()
        bot.edit_message_text("Ты получил: " + str(prize[0]) + " " + prize[1], chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("buy_") and call.data not in ["buy_boost", "buy_vip", "donate_case", "buy_biz"]:
        amount = int(call.data.split("_")[1])
        prices = {10: 5, 50: 20, 100: 35, 500: 150}
        if amount in prices:
            price = prices[amount]
            bot.send_invoice(
                call.message.chat.id,
                title="Кэш x" + str(amount),
                description="Покупка " + str(amount) + " Кэш за " + str(price) + " ★",
                invoice_payload="cash_" + str(amount),
                provider_token="",
                currency="XTR",
                prices=[telebot.types.LabeledPrice(label=str(amount) + " Кэш", amount=price * 100)]
            )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "buy_biz":
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for b in BUSINESSES:
            owned = get_business_level(user_id, b["id"]) > 0
            status = "✅" if owned else "❌"
            markup.add(telebot.types.InlineKeyboardButton(str(b["id"]) + ". " + b["name"] + " " + status, callback_data="b_" + str(b["id"])))
        bot.edit_message_text("Магазин бизнесов", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("b_"):
        business_id = int(call.data.split("_")[1])
        if get_business_level(user_id, business_id) > 0:
            bot.answer_callback_query(call.id, "У тебя уже есть этот бизнес")
            return
        b = BUSINESSES[business_id - 1]
        if user["money"] < b["price"]:
            bot.answer_callback_query(call.id, "Нужно " + str(b["price"]) + " монет")
            return
        update_money(user_id, -b["price"])
        buy_business(user_id, business_id)
        bot.edit_message_text("Ты купил " + b["name"] + "!", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "upgrade_biz":
        businesses = get_user_businesses(user_id)
        if not businesses:
            bot.edit_message_text("У тебя нет бизнесов для улучшения", chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.answer_callback_query(call.id)
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for b in businesses:
            biz = BUSINESSES[b["business_id"] - 1]
            markup.add(telebot.types.InlineKeyboardButton(biz["name"] + " (ур." + str(b["level"]) + ")", callback_data="up_" + str(b["business_id"])))
        bot.edit_message_text("Улучшение бизнесов", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("up_"):
        business_id = int(call.data.split("_")[1])
        b = BUSINESSES[business_id - 1]
        level = get_business_level(user_id, business_id)
        if level >= 10:
            bot.answer_callback_query(call.id, "Бизнес уже максимального уровня!")
            return
        cost = int(b["price"] * 0.1)
        if user["money"] < cost:
            bot.answer_callback_query(call.id, "Нужно " + str(cost) + " монет")
            return
        update_money(user_id, -cost)
        upgrade_business(user_id, business_id)
        new_level = get_business_level(user_id, business_id)
        bot.edit_message_text(b["name"] + " улучшен до " + str(new_level) + " уровня!", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return

@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    user_id = message.chat.id
    payload = message.successful_payment.invoice_payload
    if payload.startswith("cash_"):
        amount = int(payload.split("_")[1])
        update_cash(user_id, amount)
        bot.send_message(user_id, "Ты получил " + str(amount) + " Кэш!")

init_db()
print("Бот запущен!")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка: " + str(e))
        time.sleep(5)
