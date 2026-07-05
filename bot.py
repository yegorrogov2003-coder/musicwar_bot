import telebot
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = "8824209793:AAH0TEi9hZ0_pQef1uc2W6xI1f6njNU913W0"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает!")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

thread = threading.Thread(target=run_server)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    print("БОТ ЗАПУЩЕН!")
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
