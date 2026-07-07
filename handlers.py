from telebot import types
from game_logic import get_user, can_do_kvartirnik, do_kvartirnik, buy_business, get_profile_text, get_business_display_info, create_gang, BUSINESSES

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user = get_user(message.from_user.id, message.from_user.first_name or "Аноним")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("🎤 Квартирник (КД)")
        btn2 = types.KeyboardButton("🏢 Магазин бизнесов")
        btn3 = types.KeyboardButton("👤 Мой профиль")
        btn4 = types.KeyboardButton("🏙️ Создать банду")
        markup.add(btn1, btn2, btn3, btn4)
        
        text = (
            f"👋 Привет, {user['username']}!\n\n"
            "Добро пожаловать в **Music War**!\n"
            "Строй империю, создавай банды и зарабатывай."
        )
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.text == "🎤 Квартирник (КД)")
    def handle_kvartirnik(message):
        user = get_user(message.from_user.id)
        can_do, time_left = can_do_kvartirnik(user)
        
        if can_do:
            reward, xp, lvl_up = do_kvartirnik(user)
            msg = f"🎤 Соло-выступление прошло! 🎉\nТы заработал {reward:,} 💰 и {xp} XP."
            if lvl_up:
                msg += "\n🎊 Ты повысил уровень!"
            bot.reply_to(message, msg)
        else:
            mins = time_left // 60
            secs = time_left % 60
            bot.reply_to(message, f"⏳ Подожди еще {mins} мин {secs} сек перед следующим квартирником!")

    @bot.message_handler(func=lambda m: m.text == "🏢 Магазин бизнесов")
    def handle_shop(message):
        user = get_user(message.from_user.id)
        businesses_info = get_business_display_info(user)
        
        text = "🏪 **Магазин бизнесов Music War**\n\n"
        for biz in businesses_info:
            lvl_suffix = f" (Lvl {biz['current_lvl']})" if biz['current_lvl'] > 0 else ""
            text += f"{biz['emoji']} {biz['name']}{lvl_suffix} — {biz['price']} → {biz['income']}\n"
        
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
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("buy_biz_"))
    def handle_buy_click(call):
        user = get_user(call.from_user.id)
        biz_name = call.data.replace("buy_biz_", "")
        target_biz = next((b for b in BUSINESSES if b["name"] == biz_name), None)
        
        if not target_biz:
            bot.answer_callback_query(call.id, "❌ Бизнес не найден!", show_alert=True)
            return
            
        success, message = buy_business(user, target_biz["id"])
        bot.answer_callback_query(call.id, message, show_alert=True)
        
        if success:
            # Обновляем сообщение магазина
            businesses_info = get_business_display_info(user)
            text = "🏪 **Магазин бизнесов Music War**\n\n"
            for biz in businesses_info:
                lvl_suffix = f" (Lvl {biz['current_lvl']})" if biz['current_lvl'] > 0 else ""
                text += f"{biz['emoji']} {biz['name']}{lvl_suffix} — {biz['price']} → {biz['income']}\n"
            
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
                bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            except:
                pass

    @bot.callback_query_handler(func=lambda call: call.data == "shop_close")
    def handle_shop_close(call):
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass

    @bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
    def handle_profile(message):
        user = get_user(message.from_user.id)
        text = get_profile_text(user)
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(func=lambda m: m.text == "🏙️ Создать банду")
    def handle_create_gang(message):
        # Упрощенная версия: сразу создаем с дефолтными параметрами для теста
        # В идеале тут нужен FSM (машина состояний), но чтобы не усложнять код:
        user = get_user(message.from_user.id, message.from_user.first_name or "Аноним")
        
        if user["gang_id"]:
            bot.reply_to(message, "❌ Ты уже в банде!")
            return
            
        # Генерируем имя банды из имени юзера для простоты
        gang_name = f"{user['username']}'s Gang"
        district = "Бит-стрит" # Дефолтный район
        
        success, msg = create_gang(user, gang_name, district)
        bot.reply_to(message, msg)
            
