import time
import sqlite3

DB_NAME = 'game.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')  # Улучшает параллелизм в SQLite
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            gang_id INTEGER DEFAULT NULL,
            gang_role TEXT DEFAULT 'none',
            fans INTEGER DEFAULT 0,
            district_bonus REAL DEFAULT 1.0,
            last_kvartirnik REAL DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_businesses (
            user_id INTEGER,
            biz_id INTEGER,
            level INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, biz_id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS gangs (
            gang_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner_id INTEGER,
            district TEXT,
            bonus_type TEXT,
            bonus_value REAL
        )
    ''')
    return conn

def get_user(user_id, username="Аноним"):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cur.fetchone()

        if not row:
            cur.execute('INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)',
                        (user_id, username, 10000))
            conn.commit()
            cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cur.fetchone()

        # Преобразуем кортеж в словарь
        user = {
            "user_id": row, "username": row[1](https://www.pythontutorials.net/blog/sqlite3-programmingerror-cannot-operate-on-a-closed-database-python-sqlite/), "balance": row[2](https://github.com/ruslaxe/ozon-calculator/blob/main/RENDER_TROUBLESHOOTING.md),
            "level": row[3](https://qna.habr.com/q/1358802), "xp": row[4](https://www.tutorialpedia.org/blog/sqlite-python-sqlite3-operationalerror-database-is-locked/), "gang_id": row[5](https://render.com/docs/troubleshooting-deploys),
            "gang_role": row, "fans": row, "district_bonus": row,
            "last_kvartirnik": row
        }

        # Загружаем бизнесы — ДО закрытия соединения
        cur.execute('SELECT biz_id, level FROM user_businesses WHERE user_id = ?', (user_id,))
        user["businesses"] = {row: row[1](https://www.pythontutorials.net/blog/sqlite3-programmingerror-cannot-operate-on-a-closed-database-python-sqlite/) for row in cur.fetchall()}
        return user
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None
    finally:
        conn.close()

def save_user(user):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('''
            UPDATE users SET username=?, balance=?, level=?, xp=?, gang_id=?, 
            gang_role=?, fans=?, district_bonus=?, last_kvartirnik=?
            WHERE user_id=?
        ''', (user["username"], user["balance"], user["level"], user["xp"],
              user["gang_id"], user["gang_role"], user["fans"],
              user["district_bonus"], user["last_kvartirnik"], user["user_id"]))

        # Обновляем бизнесы
        cur.execute('DELETE FROM user_businesses WHERE user_id = ?', (user["user_id"],))
        for biz_id, lvl in user["businesses"].items():
            cur.execute('INSERT OR REPLACE INTO user_businesses (user_id, biz_id, level) VALUES (?, ?, ?)',
                        (user["user_id"], biz_id, lvl))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении пользователя: {e}")
    finally:
        conn.close()

# --- ДАННЫЕ ИГРЫ (без изменений) ---
BUSINESSES = [
    {"id": 1, "name": "Битмейкер", "base_price": 50000, "base_income": 5000, "max_level": 10},
    {"id": 2, "name": "Студия звука", "base_price": 120000, "base_income": 10000, "max_level": 10},
    {"id": 3, "name": "Музыкальный магаз", "base_price": 300000, "base_income": 22000, "max_level": 10},
    {"id": 4, "name": "Рэп-баттл", "base_price": 600000, "base_income": 40000, "max_level": 10},
    {"id": 5, "name": "Звукозапись", "base_price": 1200000, "base_income": 80000, "max_level": 10},
    {"id": 6, "name": "Music War Records", "base_price": 3000000, "base_income": 200000, "max_level": 10},
    {"id": 7, "name": "Продакшн", "base_price": 6000000, "base_income": 400000, "max_level": 10},
    {"id": 8, "name": "Ночной клуб", "base_price": 15000000, "base_income": 950000, "max_level": 10},
    {"id": 9, "name": "Радио", "base_price": 30000000, "base_income": 1900000, "max_level": 10},
    {"id": 10, "name": "Клипмейкер", "base_price": 60000000, "base_income": 3800000, "max_level": 10},
    {"id": 11, "name": "ТВ-канал", "base_price": 120000000, "base_income": 7500000, "max_level": 10},
    {"id": 12, "name": "Медиаимперия", "base_price": 300000000, "base_income": 18000000, "max_level": 10},
]

DISTRICTS = {
    "Бит-стрит": {"bonus_type": "xp", "value": 1.3},
    "Золотая студия": {"bonus_type": "income", "value": 1.3},
    "Бас-квартал": {"bonus_type": "raid", "value": 1.3}
}

# --- ЛОГИКА КВАРТИРНИКОВ ---
def can_do_kvartirnik(user):
    cooldown_seconds = 90
    now = time.time()
    time_since = now - user["last_kvartirnik"]
    if time_since >= cooldown_seconds:
        return True, 0
    return False, int(cooldown_seconds - time_since)

def do_kvartirnik(user):
    user["last_kvartirnik"] = time.time()
    base_reward = 1500 + (user["level"] * 200)
    reward = int(base_reward)
    xp = 50 + (user["level"] * 5)

    if user["district_bonus"] > 1.0:
        reward = int(reward * user["district_bonus"])
        xp = int(xp * user["district_bonus"])

    user["balance"] += reward
    user["xp"] += xp

    lvl_up = False
    while user["xp"] >= user["level"] * 200:
        user["level"] += 1
        lvl_up = True

    save_user(user)
    return reward, xp, lvl_up

# --- ЛОГИКА БИЗНЕСОВ ---
def buy_business(user, biz_id):
    biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
    if not biz:
        return False, "❌ Бизнес не найден."

    current_level = user["businesses"].get(biz_id, 0)
    if current_level >= biz["max_level"]:
        return False, f"🏆 {biz['name']} уже на макс. уровне!"

    next_level = current_level + 1
    price = int(biz["base_price"] * 0.1 * next_level)

    if user["balance"] < price:
        return False, f"❌ Не хватает денег! Нужно {price:,}, у тебя {user['balance']:,}."

    user["balance"] -= price
    user["businesses"][biz_id] = next_level
    save_user(user)
    return True, f"✅ Прокачан {biz['name']} до Lvl {next_level} за {price:,}!"

def get_business_display_info(user):
    info_list = []
    emoji_map = {
        "Битмейкер": "🎹", "Студия звука": "🎤", "Музыкальный магаз": "👕",
        "Рэп-баттл": "🥊", "Звукозапись": "🎙️", "Music War Records": "💿",
        "Продакшн": "🎬", "Ночной клуб": "🌃", "Радио": "📻",
        "Клипмейкер": "🎥", "ТВ-канал": "📺", "Медиаимперия": "🌐"
    }

    for biz in BUSINESSES:
        biz_id = biz["id"]
        current_lvl = user["businesses"].get(biz_id, 0)
        current_income = int(biz["base_income"] * (1 + (0.1 * current_lvl)))
        next_lvl = current_lvl + 1

        if current_lvl >= biz["max_level"]:
            price_text = "🏆 Макс. уровень"
            buy_btn_text = None
        else:
            price = int(biz["base_price"] * 0.1 * next_lvl)
            price_text = f"{price:,}\$"
            buy_btn_text = f"Купить {biz['name']}"

        info_list.append({
            "name": biz["name"],
            "emoji": emoji_map.get(biz["name"], "🏢"),
            "price": price_text,
            "income": f"{current_income:,}\$",
            "current_lvl": current_lvl,
            "buy_btn_text": buy_btn_text
        })
    return info_list

# --- ЛОГИКА БАНД ---
def create_gang(user, name, district):
    if user["gang_id"] is not None:
        return False, "❌ Ты уже состоишь в банде!"

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO gangs (name, owner_id, district, bonus_type, bonus_value) VALUES (?, ?, ?, ?, ?)',
                    (name, user["user_id"], district, "income", 1.3))
        gang_id = cur.lastrowid
        conn.commit()

        user["gang_id"] = gang_id
        user["gang_role"] = "boss"
        user["district_bonus"] = 1.3
        save_user(user)
        return True, f"✅ Банда '{name}' создана в районе '{district}'!"
    except Exception as e:
        print(f"Ошибка при создании банды: {e}")
        return False, "❌ Ошибка при создании банды."
    finally:
        conn.close()

def get_profile_text(user):
    text = (
        f"👤 **Профиль Music War**\n\n"
        f"💰 Баланс: {user['balance']:,}\n"
        f"📈 Уровень: {user['level']} ({user['xp']} XP)\n"
    )
    if user["gang_id"]:
        text += f"🏙️ Банда: ID {user['gang_id']} | Роль: {user['gang_role']}\n"
        text += f"🛡️ Районный бонус: x{user['district_bonus']}\n"
    else:
        text += "🏙️ Банда: Не состоит\n"

    text += "\n🏢 Бизнесы:\n"
    if not user["businesses"]:
        text += "   (Нет бизнесов)\n"
    else:
        for biz_id, level in user["businesses"].items():
            biz = next((b for b in BUSINESSES if b["id"] == biz_id), None)
            if biz:
                text += f"   • {biz['name']} (Lvl {level})\n"
    return text
    
