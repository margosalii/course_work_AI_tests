import pytest
import requests
import time
from models.database import get_db_connection  # Потрібен для очищення
from models.university_model import University  # Потрібен для очищення
from models.hostel_model import Hostel  # Потрібен для очищення

# Адреса сервера
BASE_URL = "http://127.0.0.1:5000"

# Робимо тестові дані унікальними для кожного запуску
UNIQUE_ID = f"e2e_test_{int(time.time())}"

STATEMENT_DATA = {
    "last_name": "ПетренкоE2E", "first_name": "ПетроE2E", "patronymic": "ПетровичE2E",
    "birth_date": "2005-01-01", "id_number": UNIQUE_ID,  # Унікальний ID
    "phone": "0501234567", "faculty": "ФІОТ", "course": 2,
    "group_name": "ІП-21", "dormitory": "18", "room_number": "404A"
}

RESIDENT_DATA = {
    "last_name": "ПетренкоE2E", "first_name": "ПетроE2E", "patronymic": "ПетровичE2E",
    "birth_date": "2005-01-01", "identification_number": UNIQUE_ID,  # Той самий ID
    "email": "e2e_test_student@stud.kai.edu.ua",  # Email тестового студента
    "phone_number": "0501234567", "faculty": "ФІОТ", "course": 2,
    "group_name": "ІП-21", "dormitory": "18", "room_number": 404,
    "residence_period": "2025-2026", "parents_full_name": "Петренко Петро Батькович",
    "parents_phone_number": "0509876543"
}


@pytest.fixture(scope="function")
def cleanup_data(setup_test_users_in_real_db):
    """
    Ця фікстура гарантує очищення даних (заяв, мешканців),
    створених під час тесту.
    Вона автоматично викликає 'setup_test_users_in_real_db' (яка є session-scoped).
    """
    yield  # Тест виконується тут

    # --- Прибирання після тесту (function scope) ---
    print(f"\n[E2E Cleanup] Очищення даних для ID: {UNIQUE_ID}...")
    try:
        # Використовуємо моделі, щоб напряму видалити дані з dormitory.db
        # (Наш pytest-процес має правильний DB_PATH завдяки 'setup_test_users_in_real_db')

        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Знайти мешканця в БД (через модель) та видалити
        # Треба видаляти мешканця ПЕРШИМ
        cursor.execute("SELECT id FROM residents WHERE identification_number = ?", (UNIQUE_ID,))
        resident = cursor.fetchone()
        if resident:
            Hostel.evict_resident(resident["id"])  # evict_resident видаляє і мешканця, і інвентар
            print(f"  - Мешканець {resident['id']} (ID: {UNIQUE_ID}) видалений.")

        # 2. Знайти заяву в БД (через модель) та видалити
        cursor.execute("SELECT id FROM statement WHERE id_number = ?", (UNIQUE_ID,))
        statement = cursor.fetchone()
        if statement:
            University.delete_statement(statement["id"])
            print(f"  - Заява {statement['id']} (ID: {UNIQUE_ID}) видалена.")

        conn.close()

    except Exception as e:
        print(f"[E2E Cleanup] Помилка очищення: {e}")


def test_e2e_settlement_happy_path(auth_session, cleanup_data):
    """
    Сценарій 1: Happy Path - повний успішний цикл поселення.
    (Фікстура 'cleanup_data' автоматично подбає про очищення)
    """

    # === Крок 1 і 2: Студент логіниться і подає заяву ===
    student_client = auth_session("student")

    r_statement = student_client.post(
        f"{BASE_URL}/student/student_statement",
        data=STATEMENT_DATA
    )
    # Припущення: ваш API повертає 200 (OK) або 302 (Redirect)
    assert r_statement.status_code in [200, 302], \
        f"Очікувався 200/302, але отримано {r_statement.status_code} при подачі заяви"

    # === Крок 3 і 4: Адмін університету логіниться і читає заяву ===
    univ_admin_client = auth_session("univ_admin")

    r_get_statements = univ_admin_client.get(f"{BASE_URL}/university/university_statement")

    assert r_get_statements.status_code == 200, \
        f"Очікувався 200, але отримано {r_get_statements.status_code} при отриманні заяв"

    # Ваш роут повертає HTML, тому ми не можемо перевірити JSON.
    # Ми перевіримо вміст бази даних напряму, щоб отримати ID заяви.
    statement_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM statement WHERE id_number = ?", (UNIQUE_ID,))
        statement_row = cursor.fetchone()
        assert statement_row is not None, f"Заява {UNIQUE_ID} не була створена в БД"
        statement_id = statement_row["id"]
        conn.close()
    except Exception as e:
        pytest.fail(f"Помилка перевірки БД: {e}")

    # === Крок 5: Адмін університету видаляє (затверджує) заяву ===

    r_delete = univ_admin_client.post(
        f"{BASE_URL}/university/university_statement",
        data={"statement_id": statement_id}
    )
    assert r_delete.status_code in [200, 302], \
        f"Очікувався 200/302, але отримано {r_delete.status_code} при видаленні заяви"

    # === Крок 6 і 7: Адмін гуртожитку логіниться і реєструє мешканця ===
    hostel_admin_client = auth_session("hostel_admin")

    r_create_resident = hostel_admin_client.post(
        f"{BASE_URL}/hostel/hostel_settlement",
        data=RESIDENT_DATA
    )
    assert r_create_resident.status_code in [200, 302], \
        f"Очікувався 200/302, але отримано {r_create_resident.status_code} при створенні мешканця"

    # === Крок 8: Верифікація ===
    # Перевіряємо напряму в БД
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM residents WHERE identification_number = ?", (UNIQUE_ID,))
    resident_row = cursor.fetchone()
    conn.close()

    assert resident_row is not None, f"Мешканець {UNIQUE_ID} не був створений в БД"
    assert resident_row["email"] == "e2e_test_student@stud.kai.edu.ua"


def test_error_incomplete_statement(auth_session, cleanup_data):
    """
    Сценарій 3: ER1.2 (Неповні дані заяви).
    """
    client = auth_session("student")

    incomplete_data = {**STATEMENT_DATA}
    del incomplete_data["id_number"]  # Видаляємо обов'язкове поле

    r = client.post(
        f"{BASE_URL}/student/student_statement",
        data=incomplete_data,
        allow_redirects = False
    )

    # Ваш контролер робить redirect (302), якщо поля не заповнені.
    assert r.status_code == 302, \
        f"Очікувалася помилка 302 (redirect), але отримано {r.status_code}"