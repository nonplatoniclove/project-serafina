import sqlite3
import hashlib

def init_db():
    # Создаем подключение к базе (файл serafina_users.db создастся сам)
    conn = sqlite3.connect("serafina_users.db")
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Вспомогательная функция для добавления пользователя с хешированием
    def add_user(username, password, role):
        # Хешируем пароль через SHA-256
        h = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                           (username, h, role))
            print(f"User {username} ({role}) added successfully.")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists.")

    # Добавляем твои данные
    add_user("Subaru", "0000", "admin")
    add_user("Moonveil04", "844962529", "tester")
    add_user("Tester", "test", "tester")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()