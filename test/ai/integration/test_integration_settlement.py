import unittest
import sqlite3
from unittest.mock import patch, MagicMock

# Імпортуємо ваші класи моделей
from models.authorization_model import Authorization
from models.student_model import Student
from models.university_model import University
from models.hostel_model import Hostel

# --- Дані для тестів ---
USER_DATA_1 = {
    "email": "test.student@stud.kai.edu.ua",
    "password": "password123",
    "first_name": "Петро",
    "last_name": "Петренко"
}
STATEMENT_DATA = {
    "last_name": "Петренко", "first_name": "Петро", "patronymic": "Петрович",
    "birth_date": "2005-01-01", "id_number": "INT_TEST_123",
    "phone": "0501234567", "faculty": "ФІОТ", "course": 2,
    "group_name": "ІП-21", "dormitory": "18", "room_number": "404A"
}
RESIDENT_DATA = {
    "last_name": "Петренко", "first_name": "Петро", "patronymic": "Петрович",
    "birth_date": "2005-01-01", "identification_number": "INT_TEST_123",
    "email": "test.student@stud.kai.edu.ua", "phone_number": "0501234567",
    "faculty": "ФІОТ", "course": 2, "group_name": "ІП-21",
    "dormitory": "18", "room_number": 404, "residence_period": "2025-2026",
    "parents_full_name": "Батько", "parents_phone_number": "050"
}


class TestIntegrationSettlement(unittest.TestCase):

    def setUp(self):
        """
        Налаштування перед кожним тестом.
        1. Створює БД в пам'яті (:memory:).
        2. Створює всі таблиці.
        3. Створює "обгортку" (proxy) для з'єднання.
        4. Патчить 'close()' на обгортці.
        5. Патчить 'get_db_connection', щоб вона повертала обгортку.
        """

        # 1. Створюємо з'єднання з БД в пам'яті
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

        # 2. Ініціалізуємо схему
        try:
            cursor = self.conn.cursor()
            # (Скопійована логіка з init_db)
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (
                                  id
                                  INTEGER
                                  PRIMARY
                                  KEY
                                  AUTOINCREMENT,
                                  email
                                  TEXT
                                  UNIQUE
                                  NOT
                                  NULL,
                                  password
                                  TEXT
                                  NOT
                                  NULL,
                                  first_name
                                  TEXT
                                  NOT
                                  NULL,
                                  last_name
                                  TEXT
                                  NOT
                                  NULL,
                                  role
                                  TEXT
                                  NOT
                                  NULL
                              )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS e_queue
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                user_id
                INTEGER
                NOT
                NULL,
                date
                DATE
                NOT
                NULL,
                time
                TIME
                NOT
                NULL,
                UNIQUE
                              (
                date,
                time
                              ), FOREIGN KEY
                              (
                                  user_id
                              ) REFERENCES users
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS residents
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                user_id
                INTEGER
                NOT
                NULL
                UNIQUE,
                last_name
                TEXT
                NOT
                NULL,
                first_name
                TEXT
                NOT
                NULL,
                patronymic
                TEXT
                NOT
                NULL,
                birth_date
                DATE
                NOT
                NULL,
                identification_number
                TEXT
                NOT
                NULL
                UNIQUE,
                email
                TEXT
                NOT
                NULL
                UNIQUE,
                phone_number
                TEXT
                NOT
                NULL,
                faculty
                TEXT
                NOT
                NULL,
                course
                INTEGER
                NOT
                NULL,
                group_name
                TEXT
                NOT
                NULL,
                dormitory
                TEXT
                NOT
                NULL,
                room_number
                INTEGER
                NOT
                NULL,
                residence_period
                TEXT
                NOT
                NULL,
                parents_full_name
                TEXT
                NOT
                NULL,
                parents_phone_number
                TEXT
                NOT
                NULL,
                FOREIGN
                KEY
                              (
                user_id
                              ) REFERENCES users
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                user_id
                INTEGER
                NOT
                NULL,
                telephone_number
                TEXT
                NOT
                NULL,
                dormitory
                TEXT
                NOT
                NULL,
                room_number
                INTEGER
                NOT
                NULL,
                issue_type
                TEXT
                NOT
                NULL,
                issue_description
                TEXT
                NOT
                NULL,
                priority
                TEXT
                NOT
                NULL,
                created_at
                TIMESTAMP
                DEFAULT
                CURRENT_TIMESTAMP,
                is_done
                BOOLEAN
                DEFAULT
                0,
                FOREIGN
                KEY
                              (
                user_id
                              ) REFERENCES users
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance_done
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                maintenance_id
                INTEGER
                NOT
                NULL,
                completed_at
                TIMESTAMP
                DEFAULT
                CURRENT_TIMESTAMP,
                FOREIGN
                KEY
                              (
                maintenance_id
                              ) REFERENCES maintenance
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS violations
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                resident_id
                INTEGER
                NOT
                NULL,
                violation_type
                TEXT
                NOT
                NULL,
                description
                TEXT
                NOT
                NULL,
                penalty
                TEXT,
                date
                TIMESTAMP
                DEFAULT
                CURRENT_TIMESTAMP,
                FOREIGN
                KEY
                              (
                resident_id
                              ) REFERENCES residents
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                resident_id
                INTEGER
                NOT
                NULL,
                inventory_type
                TEXT
                NOT
                NULL,
                inventory_item
                TEXT
                NOT
                NULL,
                inventory_code
                TEXT
                NOT
                NULL
                UNIQUE,
                FOREIGN
                KEY
                              (
                resident_id
                              ) REFERENCES residents
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS statement
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                user_id
                INTEGER
                NOT
                NULL,
                last_name
                TEXT
                NOT
                NULL,
                first_name
                TEXT
                NOT
                NULL,
                patronymic
                TEXT
                NOT
                NULL,
                birth_date
                TEXT
                NOT
                NULL,
                id_number
                TEXT
                UNIQUE
                NOT
                NULL,
                phone
                TEXT
                NOT
                NULL,
                faculty
                TEXT
                NOT
                NULL,
                course
                INTEGER
                NOT
                NULL,
                group_name
                TEXT
                NOT
                NULL,
                dormitory
                TEXT
                NOT
                NULL,
                room_number
                TEXT
                NOT
                NULL,
                FOREIGN
                KEY
                              (
                user_id
                              ) REFERENCES users
                              (
                                  id
                              )
                )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS announcements
                              (
                                  id
                                  INTEGER
                                  PRIMARY
                                  KEY
                                  AUTOINCREMENT,
                                  title
                                  TEXT
                                  NOT
                                  NULL,
                                  content
                                  TEXT
                                  NOT
                                  NULL,
                                  role
                                  TEXT
                                  NOT
                                  NULL,
                                  created_at
                                  TEXT
                                  DEFAULT
                                  CURRENT_TIMESTAMP
                              )''')
            self.conn.commit()
        except Exception as e:
            self.conn.close()  # Якщо помилка в setUp, закриваємо
            raise e

        # 3. Створюємо "обгортку" (proxy), яка копіює поведінку self.conn
        self.conn_proxy = MagicMock(wraps=self.conn)

        # 4. Перевизначаємо (патчимо) 'close' ТІЛЬКИ на 'обгортці'
        self.conn_proxy.close = MagicMock()  # "Пустушка", яка нічого не робить

        # 5. Налаштовуємо мок, який буде повертати нашу 'обгортку'
        self.mock_db_connection = MagicMock(return_value=self.conn_proxy)

        # 6. Патчимо get_db_connection у всіх моделях
        self.patchers = []
        patch_targets = [
            'models.authorization_model.get_db_connection',
            'models.student_model.get_db_connection',
            'models.university_model.get_db_connection',
            'models.hostel_model.get_db_connection',
            'models.repair_model.get_db_connection'
        ]
        for target in patch_targets:
            try:
                patcher = patch(target, self.mock_db_connection)
                self.patchers.append(patcher)
                patcher.start()
            except (ImportError, ModuleNotFoundError):
                pass  # Ігноруємо

    def tearDown(self):
        """
        Прибирання після кожного тесту.
        """
        # Зупиняємо всі патчі get_db_connection
        for patcher in self.patchers:
            patcher.stop()

        # Тепер безпечно закриваємо СПРАВЖНЄ з'єднання
        self.conn.close()

    # --- Тестові методи ---

    def test_settlement_happy_path(self):
        """
        Сценарій 1: Успішне виконання повного flow ("Happy Path").
        """

        # --- ARRANGE 1 (Створення користувача) ---
        # register_user викличе self.conn_proxy.close() ("пустушку")
        Authorization.register_user(**USER_DATA_1)

        # --- ASSERT (Верифікація) ---
        # self.conn все ще відкритий
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_DATA_1["email"],))
        user_row = cursor.fetchone()
        self.assertIsNotNone(user_row, "Користувач не був створений")
        user_id = user_row["id"]

        full_statement_data = {**STATEMENT_DATA, "user_id": user_id}
        full_resident_data = {**RESIDENT_DATA, "user_id": user_id}

        # --- ACT 1 (Крок 1: Студент подає заяву) ---
        result_submit = Student.submit_statement(**full_statement_data)

        # --- ASSERT 1 ---
        self.assertTrue(result_submit)
        cursor.execute("SELECT * FROM statement WHERE user_id = ?", (user_id,))
        statement_in_db = cursor.fetchone()
        self.assertIsNotNone(statement_in_db)
        self.assertEqual(statement_in_db["id_number"], "INT_TEST_123")

        # --- ACT 2 (Крок 2: Адміністратор читає та видаляє заяву) ---
        all_statements = University.get_all_statements()
        statement_id_to_delete = all_statements[0]["id"]

        University.delete_statement(statement_id_to_delete)

        # --- ASSERT 2 ---
        self.assertEqual(len(all_statements), 1)
        self.assertEqual(all_statements[0]["id_number"], "INT_TEST_123")
        cursor.execute("SELECT * FROM statement WHERE id = ?", (statement_id_to_delete,))
        self.assertIsNone(cursor.fetchone())

        # --- ACT 3 (Крок 4: Адміністратор гуртожитку реєструє мешканця) ---
        Hostel.insert_resident(full_resident_data)

        # --- ASSERT 3 ---
        cursor.execute("SELECT * FROM residents WHERE user_id = ?", (user_id,))
        resident_in_db = cursor.fetchone()
        self.assertIsNotNone(resident_in_db)
        self.assertEqual(resident_in_db["identification_number"], "INT_TEST_123")

    def test_negative_duplicate_statement_id_number(self):
        """
        Сценарій 2.1 (Виняток 1): Спроба подати заяву (submit_statement)
        з `id_number`, який вже існує в таблиці `statement`.
        """

        # --- ARRANGE ---
        Authorization.register_user(**USER_DATA_1)
        Authorization.register_user(
            "ivanov@stud.kai.edu.ua", "pass", "Ivan", "Ivanov"
        )

        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_DATA_1["email"],))
        user_id_1 = cursor.fetchone()["id"]
        cursor.execute("SELECT id FROM users WHERE email = ?", ("ivanov@stud.kai.edu.ua",))
        user_id_2 = cursor.fetchone()["id"]

        statement_1_data = {**STATEMENT_DATA, "user_id": user_id_1, "id_number": "DUPLICATE123"}
        result_1 = Student.submit_statement(**statement_1_data)

        statement_2_data = {**STATEMENT_DATA, "user_id": user_id_2, "id_number": "DUPLICATE123"}

        # --- ACT ---
        result_2 = Student.submit_statement(**statement_2_data)

        # --- ASSERT ---
        self.assertTrue(result_1)
        # Ваш Student.submit_statement має try/except і повертає False
        self.assertFalse(result_2)

        cursor.execute("SELECT COUNT(id) FROM statement WHERE id_number = 'DUPLICATE123'")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_negative_duplicate_resident_id_number(self):
        """
        Сценарій 2.2 (Виняток 4): Спроба зареєструвати мешканця (insert_resident)
        з `identification_number`, який вже існує в `residents`.
        """

        # --- ARRANGE ---
        Authorization.register_user(**USER_DATA_1)
        Authorization.register_user(
            "ivanov@stud.kai.edu.ua", "pass", "Ivan", "Ivanov"
        )

        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_DATA_1["email"],))
        user_id_1 = cursor.fetchone()["id"]
        cursor.execute("SELECT id FROM users WHERE email = ?", ("ivanov@stud.kai.edu.ua",))
        user_id_2 = cursor.fetchone()["id"]

        resident_1_data = {
            **RESIDENT_DATA, "user_id": user_id_1,
            "identification_number": "DUPLICATE987",
            "email": "test.student@stud.kai.edu.ua"
        }
        Hostel.insert_resident(resident_1_data)

        resident_2_data = {
            **RESIDENT_DATA, "user_id": user_id_2,
            "identification_number": "DUPLICATE987",
            "email": "ivanov@stud.kai.edu.ua"
        }

        # --- ACT & ASSERT ---
        # Hostel.insert_resident не має try/except, тому він "прокине" помилку
        with self.assertRaises(sqlite3.IntegrityError):
            Hostel.insert_resident(resident_2_data)

        cursor.execute("SELECT COUNT(id) FROM residents WHERE identification_number = 'DUPLICATE987'")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_negative_insert_resident_incomplete_data(self):
        """
        Сценарій 2.3 (Виняток 3): Спроба викликати `Hostel.insert_resident`
        з неповним словником `data`.
        """

        # --- ARRANGE ---
        Authorization.register_user(**USER_DATA_1)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_DATA_1["email"],))
        user_id_1 = cursor.fetchone()["id"]

        incomplete_data = {'user_id': user_id_1, 'last_name': 'Петренко'}

        # --- ACT & ASSERT ---
        # Ваш Hostel.insert_resident звернеться до data['first_name'] і впаде
        with self.assertRaises(KeyError):
            Hostel.insert_resident(incomplete_data)


if __name__ == '__main__':
    unittest.main()