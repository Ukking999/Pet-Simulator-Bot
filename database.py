import sqlite3

conn = sqlite3.connect("pets.db")
cursor = conn.cursor()

# PET TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    user_id TEXT PRIMARY KEY,
    species TEXT,
    level INTEGER,
    xp INTEGER,
    hunger INTEGER,
    happiness INTEGER,
    energy INTEGER,
    coins INTEGER
)
""")

# INVENTORY TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id TEXT,
    item TEXT,
    quantity INTEGER
)
""")

conn.commit()

def get_pet(user_id):
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_pet(user_id, species):
    cursor.execute("""
    INSERT INTO pets VALUES (?, ?, 1, 0, 50, 50, 50, 100)
    """, (user_id, species))
    conn.commit()

def update_pet(user_id, **kwargs):
    for key, value in kwargs.items():
        cursor.execute(f"UPDATE pets SET {key}=? WHERE user_id=?", (value, user_id))
    conn.commit()

# INVENTORY
def add_item(user_id, item, amount):
    cursor.execute("SELECT quantity FROM inventory WHERE user_id=? AND item=?", (user_id, item))
    data = cursor.fetchone()

    if data:
        cursor.execute("UPDATE inventory SET quantity=? WHERE user_id=? AND item=?",
                       (data[0] + amount, user_id, item))
    else:
        cursor.execute("INSERT INTO inventory VALUES (?, ?, ?)", (user_id, item, amount))
    conn.commit()

def get_inventory(user_id):
    cursor.execute("SELECT item, quantity FROM inventory WHERE user_id=?", (user_id,))
    return cursor.fetchall()

def remove_item(user_id, item, amount):
    cursor.execute("SELECT quantity FROM inventory WHERE user_id=? AND item=?", (user_id, item))
    data = cursor.fetchone()

    if not data or data[0] < amount:
        return False

    new_qty = data[0] - amount
    if new_qty == 0:
        cursor.execute("DELETE FROM inventory WHERE user_id=? AND item=?", (user_id, item))
    else:
        cursor.execute("UPDATE inventory SET quantity=? WHERE user_id=? AND item=?",
                       (new_qty, user_id, item))

    conn.commit()
    return True

def get_all_users():
    # Example for SQLite
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM pets")
    users = cursor.fetchall()

    conn.close()

    return [user[0] for user in users]
