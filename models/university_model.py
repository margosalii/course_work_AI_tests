import sqlite3
from models.database import get_db_connection
from datetime import datetime, timedelta

class University:
    #Отримує оголошення, які стосуються адміністратора університету.
    @staticmethod
    def get_announcements_for_univ_admin():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, content, created_at FROM announcements WHERE role = 'univ_admin' ORDER BY created_at DESC"
        )
        announcements = cursor.fetchall()
        conn.close()
        return announcements

    #Отримує оголошення для вибраних ролей.
    @staticmethod
    def get_announcements_by_role(selected_roles=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        if selected_roles:
            placeholders = ', '.join(['?'] * len(selected_roles))
            cursor.execute(f'SELECT * FROM announcements WHERE role IN ({placeholders}) ORDER BY created_at DESC',
                           selected_roles)
        else:
            cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC')

        announcements = cursor.fetchall()
        conn.close()
        return announcements

    #Видаляє оголошення з бази даних
    @staticmethod
    def delete_announcement(delete_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM announcements WHERE id = ?', (delete_id,))
        conn.commit()
        conn.close()

    #Додає нове оголошення в базу даних.
    @staticmethod
    def add_announcement(title, content, role):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(''' 
                INSERT INTO announcements (title, content, role)
                VALUES (?, ?, ?)
            ''', (title, content, role))
        conn.commit()
        conn.close()

    #Отримує всі заяви з бази даних, разом з електронною поштою користувача.
    @staticmethod
    def get_all_statements():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                SELECT statement.*, users.email
                FROM statement
                JOIN users ON statement.user_id = users.id
                ORDER BY statement.id ASC
            ''')
        statements = cursor.fetchall()
        conn.close()
        return statements

    #Видаляє заяву з бази даних.
    @staticmethod
    def delete_statement(statement_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM statement WHERE id = ?', (statement_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    #Отримує список мешканців гуртожитку
    @staticmethod
    def get_residents_by_dormitory(dormitory=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        if dormitory:
            cursor.execute('''
                    SELECT * FROM residents
                    WHERE dormitory = ?
                    ORDER BY last_name ASC
                ''', (dormitory,))
        else:
            cursor.execute('''
                    SELECT * FROM residents
                    ORDER BY dormitory ASC, last_name ASC
                ''')

        residents = cursor.fetchall()
        conn.close()
        return residents

    #Отримує список усіх гуртожитків.
    @staticmethod
    def get_all_dormitories():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT dormitory FROM residents ORDER BY dormitory ASC')
        dormitories = [row['dormitory'] for row in cursor.fetchall()]
        conn.close()
        return dormitories

    #Отримує всі порушення мешканців гуртожитку.
    @staticmethod
    def get_all_violations():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                SELECT v.id, r.last_name, r.first_name, r.patronymic, v.violation_type, v.description, v.penalty, v.date
                FROM violations v
                JOIN residents r ON v.resident_id = r.id
            ''')

        violations = cursor.fetchall()
        conn.close()
        return violations

    #Отримує інформацію про всіх користувачів.
    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT email, first_name, last_name, role FROM users')
        users = cursor.fetchall()
        conn.close()
        return users

    #Видаляє користувача за його електронною поштою.
    @staticmethod
    def delete_user_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE email = ?', (email,))
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False