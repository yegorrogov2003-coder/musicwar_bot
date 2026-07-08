# [SRC-BOT] Точка входа. Только команды, кнопки и отправка сообщений.
# Вся игровая логика вынесена в папку src/systems.
import telebot
from src.config import EMOJI_MAP
from src.user import get_user

# Вставь сюда свой токен от BotFather
BOT_TOKEN = "8948916925:AAEwHnUEp5CWkyow8tnwgAmadPbOEHyy6Ds"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = get_user(message.from_user.id, message.from_user.username)
    if not user:
        bot.reply_to(message, "❌ Ошибка загрузки профиля.")
        return
    
    # Пример использования данных из других модулей
    biz_count = len(user.get("businesses", {}))
    bot.reply_to(message, f"Привет, {user['username']}! У тебя открыто бизнесов: {biz_count}")

print("Бот запущен...")
bot.polling(none_stop=True)
