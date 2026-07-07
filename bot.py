import os
import telebot
from telebot import types

# --- НАСТРОЙКИ И БЕЗОПАСНОСТЬ ---

# 1. Получаем токен из переменной окружения (из панели Render)
TOKEN = os.environ.get("BOT_TOKEN")

# 2. Критическая проверка: если токена нет, бот падает с понятной ошибкой в логах
if not TOKEN:
    raise ValueError(
        "❌ КРИТИЧЕСКАЯ ОШИБКА: ТОКЕН НЕ НАЙДЕН!\n"
        "1. Зайди в панель Render -> вкладка Environment.\n"
        "2. Добавь переменную: Key = BOT_TOKEN, Value = твой_токен.\n"
        "3. Нажми Save, rebuild, and deploy."
    )

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# --- ОБРАБОТЧИКИ КОМАНД (HANDLERS) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Реакция на команду /start"""
    markup = types.ReplyKeyboardRemove() # Убираем клавиатуру, если была
    
    # Формируем красивое сообщение
    response_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я успешно запустился на Render! ✅\n"
        "Токен корректно загружен из переменных окружения.\n\n"
        "Попробуй нажать кнопку ниже или напиши любое сообщение."
    )
    
    # Создаем простую клавиатуру для теста
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🤖 Кто ты?")
    btn2 = types.KeyboardButton("📜 Помощь")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, response_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🤖 Кто ты?")
def about_bot(message):
    """Реакция на кнопку 'Кто ты?'"""
    bot.reply_to(message, "Я тестовый бот, который умеет брать токены из переменных окружения! 🧠")

@bot.message_handler(func=lambda message: message.text == "📜 Помощь")
def help_bot(message):
    """Реакция на кнопку 'Помощь'"""
    bot.reply_to(message, "Доступные команды:\n/start — перезапустить приветствие\nПросто пиши мне текст — я отвечу эхо-сообщением.")

@bot.message_handler(content_types=['text'])
def echo_all(message):
    """Эхо-ответ на любой текст (если не сработала другая команда)"""
    # Простая защита от спама в логах: не отвечаем на свои же сообщения, если вдруг
    if message.text and not message.text.startswith("🤖") and not message.text.startswith("📜"):
        bot.reply_to(message, f"Ты написал: {message.text} 💬")

# --- ЗАПУСК ---

if __name__ == '__main__':
    print("🔌 Подключение к серверам Telegram...")
    print("🗝️ Токен загружен успешно (значение скрыто в целях безопасности).")
    print("🚀 Запуск polling режима...")
    
    try:
        # none_stop=True гарантирует, что бот не упадет при ошибке сети
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"💥 Произошла критическая ошибка при запуске: {e}")
        
