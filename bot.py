import os
import telebot
from telebot import types
from game_logic import (
    get_user, save_user, do_kvartirnik, can_do_kvartirnik, 
    buy_business, get_profile_text, get_business_display_info, create_gang
)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не задан токен бота! Проверьте переменную окружения BOT_TOKEN.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_start(message):
    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля. Попробуй позже.")
        return
    
    text = (
        f"👋 Привет, {user['username']}! Добро пожаловать в Music War!\n\n"
        f"У тебя стартовые {user['balance']:,}\$ и базовый профиль.\n"
        f"Используй команды:\n"
        f"/profile — твой профиль\n"
        f"/buy — купить/прокачать бизнес\n"
        f"/kvartirnik — сыграть на квартирнике (каждые 90 сек)\n"
        f"/gang — создать банду\n"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['profile'])
def send_profile(message):
    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля.")
        return
    bot.reply_to(message, get_profile_text(user), parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def send_buy_menu(message):
    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля.")
        return

    info_list = get_business_display_info(user)
    text = "🏪 **Магазин бизнесов**\n\n"
    for item in info_list:
        text += f"{item['emoji']} {item['name']}\n"
        text += f"   Уровень: {item['current_lvl']} / 10\n"
        text += f"   Доход: {item['income']}\n"
        text += f"   Следующее улучшение: {item['price']}\n\n"
    text += "Напиши ID бизнеса (число от 1 до 12), чтобы купить/прокачать."
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_buy_by_id(message):
    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        return
    biz_id = int(message.text)
    success, response = buy_business(user, biz_id)
    bot.reply_to(message, response)

@bot.message_handler(commands=['kvartirnik'])
def do_kvartirnik_cmd(message):
    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля.")
        return

    can_play, wait_time = can_do_kvartirnik(user)
    if not can_play:
        bot.reply_to(message, f"⏳ Подожди ещё {wait_time} сек до следующего квартирника.")
        return

    reward, xp, lvl_up = do_kvartirnik(user)
    text = f"🎸 Квартирник завершён!\nТы заработал {reward:,}\$ и {xp} XP."
    if lvl_up:
        text += f"\n🎉 Уровень повышен!"
    bot.reply_to(message, text)

@bot.message_handler(commands=['gang'])
def create_gang_cmd(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "📝 Используй: /gang <название> <район>\nПример: /gang Бит-стрит Бит-стрит")
        return

    name = args
    district = args
    
    # Проверка района (упрощенная)
    if district not in ["Бит-стрит", "Золотая студия", "Бас-квартал"]:
        bot.reply_to(message, "❌ Неверный район. Доступные: Бит-стрит, Золотая студия, Бас-квартал")
        return

    user = get_user(message.from_user.id, message.from_user.username or "Аноним")
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля.")
        return

    success, response = create_gang(user, name, district)
    bot.reply_to(message, response)

if __name__ == '__main__':
    print("🚀 Бот запускается...")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"❌ Критическая ошибка бота: {e}")
