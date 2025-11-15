from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.university_model import University


university_bp = Blueprint('university', __name__)

#головна сторінка
@university_bp.route('/university')
def main():
    announcements = University.get_announcements_for_univ_admin()
    return render_template('university_main.html', announcements=announcements)

#розміщення інформації
@university_bp.route('/university_information', methods=["GET", "POST"])
def university_information():
    # Словник для заміни кодових значень ролей на текстові значення
    role_dict = {
        'student': 'Студенти',
        'hostel_admin': 'Адміністрація гуртожитку',
        'repr_admin': 'Експлуатаційний відділ',
        'univ_admin': 'Адміністрація університету'
    }

    # Отримуємо фільтри з параметрів запиту
    selected_roles = request.args.getlist('role_filter')

    # Виведення оголошень за допомогою моделі
    announcements = University.get_announcements_by_role(selected_roles)

    # Видалення оголошення по id (через POST-запит)
    if request.method == "POST" and 'delete_id' in request.form:
        delete_id = request.form['delete_id']
        University.delete_announcement(delete_id)
        flash("Оголошення успішно видалено!", "success")
        return redirect(url_for('university.university_information'))

    # Додавання нового оголошення
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']  # HTML-редактор
        role = request.form['role']

        if not title or not content or not role:
            flash("Будь ласка, заповніть всі поля!", "danger")
            return redirect(url_for('university.university_information'))

        University.add_announcement(title, content, role)
        flash("Оголошення успішно опубліковано!", "success")
        return redirect(url_for('university.university_information'))

    return render_template('university_information.html', announcements=announcements, role_dict=role_dict)

#заяви на поселення
@university_bp.route('/university_statement', methods=['GET', 'POST'])
def university_statement():
    if request.method == 'POST':
        statement_id = request.form.get('statement_id')
        if statement_id:
            try:
                # Викликаємо метод для видалення заяви
                University.delete_statement(statement_id)
                flash("Заяву успішно оброблено", "success")
            except Exception as e:
                flash("Помилка під час обробки заяви", "danger")
        return redirect(url_for('university.university_statement'))  # перезавантаження сторінки після POST

        # Отримуємо всі заяви
    statements = University.get_all_statements()
    return render_template('university_statement.html', statements=statements)

#мешканці гуртожитків
@university_bp.route('/university_residents')
def university_residents():
    selected_dormitory = request.args.get('dormitory')  # Отримання параметра з GET-запиту

    # Отримуємо мешканців та список гуртожитків
    residents = University.get_residents_by_dormitory(selected_dormitory)
    dormitories = University.get_all_dormitories()

    return render_template(
        'university_residents.html',
        residents=residents,
        dormitories=dormitories,
        selected_dormitory=selected_dormitory
    )

#облік порушень
@university_bp.route('/university_recording_of_violations')
def university_recording_of_violations():
    violations = University.get_all_violations()
    return render_template('university_recording_of_violations.html', violations=violations)

#управління користувачами
@university_bp.route('/university_user_management', methods=['GET', 'POST'])
def university_user_management():
    if request.method == 'POST':
        email_to_delete = request.form.get('email')
        if email_to_delete:
            if University.delete_user_by_email(email_to_delete):
                flash(f'Користувача {email_to_delete} успішно видалено', 'success')
            else:
                flash(f'Помилка: Користувача з email {email_to_delete} не знайдено', 'danger')

    users = University.get_all_users()
    return render_template('university_user_management.html', users=users)

#сторінка вихід
@university_bp.route('/university_exit')
def university_exit():
    session.clear()
    return redirect('http://127.0.0.1:5000/')
