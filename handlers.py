from telebot import types
from game_logic import get_user, can_do_kvartirnik, do_kvartirnik, buy_business, calculate_passive_income, get_profile_text, BUSINESSES

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user = get_user(message.from_user.id)
        user['username'] = message.from_user.first_name or "Аноним"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("🎤 Квартирник (КД)")
        btn2 = types.KeyboardButton("🏢 Магазин бизнесов")
        btn3 = types.KeyboardButton("👤 Мой профиль")
        btn4 = types.KeyboardButton("💸 Получить доход")
        markup.add(btn1, btn2, btn3, btn4)
        
        text = (
            f"👋 Привет, {user['username']}!\n\n"
            "Ты в игре 'Музыкальная Империя'.\n"
            "Зарабатывай на квартирниках и строй бизнес!"
        )
        bot.reply_to(message, text, reply_markup=markup)

    @bot.message_handler(func=lambda m: m.text == "🎤 Квартирник (КД)")
    def handle_kvartirnik(message):
        user = get_user(message.from_user.id)
        can_do, time_left = can_do_kvartirnik(user)
        
        if can_do:
            reward, xp, lvl_up = do_kvartirnik(user)
            msg = f"🎤 Квартирник прошел! 🎉\nТы заработал {reward} 💰 и {xp} XP."
            if lvl_up:
                msg += "\n🎊 Ты повысил уровень!"
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, f"⏳ Подожди еще {time_left} секунд перед следующим квартирником!")

    @bot.message_handler(func=lambda m: m.text == "🏢 Магазин бизнесов")
    def handle_shop(message):
        user = get_user(message.from_user.id)
        text = "🛒 **Магазин бизнесов**:\n\n"
        
        for biz in BUSINESSES:
            current_lvl = user["businesses"].get(biz["id"], 0)
            next_lvl = current_lvl + 1
            
            if current_lvl >= biz["max_level"]:
                status = "🏆 Макс. уровень"
            else:
                price = biz["cost_per_level"] * next_lvl
                status = f"💰 Цена: {price}"
            
            text += f"{biz['name']} (Ур. {current_lvl}) — {status}\n"
        
        text += "\nНажми на название бизнеса, чтобы купить (в следующей версии будет кнопка). Пока просто знай цены!"
        # Для демо-версии просто выводим список. Кнопки с ID сделаем позже, если захочешь.
        bot.reply_to(message, text)

    @bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
    def handle_profile(message):
        user = get_user(message.from_user.id)
        # Сначала начисляем пассивный доход
        income = calculate_passive_income(user)
        text = get_profile_text(user)
        if income > 0:
            text = f"💸 Получено пассивно: {income} 💰\n\n" + text
        bot.reply_to(message, text)

    @bot.message_handler(func=lambda m: m.text == "💸 Получить доход")
    def handle_income(message):
        user = get_user(message.from_user.id)
        income = calculate_passive_income(user)
        if income > 0:
            bot.reply_to(message, f"✅ Начислено: {income} 💰")
        else:
            bot.reply_to(message, "⏳ Доход пока не накопился (прошло меньше часа).")

    @bot.message_handler(content_types=['text'])
    def echo_all(message):
        # Если нажали не ту кнопку
        bot.reply_to(message, "Нажми на кнопку в меню! 👇")
      
