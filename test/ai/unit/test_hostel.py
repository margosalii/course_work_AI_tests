import unittest
import sqlite3
from unittest.mock import patch, MagicMock
from models.hostel_model import Hostel


class TestHostel(unittest.TestCase):

    @patch('models.hostel_model.get_db_connection')
    def test_insert_resident_positive(self, mock_get_db_connection):
        """
        Тестує крок 4 (Позитивний сценарій):
        Адміністратор гуртожитку успішно реєструє мешканця.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        resident_data = {
            'user_id': 1, 'last_name': 'Петренко', 'first_name': 'Петро',
            'patronymic': 'Петрович', 'birth_date': '2005-01-01',
            'identification_number': '12345678', 'email': 'petrenko@stud.kai.edu.ua',
            'phone_number': '0991234567', 'faculty': 'ФІОТ', 'course': 2,
            'group_name': 'ІП-11', 'dormitory': '18', 'room_number': 101,
            'residence_period': '2025-2026', 'parents_full_name': 'Батько',
            'parents_phone_number': '050'
        }

        Hostel.insert_resident(resident_data)

        mock_cursor.execute.assert_called_once_with(
            unittest.mock.ANY,
            tuple(resident_data.values())
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('models.hostel_model.get_db_connection')
    def test_insert_resident_negative_incomplete_data(self, mock_get_db_connection):
        """
        Тестує Виняток 3 (Негативний сценарій):
        Адміністратор гуртожитку вводить не всі дані.
        """
        # Arrange: Налаштовуємо моки
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        incomplete_data = {
            'user_id': 1, 'last_name': 'Петренко'
        }

        # Act & Assert
        # Перевіряємо, що код кидає KeyError
        with self.assertRaises(KeyError):
            Hostel.insert_resident(incomplete_data)

        # Assertions
        # Перевіряємо, що код ВСТИГ підключитися до БД...
        mock_get_db_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_not_called()
        mock_conn.close.assert_not_called()  # ...і не встиг закрити з'єднання

    # Шлях до ..._model
    @patch('models.hostel_model.get_db_connection')
    def test_insert_resident_negative_db_error(self, mock_get_db_connection):
        """
        Тестує Виняток 4 (Негативний сценарій):
        Студент не був внесений до БД (помилка БД).
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("DB integrity error")

        resident_data = {
            'user_id': 1, 'last_name': 'Петренко', 'first_name': 'Петро',
            'patronymic': 'Петрович', 'birth_date': '2005-01-01',
            'identification_number': '12345678', 'email': 'petrenko@stud.kai.edu.ua',
            'phone_number': '0991234567', 'faculty': 'ФІОТ', 'course': 2,
            'group_name': 'ІП-11', 'dormitory': '18', 'room_number': 101,
            'residence_period': '2025-2026', 'parents_full_name': 'Батько',
            'parents_phone_number': '050'
        }

        with self.assertRaises(sqlite3.Error):
            Hostel.insert_resident(resident_data)

        mock_conn.commit.assert_not_called()
        mock_conn.close.assert_not_called()


if __name__ == '__main__':
    unittest.main()