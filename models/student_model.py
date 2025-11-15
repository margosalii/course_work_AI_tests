import sqlite3
from models.database import get_db_connection
from datetime import datetime, timedelta

class Student:

    #Додає нову заяву на поселення в таблицю statement
    @staticmethod
    def submit_statement(user_id, last_name, first_name, patronymic, faculty,
                         birth_date, id_number, phone, course, group_name, dormitory, room_number):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                    INSERT INTO statement (
                        user_id, last_name, first_name, patronymic, birth_date, id_number, phone,
                        faculty, course, group_name, dormitory, room_number
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, last_name, first_name, patronymic, birth_date, id_number,
                      phone, faculty, course, group_name, dormitory, room_number))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] submit_statement: {e}")
            return False
        finally:
            conn.close()

    #Отримує всі оголошення, призначені для студентів, відсортовані за датою створення
    @staticmethod
    def get_announcements_for_students():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT title, content, created_at 
                FROM announcements 
                WHERE role = 'student' 
                ORDER BY created_at DESC
            """)
        announcements = cursor.fetchall()
        conn.close()
        return announcements

    #Функція для створення списку доступних годин з 9 до 17, по 15 хвилин
    @staticmethod
    def get_available_times(date):
        work_hours = []
        start_time = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{date} 17:00", "%Y-%m-%d %H:%M")

        # Додаємо інтервали часу до обіду (до 12:00)
        while start_time < end_time:
            if start_time.time() < datetime.strptime("12:00", "%H:%M").time() or start_time.time() >= datetime.strptime(
                    "13:00", "%H:%M").time():
                work_hours.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=15)

        return work_hours

    # функція для перевірки зайнятості часу
    @staticmethod
    def check_if_time_taken(date, time):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Перевірка на зайнятість часу для конкретної дати
        cursor.execute('''SELECT 1 FROM e_queue WHERE date = ? AND time = ? LIMIT 1''', (date, time))
        result = cursor.fetchone()

        conn.close()

        # Якщо є запис на цей слот, повертаємо True, значить час вже зайнятий
        return result is not None


    #Додає новий запис в електронну чергу
    @staticmethod
    def insert_e_queue_record(user_id, date, time):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO e_queue (user_id, date, time) VALUES (?, ?, ?)',
            (user_id, date, time)
        )
        conn.commit()
        conn.close()

    #Отримує інформацію про користувача за його email
    @staticmethod
    def get_user_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user

    #Отримує інформацію про студента з таблиці residents за email
    @staticmethod
    def get_student_info_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM residents WHERE email = ?", (email,))
        student_info = cursor.fetchone()
        conn.close()
        return student_info

    #Отримує id користувача за його email
    @staticmethod
    def get_user_id_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user['id'] if user else None

    #Отримує всі заявки на технічне обслуговування для студента за його user_id
    @staticmethod
    def get_maintenance_for_student(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM maintenance WHERE user_id = ?''', (user_id,))
        maintenance = cursor.fetchall()
        conn.close()
        return maintenance

    #Отримує всі порушення для студента з таблиці violations
    @staticmethod
    def get_violations_for_student(student_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT violation_type, description, penalty FROM violations WHERE resident_id = ?",
                       (student_id,))
        violations = cursor.fetchall()
        conn.close()
        return violations

    #Отримує весь інвентар, закріплений за студентом, з таблиці inventory
    @staticmethod
    def get_inventory_for_student(student_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT inventory_type, inventory_item, inventory_code FROM inventory WHERE resident_id = ?",
                       (student_id,))
        inventory = cursor.fetchall()
        conn.close()
        return inventory

    #Створює нову заявку на технічне обслуговування
    @staticmethod
    def submit_maintenance_request(user_id, telephone_number, dormitory, room_number, issue_type, issue_description,
                                   priority):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                    INSERT INTO maintenance (
                        user_id, telephone_number, dormitory, room_number, issue_type, issue_description, priority
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, telephone_number, dormitory, room_number, issue_type, issue_description, priority))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB ERROR] submit_maintenance_request: {e}")
            return False
        finally:
            conn.close()

