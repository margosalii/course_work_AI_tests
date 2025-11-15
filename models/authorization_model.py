from models.database import get_db_connection

class Authorization:
    #Визначає роль користувача на основі домену його email.
    @staticmethod
    def get_role_by_email(email):
        role_mapping = {
            'stud.kai.edu.ua': 'student',
            'host.kai.edu.ua': 'host_admin',
            'univ.kai.edu.ua': 'univ_admin',
            'repr.kai.edu.ua': 'repair_admin'
        }
        domain = email.split('@')[-1]
        return role_mapping.get(domain)

    #Перевіряє, чи існує користувач з певним email в базі даних.
    @staticmethod
    def email_exists(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        return user is not None

    #Реєструє нового користувача в базі даних.
    @staticmethod
    def register_user(email, password, first_name, last_name):
        role = Authorization.get_role_by_email(email)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO users (email, password, first_name, last_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password, first_name, last_name, role))
        conn.commit()
        conn.close()

    #Перевіряє правильність комбінації email і пароля для авторизації користувача.
    @staticmethod
    def validate_login(email, password):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cur.fetchone()
        conn.close()

        return user