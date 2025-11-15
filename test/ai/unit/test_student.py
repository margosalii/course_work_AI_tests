import unittest
import sqlite3
from unittest.mock import patch, MagicMock
from models.student_model import Student


class TestStudent(unittest.TestCase):

    @patch('models.student_model.get_db_connection')
    def test_submit_statement_positive(self, mock_get_db_connection):
        """
        Тестує крок 1 (Позитивний сценарій):
        Успішна подача заяви студентом.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        statement_data = {
            'user_id': 1, 'last_name': 'Петренко', 'first_name': 'Петро',
            'patronymic': 'Петрович', 'birth_date': '2005-01-01',
            'id_number': '12345678', 'phone': '0991234567', 'faculty': 'ФІОТ',
            'course': 2, 'group_name': 'ІП-11', 'dormitory': '18',
            'room_number': '101'
        }

        result = Student.submit_statement(**statement_data)

        # Перевірки
        mock_get_db_connection.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            unittest.mock.ANY,  # SQL запит
            tuple(statement_data.values())
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        self.assertTrue(result)

    @patch('models.student_model.get_db_connection')
    def test_submit_statement_negative_db_error(self, mock_get_db_connection):
        """
        Тестує Виняток 1 (Негативний сценарій):
        Помилка при записі в базу даних (наприклад, UNIQUE constraint).
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Test DB Error")

        statement_data = {
            'user_id': 1, 'last_name': 'Петренко', 'first_name': 'Петро',
            'patronymic': 'Петрович', 'birth_date': '2005-01-01',
            'id_number': '12345678', 'phone': '0991234567', 'faculty': 'ФІОТ',
            'course': 2, 'group_name': 'ІП-11', 'dormitory': '18',
            'room_number': '101'
        }

        result = Student.submit_statement(**statement_data)

        # Перевірки
        mock_conn.commit.assert_not_called()

        mock_conn.close.assert_called_once()

        self.assertFalse(result)

    def test_submit_statement_missing_fields(self):
        """
        Тестує Виняток 2 (Негативний сценарій):
        Не всі поля заповнені (помилка на рівні Python).
        """
        with self.assertRaises(TypeError):
            Student.submit_statement(user_id=1, last_name='Петренко')


if __name__ == '__main__':
    unittest.main()