from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.repair_model import Repair
repair_bp = Blueprint('repair', __name__)

#головна сторінка
@repair_bp.route('/repair')
def main():
    announcements = Repair.get_announcements_for_repair_admin()
    return render_template('repair_main.html', announcements=announcements)

#технічне обслуговування
@repair_bp.route('/repair_maintenance', methods=['GET', 'POST'])
def repair_maintenance():
    if request.method == 'POST':
        maintenance_id = request.form['maintenance_id']
        Repair.mark_maintenance_as_done(maintenance_id)
        flash('Заявку виконано!', 'success')
        return redirect(url_for('repair.repair_maintenance'))

    maintenance_records = Repair.get_active_maintenance()
    return render_template('repair_maintenance.html', maintenance_records=maintenance_records)

#звіт про технічне обслуговування
@repair_bp.route('/repair_maintenance_reports')
def repair_maintenance_reports():
    maintenance_records = Repair.get_completed_maintenance()
    return render_template('repair_maintenance_reports.html', maintenance_records=maintenance_records)

#сторінка вихід
@repair_bp.route('/repair_exit')
def repair_exit():
    session.clear()
    return redirect('http://127.0.0.1:5000/')

