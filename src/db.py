# [SRC-DB] Только работа с базой данных. Создание таблиц, подключение.
# Никаких расчетов дохода или уровней здесь быть не должно.
import os
import sqlite3

DB_NAME = os.getenv("DB_NAME", "game.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')
    
    # Создание таблиц (если их нет)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            gang_id INTEGER DEFAULT NULL,
            fans INTEGER DEFAULT 0,
            vip_until REAL DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_businesses (
            user_id INTEGER, biz_id INTEGER, level INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, biz_id)
        )
    ''')
    return conn
  
