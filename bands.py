import sqlite3

DB_PATH = "musicwar.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_band(band_id):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE band_id = ?", (band_id,)).fetchone()
    conn.close()
    return band

def get_band_members(band_id):
    conn = get_db()
    band = conn.execute("SELECT members FROM bands WHERE band_id = ?", (band_id,)).fetchone()
    conn.close()
    if band and band["members"]:
        return [int(m) for m in band["members"].split(",") if m]
    return []

def create_band(leader_id, name):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO bands (name, leader_id, members, slots) VALUES (?, ?, ?, 5)",
            (name, leader_id, str(leader_id))
        )
        band_id = cursor.lastrowid
        conn.execute(
            "UPDATE users SET band_id = ?, band_role = 'leader' WHERE user_id = ?",
            (band_id, leader_id)
        )
        conn.commit()
        return band_id
    except:
        return None
    finally:
        conn.close()

def get_band_by_name(name):
    conn = get_db()
    band = conn.execute("SELECT * FROM bands WHERE name = ?", (name,)).fetchone()
    conn.close()
    return band

def add_member(band_id, user_id):
    conn = get_db()
    members = get_band_members(band_id)
    if user_id not in members:
        members.append(user_id)
        members_str = ",".join(str(m) for m in members)
        conn.execute(
            "UPDATE bands SET members = ? WHERE band_id = ?",
            (members_str, band_id)
        )
        conn.execute(
            "UPDATE users SET band_id = ?, band_role = 'member' WHERE user_id = ?",
            (band_id, user_id)
        )
        conn.commit()
    conn.close()

def remove_member(band_id, user_id):
    conn = get_db()
    members = get_band_members(band_id)
    if user_id in members:
        members.remove(user_id)
        members_str = ",".join(str(m) for m in members) if members else ""
        conn.execute(
            "UPDATE bands SET members = ? WHERE band_id = ?",
            (members_str, band_id)
        )
        conn.execute(
            "UPDATE users SET band_id = 0, band_role = 'member' WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
    conn.close()
    return True

def get_all_bands():
    conn = get_db()
    bands = conn.execute("SELECT * FROM bands ORDER BY fund DESC").fetchall()
    conn.close()
    return bands
