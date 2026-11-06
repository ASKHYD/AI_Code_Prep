import sqlite3

def check_db():
    conn = sqlite3.connect("coach.db")
    cur = conn.cursor()
    print("ATTEMPTS SCHEMA:")
    for col in cur.execute("PRAGMA table_info(attempts)").fetchall():
        print(col)
    print("\nALL ATTEMPTS:")
    for row in cur.execute("SELECT * FROM attempts").fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    check_db()
