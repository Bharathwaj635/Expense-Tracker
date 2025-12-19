import sqlite3

conn = sqlite3.connect("expense.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    description TEXT
)
""")

conn.commit()
conn.close()
print("Database created successfully")
