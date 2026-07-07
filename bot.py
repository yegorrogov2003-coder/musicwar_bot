import os
import telebot
from handlers import register_handlers

# --- НАСТРОЙКИ ---
TOKEN = os.environ.get("BOT_TOKEN")

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
    
    # Подключаем все команды из handlers.py
    register_handlers(bot)
    
    print("🚀 Запуск polling режима (ожидание сообщений)...")
    
    # ВАЖНО: Запускаем поллинг прямо здесь, а не импортируем функцию
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"💥 Ошибка при запуске бота: {e}")
        
