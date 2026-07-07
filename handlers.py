from telebot import types
from game_logic import get_user, can_do_kvartirnik, do_kvartirnik, buy_business, calculate_passive_income, get_profile_text, BUSINESSES, get_business_display_info, can_do_label_show, do_label_show, buy_with_cash

# ВСТАВЬ СЮДА СВОЙ TELEGRAM ID (числовой), чтобы получить доступ к админке
ADMIN_IDS = [123456789]

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user = get_user(message.from_user.id)
        user['username'] = message.from_user.first_name or "Аноним"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("🎤 Квартирник (КД)")
        btn2 = types.KeyboardButton("🎸 Групповое выступление")
        btn3 = types.KeyboardButton("🏢 Магазин бизнесов")
        btn4 = types.KeyboardButton("💎 Донат / Магазин Кэш")
        btn5 = types.KeyboardButton("👤 Мой профиль")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        text = (
            f"👋 Привет, {user['username']}!\n\n"
            "Добро пожаловать в **Music War**!\n"
            "Строй империю, создавай банды и захватывай районы."
        )
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.text == "🎤 Квартирник (КД)")
    def handle_kvartirnik(message):
        user = get_user(message.from_user.id)
        can_do, time_left = can_do_kvartirnik(user)
        if can_do:
            reward, xp, lvl_up = do_kvartirnik(user
                                               
