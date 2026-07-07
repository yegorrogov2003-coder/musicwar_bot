import telebot
from telebot import types
import time

TOKEN = "8948916925:AAEwHnUEp5CWkyow8tnwgAmadPbOEHyy6Ds"

if not TOKEN:
    raise ValueError("❌ ТОКЕН НЕ ВСТАВЛЕН! Вставь его в строку TOKEN = \"...\"")

bot = telebot.TeleBot(TOKEN)

# --- ДАННЫЕ ИГРЫ ---
users_db = {}

# Экономика: первый бизнес почти подарок, дальше хардкор.
# cost_per_level - это цена ОДНОГО уровня. Цена улучшения = cost_per_level * (текущий_уровень + 1)
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "price": 1800, "income": 400, "max_level": 10, "cost_per_level": 1200},
    {"id": 2, "name": "Студия звука", "price": 8000, "income": 1500, "max_level": 8, "cost_per_level": 6000},
    {"id": 3, "name": "Музыкальный магазин", "price": 25000, "income": 4500, "max_level": 7, "cost_per_level": 18000},
    {"id": 4, "name": "Рэп-баттл", "price": 70000, "income": 11000, "max_level": 6, "cost_per_level": 50000},
    {"id": 5, "name": "Студия записи", "price": 160000, "income": 26000, "max_level": 5, "cost_per_level": 130000},
    {"id": 6, "name": "Звукозаписывающая студия", "price": 450000, "income": 75000, "max_level": 4, "cost_per_level": 350000},
    {"id": 7, "name": "Продакшн", "price": 1100000, "income": 110000, "max_level": 4, "cost_per_level": 900000},
    {"id": 8, "name": "Ночной клуб", "price": 3000000, "income": 280000, "max_level": 3, "cost_per_level": 2500000},
    {"id": 9, "name": "Радио", "price": 7000000, "income": 550000, "max_level": 3, "cost_per_level": 6000000},
    {"id": 10, "name": "Клипмейкер", "price": 14000000, "income": 950000, "max_level": 3, "cost_per_level": 12000000},
    {"id": 11, "name": "ТВ-канал", "price": 28000000, "income": 1800000, "max_level": 2, "cost_per_level": 22000000},
    {"id": 12, "name": "Медиаимперия", "price": 65000000, "income": 4200000, "max_level": 2, "cost_per_level": 55000000}
]

RANKS = [
    "🎧 Начинающий", "🎤 Андеграунд", "🎵 Хип-хопер", "🏆 Прорыв", "📀 Известный",
    "💿 Популярный", "🎶 Топ-чарт", "👑 Платиновый", "⭐ Бриллиантовый", "💎 Music Legend"
]

# КД на квартирник: 90 секунд (1.5 минуты)
KVTIRNIK_COOLDOWN_SECONDS = 90


def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "user_id": user_id,
            "username": "",
            "money": 1500,          # Чуть больше на старте, чтобы хватило на первый апгрейд или почти на бизнес
            "xp": 0,
            "level": 1,
            "group": "",
            "businesses": {},       # {biz_id: level}
            "last_income_time": time.time(),
            "last_kvartirnik_time": 0
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
    for biz_id, biz_level in user["businesses"].items():
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if biz:
            # Доход растёт с прокачкой: базовый доход * (1 + 0.3 * уровень)
            income_multiplier = 1 + (0.3 * biz_level)
            total_income += biz["income"] * income_multiplier * elapsed_hours

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
    btn3 = types.KeyboardButton("🔧 Улучшить бизнес")
    btn4 = types.KeyboardButton("👤 Профиль")
    btn5 = types.KeyboardButton("🤝 Банда")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup


def get_group_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for g in ["Реперы", "Рокеры", "Меломаны", "Клубмены"]:
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

    now = time.time()
    time_since_last = now - user["last_kvartirnik_time"]

    # Проверка КД (1.5 минуты)
    if time_since_last < KVTIRNIK_COOLDOWN_SECONDS:
        remaining = int(KVTIRNIK_COOLDOWN_SECONDS - time_since_last)
        mins = remaining // 60
        secs = remaining % 60
        # Показываем КД красиво: "1 мин 20 сек" или просто "85 сек"
        if mins > 0:
            time_text = f"{mins} мин {secs} сек"
        else:
            time_text = f"{secs} сек"
        bot.reply_to(message, f"⏳ Квартирник на КД! Подожди ещё {time_text}.")
        return

    # Награда за квартирник
    earned_money = 800 + (user["level"] * 50)
    earned_xp = 12 + (user["level"] // 2)

    user["money"] += earned_money
    leveled = add_xp(user, earned_xp)
    user["last_kvartirnik_time"] = now
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
    user["businesses"][biz_id] = 0  # Купили с уровнем 0
    save_user(user)
    bot.answer_callback_query(call.id, f"✅ Ты купил: {business['name']}!", show_alert=False)


@bot.message_handler(func=lambda m: m.text == "🔧 Улучшить бизнес")
def show_upgrade_panel(message):
    """Панель улучшений: показывает только купленные бизнесы и кнопки улучшить"""
    user = get_user(message.from_user.id)
    give_income(user)

    if not user["businesses"]:
        bot.reply_to(message, "❌ У тебя пока нет ни одного бизнеса. Сначала купи что-то в разделе «Бизнесы».")
        return

    text_parts = ["🔧 Панель улучшения бизнесов:\n"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []

    for biz_id, current_level in user["businesses"].items():
        biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
        if not biz:
            continue

        next_level = current_level + 1
        can_upgrade = next_level <= biz["max_level"]
        upgrade_cost = biz["cost_per_level"] * next_level  # Цена растёт с каждым уровнем

        level_status = f"Уровень: {current_level}/{biz['max_level']}"
        money_status = ""
        action_btn_text = ""
        action_callback = ""

        if not can_upgrade:
            money_status = "🏆 Макс. уровень достигнут"
            action_btn_text = "—"
        elif user["money"] >= upgrade_cost:
            money_status = f"💰 Цена улучшения: {upgrade_cost:,}"
            action_btn_text = "🚀 Улучшить"
            action_callback = f"upgrade_{biz_id}"
        else:
            money_status = f"❌ Нужно: {upgrade_cost:,}, у тебя: {user['money']:,}"
            action_btn_text = "🚫 Не хватает денег"

        line = f"{biz['name']}\n{level_status}\n{money_status}\n"
        text_parts.append(line)

        if action_callback:
            buttons.append(types.InlineKeyboardButton(action_btn_text, callback_data=action_callback))

    text = "\n".join(text_parts)
    markup.add(*buttons)

    bot.send_message(message.chat.id, text, reply_markup=markup)
    
