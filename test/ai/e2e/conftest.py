import pytest
import requests
import os
import models.database  # Імпортуємо для доступу до DB_PATH
from models.authorization_model import Authorization
from models.university_model import University  # Потрібен для очищення

# --- Налаштування ---
BASE_URL = "http://127.0.0.1:5000"  # Адреса вашого запущеного Flask-сервера

# --- Тестові Користувачі (будуть тимчасово створені) ---
# Використовуйте унікальні email, щоб не конфліктувати з реальними даними
STUDENT_USER = {"email": "e2e_test_student@stud.kai.edu.ua", "password": "e2epass"}
UNIV_ADMIN_USER = {"email": "e2e_test_admin@univ.kai.edu.ua", "password": "e2epass"}
HOSTEL_ADMIN_USER = {"email": "e2e_test_hostel@host.kai.edu.ua", "password": "e2epass"}
ALL_TEST_USERS = [STUDENT_USER, UNIV_ADMIN_USER, HOSTEL_ADMIN_USER]


@pytest.fixture(scope="session", autouse=True)
def setup_test_users_in_real_db():
    """
    Фікстура, що виконується ОДИН РАЗ за сесію (session scope).

    1. "Вручну" встановлює DB_PATH для pytest-процесу на dormitory.db.
    2. Створює тестових користувачів у dormitory.db.
    3. 'yield' для виконання тестів.
    4. Видаляє тестових користувачів з dormitory.db після завершення.
    5. Відновлює оригінальний DB_PATH.
    """

    # --- 1. Налаштування шляху до БД (Ручна підміна) ---

    # Припускаємо, що conftest.py лежить у '.../dormitory_management1/test/ai/e2e/'
    # Нам потрібно піднятися на 4 рівні, щоб потрапити у корінь 'dormitory_management1'
    # і потім спуститися в 'models/dormitory.db'
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    real_db_path = os.path.join(base_dir, 'models', 'dormitory.db')

    # Альтернативна перевірка, якщо структура інша
    if not os.path.exists(real_db_path):
        # Можливо, 'test' лежить у корені поруч з 'models'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        real_db_path = os.path.join(base_dir, '..', 'models', 'dormitory.db')

        if not os.path.exists(real_db_path):
            pytest.fail(
                f"Не вдалося знайти реальну БД 'dormitory.db'. "
                f"Перевірений шлях: {real_db_path}. "
                "Будь ласка, перевірте шлях у conftest.py."
            )

    # Зберігаємо оригінальний шлях, щоб відновити його в кінці
    original_db_path = models.database.DB_PATH

    # Встановлюємо потрібний шлях
    models.database.DB_PATH = real_db_path

    # --- 2. Створення тестових користувачів ---
    print("\n[E2E Setup] Створення тестових користувачів у dormitory.db...")
    try:
        for user in ALL_TEST_USERS:
            # Перевіряємо, чи користувач вже не існує (від минулого прогону)
            if not Authorization.email_exists(user["email"]):
                Authorization.register_user(
                    email=user["email"],
                    password=user["password"],
                    first_name="E2E_Test",
                    last_name=user["email"].split('@')[0]
                )
    except Exception as e:
        pytest.fail(f"[E2E Setup] Помилка створення користувачів: {e}. Перевірте підключення до БД.")

    yield  # Тести виконуються тут

    # --- 4. Прибирання (Teardown) ---
    print("\n[E2E Teardown] Видалення тестових користувачів...")
    try:
        # Переконуємось, що DB_PATH все ще правильний
        models.database.DB_PATH = real_db_path
        for user in ALL_TEST_USERS:
            University.delete_user_by_email(user["email"])
    except Exception as e:
        print(f"[E2E Teardown] Помилка видалення користувачів: {e}")

    # Відновлюємо оригінальний шлях до БД
    models.database.DB_PATH = original_db_path


@pytest.fixture(scope="function")  # function scope
def auth_session():
    """
    Фабрика-фікстура для автентифікації.
    (Тепер буде використовувати користувачів, створених у setup_test_users_in_real_db)
    """

    def _get_session(user_type):
        if user_type == "student":
            creds = STUDENT_USER
        elif user_type == "univ_admin":
            creds = UNIV_ADMIN_USER
        elif user_type == "hostel_admin":
            creds = HOSTEL_ADMIN_USER
        else:
            raise ValueError("Unknown user type")

        client = requests.Session()
        login_payload = {"email": creds["email"], "password": creds["password"]}

        try:
            r = client.post(f"{BASE_URL}/login", data=login_payload, timeout=5)
            r.raise_for_status()  # Викличе помилку, якщо логін невдалий
        except requests.exceptions.ConnectionError:
            pytest.fail(
                f"НЕ ВДАЛОСЯ ПІДКЛЮЧИТИСЯ ДО {BASE_URL}. "
                "Переконайтеся, що ваш веб-сервер (Flask) запущено."
            )
        except requests.exceptions.HTTPError as e:
            pytest.fail(
                f"Помилка E2E логіну для {user_type} ({creds['email']}): "
                f"{e.response.status_code}. "
                "Сервер не зміг автентифікувати тестового користувача."
            )

        return client

    return _get_session