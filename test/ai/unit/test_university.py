import unittest
from unittest.mock import patch, MagicMock
from models.university_model import University


class TestUniversity(unittest.TestCase):

    @patch('models.university_model.get_db_connection')
    def test_get_all_statements_positive(self, mock_get_db_connection):
        """
        Тестує крок 2 (Позитивний сценарій):
        Адміністрація отримує список заяв.
        """
        mock_data = [
            (1, 1, 'Петренко', ...),  # імітація рядка з БД
            (2, 2, 'Іваненко', ...)
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_data

        statements = University.get_all_statements()

        # Перевірки
        mock_cursor.execute.assert_called_with(unittest.mock.ANY)  # Перевірка, що запит було виконано
        self.assertEqual(statements, mock_data)
        mock_conn.close.assert_called_once()

    @patch('models.university_model.get_db_connection')
    def test_delete_statement_positive(self, mock_get_db_connection):
        """
        Тестує крок 2 (Позитивний сценарій):
        Адміністрація видаляє оброблену заяву.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        statement_id = 1

        University.delete_statement(statement_id)

        # Перевірки
        mock_cursor.execute.assert_called_with('DELETE FROM statement WHERE id = ?', (statement_id,))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('models.university_model.get_db_connection')
    def test_delete_statement_negative_db_error(self, mock_get_db_connection):
        """
        Тестує крок 2 (Негативний сценарій):
        Помилка при видаленні заяви.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Імітуємо помилку
        mock_cursor.execute.side_effect = Exception("Test Error")

        statement_id = 1

        # Перевіряємо, що виняток був перехоплений, зробл. rollback і прокинутий далі
        with self.assertRaises(Exception):
            University.delete_statement(statement_id)

        # Перевірки
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('models.university_model.get_db_connection')
    def test_add_announcement_positive(self, mock_get_db_connection):
        """
        Тестує крок 3 (Позитивний сценарій):
        Адміністрація додає оголошення (список на поселення).
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        title = "Списки на поселення"
        content = "Список..."
        role = "student"  # Оголошення для студентів

        University.add_announcement(title, content, role)

        # Перевірки
        mock_cursor.execute.assert_called_with(
            unittest.mock.ANY,
            (title, content, role)
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()