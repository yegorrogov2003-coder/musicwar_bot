import os
import telebot
from handlers import register_handlers, start_polling

# --- НАСТРОЙКИ ---

# Получаем токен из переменной окружения (Render Environment)
TOKEN = os.environ.get("BOT_TOKEN")

# Критическая проверка: если токена нет, сразу падаем с понятной ошибкой в логах
if not TOKEN:
    raise ValueError(
        "❌ КРИТИЧЕСКАЯ ОШИБКА: ТОКЕН НЕ НАЙДЕН!\n"
        "1. Зайди в панель Render -> вкладка Environment.\n"
        "2. Добавь переменную: Key = BOT_TOKEN, Value = твой_токен.\n"
        "3. Нажми Save, rebuild, and deploy."
    )

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# --- ЗАПУСК ---

if __name__ == '__main__':
    print("🔌 Сборка бота с экономикой и КД...")
    
    # Подключаем всю логику команд из handlers.py
    register_handlers(bot)
    
    print("🚀 Запуск polling режима (ожидание сообщений)...")
    start_polling(bot)
    
