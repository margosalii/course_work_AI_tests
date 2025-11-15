from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import get_db_connection
from datetime import datetime, timedelta
from models.student_model import Student


student_bp = Blueprint('student', __name__)

#головна сторінка
@student_bp.route('/student')
def main():
    announcements = Student.get_announcements_for_students()
    return render_template('student_main.html', announcements=announcements)

#сторінка заява на поселення
@student_bp.route('/student_statement', methods=["GET", "POST"])
def student_statement():
    email = session.get('email')
    if not email:
        flash("Сесія завершена. Увійдіть ще раз.", "danger")
        return redirect(url_for('authorization.login'))

    if request.method == 'POST':
        # Отримуємо всі дані з форми, в тому числі факультет
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        patronymic = request.form.get('patronymic')
        faculty = request.form.get('faculty')  # Додаємо отримання факультету
        birth_date = request.form.get('birth_date')
        id_number = request.form.get('id_number')
        phone = request.form.get('phone')
        course = request.form.get('course')
        group_name = request.form.get('group_name')
        dormitory = request.form.get('dormitory')
        room_number = request.form.get('room_number')

        # Перевіряємо, чи всі необхідні поля заповнені
        if not all([last_name, first_name, patronymic, faculty, birth_date, id_number, phone, course, group_name,
                    dormitory, room_number]):
            flash("Будь ласка, заповніть всі поля.", "danger")
            return redirect(url_for('student.student_statement'))

        # Отримуємо user_id з email за допомогою методу get_user_by_email
        user = Student.get_user_by_email(email)
        if not user:
            flash("Користувача не знайдено в системі.", "danger")
            return redirect(url_for('authorization.login'))

        user_id = user['id']  # Використовуємо id користувача

        # Зберігаємо заяву в базу
        success = Student.submit_statement(  # Викликаємо метод класу Student
            user_id, last_name, first_name, patronymic,
            faculty, birth_date, id_number, phone, course, group_name, dormitory, room_number
        )

        if success:
            flash("Заява успішно подана!", "success")
        else:
            flash("Помилка при поданні заяви.", "danger")
        return redirect(url_for('student.student_statement'))

    return render_template("student_statement.html")

#сторінка е-черга
@student_bp.route('/student_e_queue', methods=['GET', 'POST'])
def student_e_queue():
    # Отримуємо email з сесії
    email = session.get('email')
    if not email:
        flash("Сесія завершена. Увійдіть ще раз.", "danger")
        return redirect(url_for('authorization.login'))

    # Отримуємо користувача за email
    user = Student.get_user_by_email(email)
    if not user:
        flash("Користувач не знайдений.", "danger")
        return redirect(url_for('authorization.login'))

    user_id = user['id']

    # Отримуємо поточну дату або дату з параметрів запиту
    selected_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))

    # Отримуємо доступні часи для вибраної дати
    available_times = Student.get_available_times(selected_date)

    # Дані форми
    form_data = {
        "date": selected_date,
        "time": ""
    }

    if request.method == 'POST':
        form_data["time"] = request.form['time']

        # Перевірка чи вибраний слот вже зайнятий
        if Student.check_if_time_taken(selected_date, form_data["time"]):
            flash("Обраний час вже зайнятий. Оберіть, будь ласка, інший", "danger")
        else:
            # Додаємо новий запис у базу даних
            Student.insert_e_queue_record(user_id, selected_date, form_data["time"])
            flash("Ви успішно записалися в електронну чергу!", "success")
            form_data = {  # Очищаємо форму після успішної реєстрації
                "date": selected_date,
                "time": ""
            }

    return render_template('student_e_queue.html',
                           available_times=available_times,
                           selected_date=selected_date,
                           form_data=form_data)

#сторінка е-перепустка
@student_bp.route('/student_e_pass')
def student_e_pass():
    return render_template('student_e_pass.html')

#сторінка інформація
@student_bp.route('/student_information', methods=['GET', 'POST'])
def student_information():
    email = session.get('email')  # Отримуємо email зі сесії
    if not email:
        flash("Ви не авторизовані!", "danger")
        return redirect(url_for('authorization.login'))

    # отримуємо інформацію про студента
    student_info = Student.get_student_info_by_email(email)

    # отримуємо ID користувача з таблиці users
    user_id = Student.get_user_id_by_email(email)

    maintenance = []
    violations = []
    inventory = []

    if user_id:
        maintenance = Student.get_maintenance_for_student(user_id)
    if student_info:
        student_id = student_info['id']
        violations = Student.get_violations_for_student(student_id)
        inventory = Student.get_inventory_for_student(student_id)

    return render_template('student_information.html',
                            student_info=student_info,
                            maintenance=maintenance,
                            violations=violations,
                            inventory=inventory)

#сторінка технічне обслуговування
@student_bp.route('/student_maintenance', methods=['GET', 'POST'])
def student_maintenance():
    email = session.get('email')
    if not email:
        flash("Сесія завершена. Увійдіть ще раз.", "danger")
        return redirect(url_for('authorization.login'))

    # Отримуємо дані користувача за email
    user = Student.get_user_by_email(email)
    if not user:
        flash("Користувача не знайдено в системі.", "danger")
        return redirect(url_for('authorization.login'))

    user_id = user['id']

    if request.method == 'POST':
        telephone_number = request.form['telephone_number']
        dormitory = request.form['dormitory']
        room_number = request.form['room_number']
        issue_type = request.form['issue_type']
        issue_description = request.form['issue_description']
        priority = request.form['priority']

        # Перевірки на порожні поля
        if not all([telephone_number, dormitory, room_number, issue_type, issue_description, priority]):
            flash("Будь ласка, заповніть всі поля.", "danger")
            return redirect(url_for('student.student_maintenance'))

        # Перевірка номера кімнати (має бути додатнім числом)
        try:
            room_number = int(room_number)
            if room_number <= 0:
                flash("Номер кімнати має бути додатнім числом.", "danger")
                return redirect(url_for('student.student_maintenance'))
        except ValueError:
            flash("Номер кімнати має бути цілим числом.", "danger")
            return redirect(url_for('student.student_maintenance'))

        # Викликаємо метод для вставлення заяви на технічне обслуговування
        if Student.submit_maintenance_request(user_id, telephone_number, dormitory, room_number, issue_type,
                                              issue_description, priority):
            flash('Ваша заявка на технічне обслуговування успішно подана!', 'success')
        else:
            flash('Сталася помилка при подачі заявки на технічне обслуговування.', 'danger')

        return redirect(url_for('student.student_maintenance'))

    return render_template('student_maintenance.html', user=user)

#сторінка вихід
@student_bp.route('/student_exit')
def student_exit():
    session.clear()
    return redirect('http://127.0.0.1:5000/')






