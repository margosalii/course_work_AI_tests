from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import get_db_connection
from models.authorization_model import Authorization

authorization_bp = Blueprint('authorization', __name__)

@authorization_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        allowed_domains = ['stud.kai.edu.ua', 'host.kai.edu.ua', 'univ.kai.edu.ua', 'repr.kai.edu.ua']
        domain = email.split('@')[-1]

        if domain not in allowed_domains:
            flash('Помилка: Невірний домен!', 'danger')
            return redirect(url_for('authorization.register'))

        if Authorization.email_exists(email):
            flash('Пошта вже існує', 'danger')
            return redirect(url_for('authorization.register'))

        Authorization.register_user(email, password, first_name, last_name)
        flash('Реєстрація успішна!', 'success')
        return redirect(url_for('authorization.login'))

    return render_template('register.html')

@authorization_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Authorization.validate_login(email, password)
        if user:
            session['email'] = user['email']
            session['role'] = user['role']
            session['user_id'] = user['id']
            session['full_name'] = f"{user['first_name']} {user['last_name']}"

            role_routes = {
                'student': 'student.main',
                'host_admin': 'hostel.main',
                'univ_admin': 'university.main',
                'repair_admin': 'repair.main'
            }
            return redirect(url_for(role_routes.get(user['role'], 'authorization.login')))

        flash('Невірна пошта або пароль!', 'danger')
        return redirect(url_for('authorization.login'))

    return render_template('login.html')
