from flask import Blueprint, render_template, redirect, url_for, request, flash, session

from models.hostel_model import Hostel

hostel_bp = Blueprint('hostel', __name__)

#головна сторінка
@hostel_bp.route('/hostel')
def main():
    announcements = Hostel.get_announcements_by_role('hostel_admin')
    return render_template('hostel_main.html', announcements=announcements)

#е-черга
@hostel_bp.route('/hostel_e_queue', methods=['GET', 'POST'])
def hostel_e_queue():
    if request.method == 'POST':
        queue_id = request.form.get('queue_id')
        if queue_id:
            Hostel.delete_queue_record(queue_id)
            flash('Запис успішно видалено!', 'success')
        return redirect(url_for('hostel.hostel_e_queue'))

    queue_records = Hostel.get_e_queue_with_user_info()
    return render_template('hostel_e_queue.html', queue_records=queue_records)

#поселення
@hostel_bp.route('/hostel_settlement', methods=['GET', 'POST'])
def hostel_settlement():
    if request.method == 'POST':
        try:
            # Отримання даних з форми
            last_name = request.form.get('last_name')
            first_name = request.form.get('first_name')
            patronymic = request.form.get('patronymic')
            birth_date = request.form.get('birth_date')
            identification_number = request.form.get('identification_number')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            faculty = request.form.get('faculty')
            course = request.form.get('course')
            group_name = request.form.get('group_name')
            dormitory = request.form.get('dormitory')
            room_number = request.form.get('room_number')
            residence_period = request.form.get('residence_period')
            parents_full_name = request.form.get('parents_full_name')
            parents_phone_number = request.form.get('parents_phone_number')

            # Пошук user_id за email
            user_id = Hostel.find_user_id_by_email(email) or 0

            # Підготовка даних для збереження
            resident_data = {
                'user_id': user_id,
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic,
                'birth_date': birth_date,
                'identification_number': identification_number,
                'email': email,
                'phone_number': phone_number,
                'faculty': faculty,
                'course': course,
                'group_name': group_name,
                'dormitory': dormitory,
                'room_number': room_number,
                'residence_period': residence_period,
                'parents_full_name': parents_full_name,
                'parents_phone_number': parents_phone_number
            }

            # Додавання в базу
            Hostel.insert_resident(resident_data)
            flash(" Студента успішно поселено!", "success")
            return redirect(url_for('hostel.hostel_settlement'))

        except Exception as e:
            flash(f" Помилка при поселенні студента: {str(e)}", "danger")
            return redirect(url_for('hostel.hostel_settlement'))

    return render_template('hostel_settlement.html')

#облік мешканців
@hostel_bp.route('/hostel_residents', methods=['GET', 'POST'])
def hostel_residents():
    search_query = ''
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

    # Отримуємо список мешканців, якщо є запит на пошук, передаємо search_query
    residents = Hostel.get_residents(search_query)

    return render_template('hostel_residents.html', residents=residents, search_query=search_query)

#виселення
@hostel_bp.route('/hostel_eviction', methods=['GET', 'POST'])
def hostel_eviction():
    residents = []
    if request.method == 'POST':
        # Якщо пошук
        if 'last_name_search' in request.form:
            search_query = request.form['last_name_search']
            residents = Hostel.get_residents_for_eviction(search_query)

        # Якщо виселення
        if 'resident_id' in request.form:
            resident_id = request.form['resident_id']
            Hostel.evict_resident(resident_id)
            flash('Студента виселено і всі дані видалено!', 'success')
            return redirect(url_for('hostel.hostel_eviction'))

    # Якщо GET запит або при відкритті сторінки без пошуку
    if not residents:
        residents = Hostel.get_residents_for_eviction()

    return render_template('hostel_eviction.html', residents=residents)

#порушення правил проживання
@hostel_bp.route('/hostel_violation_rules', methods=['GET', 'POST'])
def hostel_violation_rules():
    if request.method == 'POST':
        resident_id = request.form['resident_id']
        violation_type = request.form['violation_type']
        description = request.form['description']
        penalty = request.form['penalty'] if request.form['penalty'] else None

        success, message = Hostel.insert_violation(resident_id, violation_type, description, penalty)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('hostel.hostel_violation_rules'))

    residents = Hostel.get_all_residents()
    return render_template('hostel_violation_rules.html', residents=residents)

#облік порушень
@hostel_bp.route('/hostel_recording_of_violations', methods=['GET', 'POST'])
def hostel_recording_of_violations():
    search_query = ""
    if request.method == 'POST':
        if 'delete_violation' in request.form:
            violation_id = request.form['delete_violation']
            success, message = Hostel.delete_violation_by_id(violation_id)
            flash(message, 'success' if success else 'danger')
            return redirect(url_for('hostel.hostel_recording_of_violations'))
        else:
            search_query = request.form.get('search_query', '').strip()

    violations = Hostel.get_all_violations(search_query)
    return render_template('hostel_recording_of_violations.html', violations=violations, search_query=search_query)

#додати інвентар
@hostel_bp.route('/hostel_add_inventory', methods=['GET', 'POST'])
def hostel_add_inventory():
    if request.method == 'POST':
        resident_id = request.form['resident_id']
        inventory_type = request.form['inventory_type']
        inventory_item = request.form['inventory_item']
        inventory_code = request.form['inventory_code']

        success, message = Hostel.add_inventory(resident_id, inventory_type, inventory_item, inventory_code)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('hostel.hostel_add_inventory'))

    residents = Hostel.get_all_residents()
    return render_template('hostel_add_inventory.html', residents=residents)

#облік інвентарю
@hostel_bp.route('/hostel_inventory_accounting', methods=['GET', 'POST'] )
def hostel_inventory_accounting():
    last_name_search = request.form.get('last_name_search', '').strip()
    inventory_code_search = request.form.get('inventory_code_search', '').strip()

    if request.method == 'POST' and 'inventory_code' in request.form:
        inventory_code = request.form['inventory_code']
        if Hostel.delete_inventory_by_code(inventory_code):
            flash('Інвентар успішно видалено!', 'success')
        else:
            flash('Помилка при видаленні інвентарю.', 'danger')
        return redirect(url_for('hostel.hostel_inventory_accounting'))

    inventory_items = Hostel.get_inventory_items(last_name_search, inventory_code_search)
    return render_template('hostel_inventory_accounting.html', inventory_items=inventory_items)

#технічне обслуговування
@hostel_bp.route('/hostel_maintenance')
def hostel_maintenance():
    maintenance_records = Hostel.get_all_maintenance_requests()
    return render_template('hostel_maintenance.html', maintenance_records=maintenance_records)

#звіти про технічне обслуговування
@hostel_bp.route('/hostel_maintenance_reports')
def hostel_maintenance_reports():
    maintenance_records = Hostel.get_all_completed_maintenance_reports()
    return render_template('hostel_maintenance_reports.html', maintenance_records=maintenance_records)

#сторінка вихід
@hostel_bp.route('/hostel_exit')
def hostel_exit():
    session.clear()
    return redirect('http://127.0.0.1:5000/')




