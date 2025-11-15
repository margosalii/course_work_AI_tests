import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'dormitory.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    #таблиця зареєстрованих користувачів
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    # Таблиця електронної черги
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS e_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,  -- посилання на users
            date DATE NOT NULL,
            time TIME NOT NULL,
            UNIQUE(date, time),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Таблиця мешканців гуртожитків
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,  -- ключ до таблиці users
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            patronymic TEXT NOT NULL,
            birth_date DATE NOT NULL,
            identification_number TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL,
            faculty TEXT NOT NULL,
            course INTEGER NOT NULL,
            group_name TEXT NOT NULL,
            dormitory TEXT NOT NULL,
            room_number INTEGER NOT NULL,
            residence_period TEXT NOT NULL,
            parents_full_name TEXT NOT NULL,
            parents_phone_number TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Таблиця технічного обслуговування
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,  -- зв'язок із мешканцем
            telephone_number TEXT NOT NULL,
            dormitory TEXT NOT NULL,
            room_number INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_done BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Таблиця виконаного технічного обслуговування
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_done (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maintenance_id INTEGER NOT NULL,  -- посилання на maintenance
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maintenance_id) REFERENCES maintenance(id)
        )
    ''')

    #Таблиця порушень правил проживання
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id INTEGER NOT NULL,
            violation_type TEXT NOT NULL,
            description TEXT NOT NULL,
            penalty TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resident_id) REFERENCES residents(id)
        )
    ''')

    # Таблиця обліку інвентарю
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_id INTEGER NOT NULL,
            inventory_type TEXT NOT NULL,
            inventory_item TEXT NOT NULL,
            inventory_code TEXT NOT NULL UNIQUE,
            FOREIGN KEY (resident_id) REFERENCES residents(id)
         )       
    ''')

    #Таблиця заяв на поселення
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, 
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            patronymic TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            id_number TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            faculty TEXT NOT NULL,
            course INTEGER NOT NULL,
            group_name TEXT NOT NULL,
            dormitory TEXT NOT NULL,
            room_number TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    #Таблиця для оголошень
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
