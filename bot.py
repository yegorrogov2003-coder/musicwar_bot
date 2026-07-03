import os
import sqlite3
import telebot
from dotenv import load_dotenv
from telebot import types

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Токен не найден! Проверьте файл .env и переменную TELEGRAM_BOT_TOKEN.")

bot = telebot.TeleBot(TOKEN)
DB_PATH = "musicwar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    try:
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
        print("База данных готова.")
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        conn.close()

def register_user(user_id, username):
    conn = get_db()
    try:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, money, xp, level) VALUES (?, ?, 1000, 0, 1)",
                     (user_id, username))
        conn.commit()
    except Exception as e:
        print(f"Ошибка регистрации пользователя: {e}")
    finally:
        conn.close()

def get_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def update_money(user_id, amount):
    conn = get_db()
    try:
        # Исправлено: добавлен оператор +
        conn.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка обновления денег: {e}")
    finally:
        conn.close()

def add_xp(user_id, amount):
    conn = get_db()
    try:
        user = conn.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if user:
            # Исправлено: добавлен оператор +
            new_xp = user["xp"] + amount
            current_level = user["level"]
            leveled_up = False

            while new_xp >= current_level * 100:
                new_xp -= current_level * 100
                current_level += 1
                leveled_up = True

            conn.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
                         (new_xp, current_level, user_id))
            conn.commit()
            return leveled_up, current_level
    except Exception as e:
        print(f"Ошибка добавления опыта: {e}")
    finally:
        conn.close()
    return False, 1

def buy_business(user_id, business_id):
    # Сначала проверяем, есть ли у пользователя достаточно денег (логика цены должна быть снаружи)
    conn = get_db()
    try:
        # Используем INSERT OR IGNORE, чтобы не перезаписывать лишние поля
        conn.execute("INSERT OR IGNORE INTO businesses (user_id, business_id, owned, level) VALUES (?, ?, 1, 0)",
                     (user_id, business_id))
        conn.execute("UPDATE businesses SET owned = 1 WHERE user_id = ? AND business_id = ?",
                     (user_id, business_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка покупки бизнеса: {e}")
        return False
    finally:
        conn.close()

def get_user_businesses(user_id):
    conn = get_db()
    businesses = conn.execute("SELECT * FROM businesses WHERE user_id = ? AND owned = 1", (user_id,)).fetchall()
    conn.close()
    return businesses

def get_business_by_id(business_id):
    for b in BUSINESSES:
        if b["id"] == business_id:
            return b
    return None

def get_rank(level):
    if level <= 5:
        return "Новичок"
    elif level <= 10:
        return "Андеграунд"
    elif level <= 15:
        return "Хип-хопер"
    elif level <= 20:
        return "Прорыв"
    elif level <= 25:
        return "Известный"
    elif level <= 30:
        return "Популярный"
    elif level <= 35:
        return "Топ-чарт"
    elif level <= 40:
        return "Платиновый"
    elif level <= 45:
        return "Бриллиантовый"
    else:
        return "Music Legend"

# Исправленный список бизнесов (все поля на месте)
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 50000, "income": 5000},
    {"id": 2, "name": "Студия звука", "price": 120000, "income": 10000},
    {"id": 3, "name": "Музыкальный магазин", "price": 300000, "income": 22000},
    {"id": 4, "name": "Рэп-баттл", "price": 600000, "income": 40000},
    {"id": 5, "name": "Студия записи", "price": 1200000, "income": 80000},
    {"id": 6, "name": "Звукозаписывающая студия", "price": 3000000, "income": 150000}
]

# --- Обработчики команд ---

@bot.message_handler(commands=["start"])
def send_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    register_user(user_id, username)
    bot.reply_to(message, f"Привет, {username}! Добро пожаловать в Music War. Используй /profile, чтобы посмотреть статус, и /businesses, чтобы купить бизнес.")

@bot.message_handler(commands=["profile"])
def send_profile(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        bot.reply_to(message, "Что-то пошло не так. Попробуй нажать /start.")
        return

    rank = get_rank(user["level"])
    text = (
        f"👤 Профиль: {user['username']}\n"
        f"💰 Деньги: {user['money']:,}\n"
        f"⭐ Уровень: {user['level']} ({rank})\n"
        f"⚡ Опыт: {user['xp']}/{user['level'] * 100}\n"
        f"🏢 Группа: {user['group_name'] or 'Не указана'}"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=["businesses"])
def send_businesses_panel(message):
    """Удобная панелька с бизнесами: кнопки с названием, ценой и доходом"""
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        bot.reply_to(message, "Сначала нажми /start")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []

    for b in BUSINESSES:
        owned = any(bus["business_id"] == b["id"] for bus in get_user_businesses(user_id))
        status = "✅ Куплено" if owned else f"💰 {b['price']:,} | Доход: {b['income']:,}"
        btn_text = f"{b['name']} — {status}"

        # Кнопка с callback_data для покупки
        callback = f"buy_{b['id']}" if not owned else "already_bought"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=callback))

    markup.add(*buttons)
    bot.send_message(message.chat.id, "🏙️ Панель бизнесов — нажми, чтобы купить:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "already_bought":
        bot.answer_callback_query(call.id, "Этот бизнес уже у тебя есть!", show_alert=True)
        return

    if data.startswith("buy_"):
        try:
            business_id = int(data.split("_")[1])
        except ValueError:
            bot.answer_callback_query(call.id, "Ошибка данных", show_alert=True)
            return

        business = get_business_by_id(business_id)
        if not business:
            bot.answer_callback_query(call.id, "Бизнес не найден", show_alert=True)
            return

        user = get_user(user_id)
        if not user:
            bot.answer_callback_query(call.id, "Сначала нажми /start", show_alert=True)
            return

        if user["money"] < business["price"]:
            bot.answer_callback_query(call.id, f"Не хватает денег! Нужно: {business['price']:,}", show_alert=True)
            return

        # Покупка
        success = buy_business(user_id, business_id)
        if success:
            update_money(user_id, -business["price"])
            bot.answer_callback_query(call.id, f"✅ Ты купил бизнес: {business['name']}", show_alert=False)
            # Можно дополнительно отправить сообщение о покупке, если нужно
        else:
            bot.answer_callback_query(call.id, "Произошла ошибка при покупке", show_alert=True)

# Запуск
if __name__ == "__main__":
    init_db()
    print("Бот запущен...")
    bot.polling(none_stop=True)
        
