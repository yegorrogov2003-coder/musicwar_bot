# [SRC-USER] Универсальный профиль. Загрузка и сохранение состояния игрока.
# Работает как «посредник» между ботом и базой данных.
from .db import get_db_connection

def get_user(user_id, username="Аноним"):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cur.fetchone()

        # Если пользователя нет — создаем с базовыми значениями
        if not row:
            cur.execute('INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)',
                        (user_id, username, 10000))
            conn.commit()
            cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cur.fetchone()

        # Превращаем строку БД в словарь
        user = {
            "user_id": row, "username": row[1](https://pythonru.com/primery/telegram-bot-na-python-ustanovka-i-nastrojka), "balance": row[2](https://dzen.ru/a/YzHwMs-VpF6BeAnC),
            "level": row[3](https://habr.com/ru/articles/862434/), "xp": row[4](https://habr.com/ru/companies/otus/articles/760890/), "gang_id": row[5](https://sky.pro/wiki/python/razrabotka-telegram-botov-na-python/),
            "fans": row, "vip_until": row
        }

        # Загружаем бизнесы пользователя
        cur.execute('SELECT biz_id, level FROM user_businesses WHERE user_id = ?', (user_id,))
        user["businesses"] = {row: row[1](https://pythonru.com/primery/telegram-bot-na-python-ustanovka-i-nastrojka) for row in cur.fetchall()}
        return user
    except Exception as e:
        print(f"❌ Ошибка в get_user: {e}")
        return None
    finally:
        conn.close()

def save_user(user):
    # Здесь будет логика обновления полей в БД
    pass
  
