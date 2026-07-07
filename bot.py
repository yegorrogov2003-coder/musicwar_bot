import telebot
from telebot import types
import time

# Вставь свой токен между кавычками. Без него бот не запустится!
TOKEN = "8948916925:AAEwHnUEp5CWkyow8tnwgAmadPbOEHyy6Ds"

if not TOKEN:
    raise ValueError("❌ ТОКЕН НЕ ВСТАВЛЕН! Открой bot.py и напиши свой токен в строке TOKEN = \"...\"")

bot = telebot.TeleBot(TOKEN)

# --- ДАННЫЕ ИГРЫ (В ПАМЯТИ) ---
users_db = {}

GROUPS = ["Реперы", "Рокеры", "Меломаны", "Клубмены"]

BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 35000, "income": 4000},
    {"id": 2, "name": "Студия звука", "price": 90000, "income": 8000},
    {"id": 3, "name": "Музыкальный магазин", "price": 250000, "income": 18000},
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

RANKS = [
    "🎧 Начинающий", "🎤 Андеграунд", "🎵 Хип-хопер", "🏆 Прорыв", "📀 Известный",
    "💿 Популярный", "🎶 Топ-чарт", "👑 Платиновый", "⭐ Бриллиантовый", "💎 Music Legend"
]

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "user_id": user_id,
            "username": "",
            "money": 1000,
            "xp": 0,
            "level": 1,
            "group": "",
            "businesses": [],
            "last_income_time": time.time()
        }
    return users_db[user_id]

def save_user(user):
    users_db[user["user_id"]] = user

def calculate_income_bonus(level):
    bonus = 0
    if level >= 50: bonus = 0.25
    elif level >= 40: bonus = 0.20
    elif level >= 30: bonus = 0.15
    elif level >= 20: bonus = 0.10
    elif level >= 10: bonus = 0.05
    return bonus

def give_income(user):
    now = time.time()
    elapsed_hours = int((now - user["last_income_time"]) // 3600)
    if elapsed_hours < 1:
        return 0

    total_income = 0
    for biz_id in user["businesses"]:
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if biz:
            total_income += biz["income"] * elapsed_hours

    bonus_mult = calculate_income_bonus(user["level"])
    total_income = int(total_income * (1 + bonus_mult))

    user["money"] += total_income
    user["last_income_time"] = now
    save_user(user)
    return total_income

def add_xp(user, amount):
    user["xp"] += amount
    leveled_up = False
    while user["level"] < 50 and user["xp"] >= user["level"] * 80:
        user["xp"] -= user["level"] * 80
        user["level"] += 1
        leveled_up = True
    save_user(user)
    return leveled_up

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🎙️ Квартирник")
    btn2 = types.KeyboardButton("🏢 Бизнесы")
    btn3 = types.KeyboardButton("👤 Профиль")
    btn4 = types.KeyboardButton("🤝 Банда")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

def get_group_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for g in GROUPS:
        buttons.append(types.InlineKeyboardButton(f"🎸 {g}", callback_data=f"group_{g}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=["start"])
def send_start(message):
    user = get_user(message.from_user.id)
    user["username"] = message.from_user.username or "Unknown"
    save_user(user)

    if not user["group"]:
        bot.send_message(
            message.chat.id, 
            f"👋 Привет, {user['username']}! Ты в игре Music War.\n\nВыбери свою группировку:",
            reply_markup=get_group_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"👋 Добро пожаловать обратно!\nТвой путь: {user['group']}.",
            reply_markup=get_main_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def handle_group_select(call):
    group_name = call.data.split("_")[1]
    user = get_user(call.from_user.id)
    user["group"] = group_name
    save_user(user)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Ты выбрал: {group_name}!"
    )
    bot.send_message(call.message.chat.id, "Теперь ты можешь зарабатывать!", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🎙️ Квартирник")
def do_kvartirnik(message):
    user = get_user(message.from_user.id)
    give_income(user)

    earned_money = 800 + (user["level"] * 60)
    earned_xp = 10 + (user["level"] // 2)

    user["money"] += earned_money
    leveled = add_xp(user, earned_xp)
    save_user(user)

    text = f"🎸 Ты отыграл квартирник!\n💰 Получено монет: {earned_money:,}\n⭐ Получено опыта: {earned_xp}"
    if leveled:
        text += "\n🎉 Поздравляем, ты повысил уровень!"

    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: m.text == "🏢 Бизнесы")
def show_businesses(message):
    user = get_user(message.from_user.id)
    give_income(user)

    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    for b in BUSINESSES:
        status = "✅ Куплено" if b["id"] in user["businesses"] else f"{b['price']:,} 💰"
        btn_text = f"{b['name']} — {status}"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{b['id']}"))
    markup.add(*buttons)

    bot.send_message(message.chat.id, "🏙️ Магазин бизнесов:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_business(call):
    biz_id = int(call.data.split("_")[1])
    user = get_user(call.from_user.id)
    give_income(user)

    business = next((b for b in BUSINESSES if b["id"] == biz_id), None)
    if not business:
        bot.answer_callback_query(call.id, "Ошибка", show_alert=True)
        return

    if biz_id in user["businesses"]:
        bot.answer_callback_query(call.id, "У тебя уже есть этот бизнес!", show_alert=False)
        return

    if user["money"] < business["price"]:
        bot.answer_callback_query(
            call.id, 
            f"❌ Не хватает денег! Нужно: {business['price']:,}. У тебя: {user['money']:,}", 
            show_alert=True
        )
        return

    user["money"] -= business["price"]
    user["businesses"].append(biz_id)
    save_user(user)
    bot.answer_callback_query(call.id, f"✅ Ты купил: {business['name']}!", show_alert=False)

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def show_profile(message):
    user = get_user(message.from_user.id)
    give_income(user)

    rank_index = min(user["level"] - 1, len(RANKS) - 1)
    rank = RANKS[rank_index]

    biz_names = []
    for bid in user["businesses"]:
        b = next((x for x in BUSINESSES if x["id"] == bid), None)
        if b: biz_names.append(b["name"])
    biz_text = ", ".join(biz_names) if biz_names else "Нет бизнесов"

    text = (f"👤 Профиль: @{user['username']}\n"
            f"🏙️ Группировка: {user['group'] or 'Не выбрана'}\n"
            f"💰 Деньги: {user['money']:,}\n"
            f"⭐ Уровень: {user['level']} ({rank})\n"
            f"⚡ Опыт: {user['xp']}/{user['level'] * 80}\n"
            f"🏢 Твои бизнесы: {biz_text}")

    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: m.text == "🤝 Банда")
def show_banda(message):
    bot.reply_to(message, "🫡 Система банд скоро появится!")

if __name__ == "__main__":
    print("MusicWar Bot запускается...")
    bot.polling(none_stop=True)
        
