from models.database import get_db_connection

class Repair:

    #Отримує оголошення, які стосуються експлуатаційного відділу.
    @staticmethod
    def get_announcements_for_repair_admin():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                SELECT title, content, created_at 
                FROM announcements 
                WHERE role = 'repr_admin' 
                ORDER BY created_at DESC
            ''')
        announcements = cursor.fetchall()
        conn.close()
        return announcements

    #Отримує всі активні заявки на технічне обслуговування, які ще не завершено.
    @staticmethod
    def get_active_maintenance():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT m.*, u.first_name, u.last_name, u.email
            FROM maintenance m
            JOIN users u ON m.user_id = u.id
            WHERE m.is_done = 0
            ORDER BY priority DESC, created_at ASC
        ''')
        records = cur.fetchall()
        conn.close()
        return records

    #Отримує всі завершені заявки на технічне обслуговування, що вже виконані.
    @staticmethod
    def get_completed_maintenance():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT m.*, u.first_name, u.last_name, u.email, d.completed_at
            FROM maintenance_done d
            JOIN maintenance m ON d.maintenance_id = m.id
            JOIN users u ON m.user_id = u.id
            ORDER BY d.completed_at DESC
        ''')
        records = cur.fetchall()
        conn.close()
        return records

    #Оновлює статус заявки на технічне обслуговування, позначаючи її як завершену, та додає запис до таблиці maintenance_done.
    @staticmethod
    def mark_maintenance_as_done(maintenance_id):
        conn = get_db_connection()
        cur = conn.cursor()
        # Оновлюємо статус заявки
        cur.execute('UPDATE maintenance SET is_done = 1 WHERE id = ?', (maintenance_id,))
        # Додаємо запис про завершення
        cur.execute('INSERT INTO maintenance_done (maintenance_id) VALUES (?)', (maintenance_id,))
        conn.commit()
        conn.close()