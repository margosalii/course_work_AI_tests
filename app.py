from flask import Flask, render_template
from controllers.authorization import authorization_bp
from controllers.student import student_bp
from controllers.university import university_bp
from controllers.hostel import hostel_bp
from controllers.repair import repair_bp
from models.database import init_db

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Ініціалізуємо БД
init_db()

# Реєстрація Blueprint'ів
app.register_blueprint(authorization_bp)
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(university_bp, url_prefix='/university')
app.register_blueprint(hostel_bp, url_prefix='/hostel')
app.register_blueprint(repair_bp, url_prefix='/repair')

# Головна сторінка
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
