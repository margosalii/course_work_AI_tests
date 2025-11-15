
from models.database import get_db_connection

class Hostel:

    #Отримує оголошення
    @staticmethod
    def get_announcements_by_role(role):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, content, created_at FROM announcements WHERE role = ? ORDER BY created_at DESC",
            (role,)
        )
        announcements = cursor.fetchall()
        conn.close()
        return announcements

    #Отримує е-чергу з інформацією про користувачів, такою як ім'я, прізвище, email та час.
    @staticmethod
    def get_e_queue_with_user_info():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                SELECT e_queue.id, u.first_name, u.last_name, u.email, e_queue.date, e_queue.time
                FROM e_queue
                JOIN users u ON e_queue.user_id = u.id
                ORDER BY e_queue.date, e_queue.time
            ''')

        records = cursor.fetchall()
        conn.close()
        return records

    #Видаляє запис із е-черги за вказаним ID.
    @staticmethod
    def delete_queue_record(queue_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM e_queue WHERE id = ?', (queue_id,))
            conn.commit()
        finally:
            conn.close()

    #Отримує ID користувача за електронною поштою
    @staticmethod
    def find_user_id_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    #Додає нового мешканця на основі переданих даних
    @staticmethod
    def insert_resident(data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO residents (
                user_id, last_name, first_name, patronymic, birth_date, identification_number,
                email, phone_number, faculty, course, group_name, dormitory,
                room_number, residence_period, parents_full_name, parents_phone_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['user_id'], data['last_name'], data['first_name'], data['patronymic'],
            data['birth_date'], data['identification_number'], data['email'],
            data['phone_number'], data['faculty'], data['course'], data['group_name'],
            data['dormitory'], data['room_number'], data['residence_period'],
            data['parents_full_name'], data['parents_phone_number']
        ))
        conn.commit()
        conn.close()

    #Отримує список всіх мешканців або фільтрує за запитом.
    @staticmethod
    def get_residents(search_query=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search_query:
            cursor.execute('''SELECT * FROM residents WHERE last_name LIKE ?''', (f'%{search_query}%',))
        else:
            cursor.execute('SELECT * FROM residents')

        residents = cursor.fetchall()
        conn.close()
        return residents

    #Отримує мешканців, які підлягають виселенню, з можливістю фільтрування за прізвищем.
    @staticmethod
    def get_residents_for_eviction(search_query=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search_query:
            cursor.execute(''' 
                SELECT id, last_name, first_name, patronymic, birth_date, dormitory, room_number, residence_period
                FROM residents
                WHERE last_name LIKE ?
            ''', (f'%{search_query}%',))
        else:
            cursor.execute('''
                SELECT id, last_name, first_name, patronymic, birth_date, dormitory, room_number, residence_period
                FROM residents
            ''')

        residents = cursor.fetchall()
        conn.close()
        return residents

    #Видаляє мешканця з системи та пов'язаний з ним інвентар.
    @staticmethod
    def evict_resident(resident_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Видалення інвентаря
        cursor.execute('''
            DELETE FROM inventory WHERE resident_id = ?
        ''', (resident_id,))

        # Видалення запису про мешканця
        cursor.execute('''
            DELETE FROM residents WHERE id = ?
        ''', (resident_id,))

        conn.commit()
        conn.close()

    #Отримує список всіх мешканців, відсортованих за прізвищем.
    @staticmethod
    def get_all_residents():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, last_name, first_name, patronymic FROM residents ORDER BY last_name')
        residents = cursor.fetchall()
        conn.close()
        return residents

    #Отримує повне ім'я мешканця за його ID. !!!
    @staticmethod
    def get_resident_fullname_by_id(resident_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT last_name, first_name, patronymic FROM residents WHERE id = ?', (resident_id,))
        resident = cursor.fetchone()
        conn.close()
        return resident  # tuple або None

    #Додає порушення для мешканця, з перевіркою на наявність мешканця.
    @staticmethod
    def insert_violation(resident_id, violation_type, description, penalty):
        resident = Hostel.get_resident_fullname_by_id(resident_id)
        if not resident:
            return False, 'Студента не знайдено'

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            last_name, first_name, patronymic = resident
            cursor.execute('''
                INSERT INTO violations (resident_id, violation_type, description, penalty)
                VALUES (?, ?, ?, ?)
            ''', (resident_id, violation_type, description, penalty))
            conn.commit()
            return True, 'Порушення створено'
        except Exception as e:
            return False, f'Помилка при додаванні: {str(e)}'
        finally:
            conn.close()

    #Отримує всі порушення або фільтрує їх за прізвищем.
    @staticmethod
    def get_all_violations(search_query=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if search_query:
                cursor.execute('''
                        SELECT v.id, r.last_name, r.first_name, r.patronymic,
                               v.violation_type, v.description, v.penalty
                        FROM violations v
                        JOIN residents r ON v.resident_id = r.id
                        WHERE r.last_name LIKE ?
                        ORDER BY r.last_name
                    ''', (f"%{search_query}%",))
            else:
                cursor.execute('''
                        SELECT v.id, r.last_name, r.first_name, r.patronymic,
                               v.violation_type, v.description, v.penalty
                        FROM violations v
                        JOIN residents r ON v.resident_id = r.id
                        ORDER BY r.last_name
                    ''')
            return cursor.fetchall()
        finally:
            conn.close()

    #Видаляє порушення за вказаним ID.
    @staticmethod
    def delete_violation_by_id(violation_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM violations WHERE id = ?', (violation_id,))
            conn.commit()
            return True, 'Порушення скасовано'
        except Exception as e:
            conn.rollback()
            return False, f'Помилка при видаленні порушення: {str(e)}'
        finally:
            conn.close()

    #Додає інвентар до мешканця, перевіряючи унікальність інвентарного коду.
    @staticmethod
    def add_inventory(resident_id, inventory_type, inventory_item, inventory_code):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Перевірка унікальності інвентарного коду
            cursor.execute('SELECT 1 FROM inventory WHERE inventory_code = ?', (inventory_code,))
            if cursor.fetchone():
                return False, 'Інвентар з таким кодом вже існує. Спробуйте інший код.'

            # Перевірка, чи існує мешканець
            cursor.execute('SELECT id FROM residents WHERE id = ?', (resident_id,))
            if not cursor.fetchone():
                return False, 'Не знайдено студента з таким ID.'

            # Додавання інвентарю
            cursor.execute('''
                   INSERT INTO inventory (resident_id, inventory_type, inventory_item, inventory_code)
                   VALUES (?, ?, ?, ?)
               ''', (resident_id, inventory_type, inventory_item, inventory_code))

            conn.commit()
            return True, 'Інвентар успішно закріплений за студентом.'
        except Exception as e:
            conn.rollback()
            return False, f'Помилка: {str(e)}'
        finally:
            conn.close()

    #Отримує список інвентарю, фільтруючи за прізвищем чи інвентарним кодом.
    @staticmethod
    def get_inventory_items(last_name_search='', inventory_code_search=''):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = '''
                    SELECT i.id, i.resident_id, i.inventory_type, i.inventory_item, i.inventory_code,
                           r.last_name, r.first_name, r.patronymic
                    FROM inventory i
                    JOIN residents r ON i.resident_id = r.id
                    WHERE 1=1
                '''
            params = []

            if last_name_search:
                query += ' AND r.last_name LIKE ?'
                params.append(f'%{last_name_search}%')

            if inventory_code_search:
                query += ' AND i.inventory_code LIKE ?'
                params.append(f'%{inventory_code_search}%')

            cursor.execute(query, params)
            inventory_items = cursor.fetchall()
            return inventory_items
        finally:
            conn.close()

    #Видаляє інвентар за його інвентарним кодом.
    @staticmethod
    def delete_inventory_by_code(inventory_code):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM inventory WHERE inventory_code = ?', (inventory_code,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    #Отримує всі запити на технічне обслуговування, відсортовані за пріоритетом і датою створення.
    @staticmethod
    def get_all_maintenance_requests():
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                    SELECT m.id, u.first_name, u.last_name, u.email,
                           m.telephone_number, m.dormitory, m.room_number,
                           m.issue_type, m.issue_description, m.priority, m.created_at
                    FROM maintenance m
                    JOIN users u ON m.user_id = u.id
                    ORDER BY m.priority DESC, m.created_at ASC
                ''')
            maintenance_records = cursor.fetchall()
            return maintenance_records
        finally:
            conn.close()

    #Отримує всі завершені звіти по технічному обслуговуванню.
    @staticmethod
    def get_all_completed_maintenance_reports():
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                    SELECT md.id, u.first_name, u.last_name, u.email,
                           m.telephone_number, m.dormitory, m.room_number,
                           m.issue_type, m.issue_description, m.priority,
                           m.created_at, md.completed_at
                    FROM maintenance_done md
                    JOIN maintenance m ON md.maintenance_id = m.id
                    JOIN users u ON m.user_id = u.id
                    ORDER BY md.completed_at DESC
                ''')
            return cursor.fetchall()
        finally:
            conn.close()