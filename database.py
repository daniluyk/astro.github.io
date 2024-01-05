# database.py
import sqlite3

def add_user(user_id, username, first_name, last_name, birth_date, birth_place):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создание таблицы, если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users
        (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, birth_date TEXT, birth_place TEXT)
    ''')

    # Добавление пользователя в базу данных
    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, birth_date, birth_place)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, birth_date, birth_place))

    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Выборка всех пользователей из базы данных
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()

    # Закрытие соединения
    conn.close()

    # Формирование списка пользователей
    users = []
    for row in rows:
        user = User(row[0], row[1], row[2], row[3], row[4], row[5])
        users.append(user)

    return users

class User:
    def __init__(self, user_id, username, first_name, last_name, birth_date, birth_place):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.birth_place = birth_place

def get_user_info(user_id):
    users = get_all_users()
    for user in users:
        if user.id == user_id:
            return user
    return None

def is_user_registered(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Выполнение запроса
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    data = c.fetchone()

    # Закрытие соединения с базой данных
    conn.close()

    # Если пользователь найден, то функция возвращает True, иначе False
    return data is not None