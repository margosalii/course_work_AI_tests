import unittest
from unittest.mock import patch, MagicMock
from models.authorization_model import Authorization

class TestAuthorization(unittest.TestCase):

    def test_get_role_by_email_student(self):
        """
        Тестує позитивний сценарій:
        коректне визначення ролі 'student'.
        """
        email = "test.user@stud.kai.edu.ua"
        self.assertEqual(Authorization.get_role_by_email(email), 'student')

    def test_get_role_by_email_host_admin(self):
        """
        Тестує позитивний сценарій:
        коректне визначення ролі 'host_admin'.
        """
        email = "admin@host.kai.edu.ua"
        self.assertEqual(Authorization.get_role_by_email(email), 'host_admin')

    def test_get_role_by_email_unknown(self):
        """
        Тестує негативний сценарій (граничний випадок):
        email з невідомим доменом повертає None.
        """
        email = "user@gmail.com"
        self.assertIsNone(Authorization.get_role_by_email(email))

    def test_get_role_by_email_invalid(self):
        """
        Тестує негативний сценарій:
        обробка email без '@'.
        """
        email = "invalid-email"
        # .split('@')[-1] поверне 'invalid-email', .get() поверне None
        self.assertIsNone(Authorization.get_role_by_email(email))

    @patch('models.authorization_model.get_db_connection')
    def test_email_exists_positive(self, mock_get_db_connection):
        """
        Тестує позитивний сценарій:
        перевірка, що email існує.
        """
        # Налаштування моків
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Налаштовуємо, що fetchone() поверне результат (кортеж)
        mock_cursor.fetchone.return_value = (1,)

        result = Authorization.email_exists("exists@stud.kai.edu.ua")

        # Перевірки
        mock_get_db_connection.assert_called_once()
        mock_cursor.execute.assert_called_with("SELECT id FROM users WHERE email = ?", ("exists@stud.kai.edu.ua",))
        mock_conn.close.assert_called_once()
        self.assertTrue(result)

    @patch('models.authorization_model.get_db_connection')
    def test_email_exists_negative(self, mock_get_db_connection):
        """
        Тестує негативний сценарій:
        перевірка, що email не існує.
        """
        # Налаштування моків
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Налаштовуємо, що fetchone() поверне None
        mock_cursor.fetchone.return_value = None

        result = Authorization.email_exists("notexists@stud.kai.edu.ua")

        # Перевірки
        mock_cursor.execute.assert_called_with("SELECT id FROM users WHERE email = ?", ("notexists@stud.kai.edu.ua",))
        self.assertFalse(result)

    @patch('models.authorization_model.get_db_connection')
    @patch('models.authorization_model.Authorization.get_role_by_email')
    def test_register_user_positive(self, mock_get_role, mock_get_db_connection):
        """
        Тестує позитивний сценарій:
        успішна реєстрація користувача.
        """
        # Налаштування моків
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Мок для get_role_by_email
        mock_get_role.return_value = 'student'

        email = "new@stud.kai.edu.ua"
        password = "password123"
        first_name = "Test"
        last_name = "User"

        Authorization.register_user(email, password, first_name, last_name)

        # Перевірки
        mock_get_role.assert_called_with(email)
        mock_cursor.execute.assert_called_once_with(
            unittest.mock.ANY,  # SQL запит
            (email, password, first_name, last_name, 'student')
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('models.authorization_model.get_db_connection')
    def test_validate_login_positive(self, mock_get_db_connection):
        """
        Тестує позитивний сценарій:
        успішна валідація логіну.
        """
        mock_user_row = (1, 'test@stud.kai.edu.ua', 'pass', 'Test', 'User', 'student')

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = mock_user_row

        user = Authorization.validate_login("test@stud.kai.edu.ua", "pass")

        mock_cursor.execute.assert_called_with(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            ("test@stud.kai.edu.ua", "pass")
        )
        self.assertEqual(user, mock_user_row)
        mock_conn.close.assert_called_once()

    @patch('models.authorization_model.get_db_connection')
    def test_validate_login_negative(self, mock_get_db_connection):
        """
        Тестує негативний сценарій:
        неправильний логін або пароль.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None  # Користувача не знайдено

        user = Authorization.validate_login("test@stud.kai.edu.ua", "wrongpass")

        self.assertIsNone(user)
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()