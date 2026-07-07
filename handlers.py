from telebot import types
from game_logic import get_user, can_do_kvartirnik, do_kvartirnik, buy_business, calculate_passive_income, get_profile_text, BUSINESSES, get_business_display_info

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
            msg = f"🎤 Квартирник прошел! 🎉\nТы заработал {reward:,} 💰 и {xp} XP."
            if lvl_up:
                msg += "\n🎊 Ты повысил уровень!"
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, f"⏳ Подожди еще {time_left} секунд перед следующим квартирником!")

    @bot.message_handler(func=lambda m: m.text == "🏢 Магазин бизнесов")
    def handle_shop(message):
        user = get_user(message.from_user.id)
        businesses_info = get_business_display_info(user)
        
        # Формируем текст сообщения (как на скрине: Эмодзи Название — Цена → Доход)
        text = "🏪 **Магазин бизнесов**\n\n"
        
        for biz in businesses_info:
            lvl_suffix = f" (Lvl {biz['current_lvl']})" if biz['current_lvl'] > 0 else ""
            text += f"{biz['emoji']} {biz['name']}{lvl_suffix} — {biz['price']} → {biz['income']}\n"
        
        text += "\n👇 Нажми на кнопку ниже, чтобы купить бизнес."
        text += "\n\n📊 Инфляция: 0% | VIP бонус: 0%"
        
        # Создаем кнопки (как на скрине: по 2 в ряд)
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        for biz in businesses_info:
            if biz['buy_btn_text']:
                # Копируем название бизнеса для callback_data
                callback_data = f"buy_biz_{biz['name']}" 
                btn = types.InlineKeyboardButton(f"{biz['emoji']} {biz['name']}", callback_data=callback_data)
                buttons.append(btn)
        
        # Кнопка "Далее" (заглушка, если бизнесов больше 6)
        if len(businesses_info) > 6:
            next_btn = types.InlineKeyboardButton("▶️ Далее", callback_data="shop_next_page")
            buttons.append(next_btn)
            
        # Кнопка "Закрыть"
        close_btn = types.InlineKeyboardButton("❌ Закрыть", callback_data="shop_close")
        buttons.append(close_btn)
        
        markup.add(*buttons)
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_biz_"))
    def handle_buy_click(call):
        user = get_user(call.from_user.id)
        biz_name = call.data.replace("buy_biz_", "")
        
        # Ищем ID бизнеса по имени (так как названия мы не меняем)
        target_biz = next((b for b in BUSINESSES if b["name"] == biz_name), None)
        
        if not target_biz:
            bot.answer_callback_query(call.id, "❌ Бизнес не найден!", show_alert=True)
            return
            
        success, message = buy_business(user, target_biz["id"])
        
        if success:
            bot.answer_callback_query(call.id, message, show_alert=True)
            # Обновляем сообщение магазина, чтобы показать новый уровень
            handle_shop_update(call, user)
        else:
            bot.answer_callback_query(call.id, message, show_alert=True)

    def handle_shop_update(call, user):
        """Перерисовывает сообщение магазина после покупки."""
        businesses_info = get_business_display_info(user)
        text = "🏪 **Магазин бизнесов (обновлено)**\n\n"
        for biz in businesses_info:
            lvl_suffix = f" (Lvl {biz['current_lvl']})" if biz['current_lvl'] > 0 else ""
            text += f"{biz['emoji']} {biz['name']}{lvl_suffix} — {biz['price']} → {biz['income']}\n"
        text += "\n👇 Выбери другой бизнес."
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for biz in businesses_info:
            if biz['buy_btn_text']:
                callback_data = f"buy_biz_{biz['name']}"
                btn = types.InlineKeyboardButton(f"{biz['emoji']} {biz['name']}", callback_data=callback_data)
                buttons.append(btn)
        
        close_btn = types.InlineKeyboardButton("❌ Закрыть", callback_data="shop_close")
        buttons.append(close_btn)
        markup.add(*buttons)
        
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            pass  # Если сообщение нельзя редактировать, просто игнорируем

    @bot.callback_query_handler(func=lambda call: call.data == "shop_close")
    def handle_shop_close(call):
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, "🛒 Магазин закрыт. Выбирай действие в меню.")
        except Exception:
            pass

    @bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
    def handle_profile(message):
        user = get_user(message.from_user.id)
        income = calculate_passive_income(user)
        text = get_profile_text(user)
        if income > 0:
            text = f"💸 Получено пассивно: {income:,} 💰\n\n" + text
        bot.reply_to(message, text)

    @bot.message_handler(func=lambda m: m.text == "💸 Получить доход")
    def handle_income(message):
        user = get_user(message.from_user.id)
        income = calculate_passive_income(user)
        if income > 0:
            bot.reply_to(message, f"✅ Начислено: {income:,} 💰")
        else:
            bot.reply_to(message, "⏳ Доход пока не накопился.")

    @bot.message_handler(content_types=['text'])
    def echo_all(message):
        bot.reply_to(message, "Нажми на кнопку в меню! 👇")
        
