import sqlite3

DB_PATH = "/home/musicwar/musicwar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_band(user_id, name):
    conn = get_db()
    try:
        conn.execute("INSERT INTO bands (name, leader_id, members, fund) VALUES (?, ?, ?, 0)", (name, user_id, str(user_id)))
        band_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("UPDATE users SET band_id = ?, band_role = 'leader' WHERE user_id = ?", (band_id, user_id))
        conn.commit()
        conn.close()
        return band_id
    except:
        conn.close()
        return None

def get_band(band_id):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE band_id = ?", (band_id,)).fetchone()
    conn.close()
    return band

def get_band_by_name(name):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE name = ?", (name,)).fetchone()
    conn.close()
    return band

def get_band_members(band_id):
    conn = get_db()
    band = get_band(band_id)
    if not band:
        conn.close()
        return []
    members = band["members"].split(",") if band["members"] else []
    conn.close()
    return members

def add_member(band_id, user_id):
    conn = get_db()
    band = get_band(band_id)
    members = band["members"].split(",") if band["members"] else []
    if str(user_id) not in members:
        members.append(str(user_id))
        conn.execute("UPDATE bands SET members = ? WHERE band_id = ?", (",".join(members), band_id))
        conn.execute("UPDATE users SET band_id = ?, band_role = 'member' WHERE user_id = ?", (band_id, user_id))
        conn.commit()
    conn.close()

def remove_member(band_id, user_id):
    conn = get_db()
    band = get_band(band_id)
    members = band["members"].split(",") if band["members"] else []
    if str(user_id) in members:
        members.remove(str(user_id))
        conn.execute("UPDATE bands SET members = ? WHERE band_id = ?", (",".join(members), band_id))
        conn.execute("UPDATE users SET band_id = 0, band_role = 'member' WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()
