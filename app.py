# -*- coding: utf-8 -*-
import pandas as pd
import qrcode
import os
from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, read_students, read_disciplines, read_admins, add_student, add_discipline, add_admin, add_log_entry, update_statistics, read_logs, get_total_users, get_students_by_course, get_students_with_disciplines, get_popular_disciplines, get_logins_by_period, get_admin_activity

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = 'database.xlsx'

# Инициализация базы данных
init_db()

# Создаем директорию для хранения QR-кодов, если она не существует
QR_CODES_DIR = 'static/qr_codes'
if not os.path.exists(QR_CODES_DIR):
    os.makedirs(QR_CODES_DIR)

def save_to_excel(df, sheet_name):
    """Функция для сохранения данных в Excel файл."""
    try:
        with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    except Exception as e:
        return f"Ошибка сохранения в Excel: {str(e)}"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        students = read_students()
        if isinstance(students, str):
            return students  # Возвращаем сообщение об ошибке
        student = students[students['student_id'].astype(str) == student_id]
        if not student.empty:
            session['student_id'] = student_id
            add_log_entry(student_id, 'student', 'login')
            return redirect(url_for('select_disciplines'))
        else:
            return 'Неверный номер студенческого билета'
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_full_name = request.form['admin_full_name']
        admin_id = request.form['admin_id']
        admins = read_admins()
        if isinstance(admins, str):
            return admins  # Возвращаем сообщение об ошибке
        admin = admins[(admins['full_name'] == admin_full_name) & (admins['admin_id'].astype(str) == admin_id)]
        if not admin.empty:
            session['admin_id'] = admin_id
            session['role'] = int(admin['role'].values[0])
            add_log_entry(admin_id, 'admin', 'login')
            if session['role'] == 1:
                return redirect(url_for('admin'))
            elif session['role'] == 2:
                return redirect(url_for('admin2'))
        else:
            return 'Данного администратора нет'
    return render_template('admin_login.html')

@app.route('/select_disciplines', methods=['GET', 'POST'])
def select_disciplines():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    success = False
    students = read_students()
    if isinstance(students, str):
        return students  # Возвращаем сообщение об ошибке
    student = students[students['student_id'].astype(str) == session['student_id']].iloc[0]
    student_course = student['course']

    if request.method == 'POST':
        selected_disciplines = request.form.getlist('disciplines')
        valid_disciplines = read_disciplines()
        if isinstance(valid_disciplines, str):
            return valid_disciplines  # Возвращаем сообщение об ошибке
        valid_disciplines = valid_disciplines[valid_disciplines['course'].astype(str) == str(student_course)]
        valid_discipline_ids = valid_disciplines['discipline_id'].values

        for discipline in selected_disciplines:
            if discipline not in valid_discipline_ids:
                return render_template('error.html', message='Выбранная дисциплина не соответствует вашему курсу')

        students.loc[students['student_id'] == session['student_id'], 'selected_disciplines'] = ','.join(selected_disciplines)
        save_error = save_to_excel(students, 'students')
        if save_error:
            return save_error
        success = True
        add_log_entry(session['student_id'], 'student', 'select disciplines')

    disciplines = read_disciplines()
    if isinstance(disciplines, str):
        return disciplines  # Возвращаем сообщение об ошибке
    disciplines = disciplines[disciplines['course'].astype(str) == str(student_course)]
    disciplines['semester'] = disciplines['semester'].astype(int)

    for index, discipline in disciplines.iterrows():
        qr_code_path = os.path.join(QR_CODES_DIR, f"{discipline['discipline_id']}.png")
        qr = qrcode.make(discipline['link'].strip())
        qr.save(qr_code_path)
        disciplines.at[index, 'qr_code_path'] = qr_code_path

    first_semester_disciplines = disciplines[disciplines['semester'] == 1].to_dict('records')
    second_semester_disciplines = disciplines[disciplines['semester'] == 2].to_dict('records')

    return render_template('select_disciplines.html',
                           first_semester_disciplines=first_semester_disciplines,
                           second_semester_disciplines=second_semester_disciplines,
                           success=success)

    # Генерация QR-кодов для каждой дисциплины
    for index, discipline in disciplines.iterrows():
        qr_code_path = os.path.join(QR_CODES_DIR, f"{discipline['discipline_id']}.png")
        qr = qrcode.make(discipline['link'].strip())
        qr.save(qr_code_path)
        disciplines.at[index, 'qr_code_path'] = qr_code_path

    # Разделение дисциплин по семестрам
    first_semester_disciplines = disciplines[disciplines['semester'] == 1].to_dict('records')
    second_semester_disciplines = disciplines[disciplines['semester'] == 2].to_dict('records')

    return render_template('select_disciplines.html',
                           first_semester_disciplines=first_semester_disciplines,
                           second_semester_disciplines=second_semester_disciplines,
                           success=success)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    students = read_students()
    disciplines = read_disciplines()
    if isinstance(students, str):
        return students  # Возвращаем сообщение об ошибке
    if isinstance(disciplines, str):
        return disciplines  # Возвращаем сообщение об ошибке

    return render_template('admin.html', students=students.to_dict('records'))

@app.route('/admin2', methods=['GET', 'POST'])
def admin2():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    students = read_students()
    disciplines = read_disciplines()
    if isinstance(students, str):
        return students  # Возвращаем сообщение об ошибке
    if isinstance(disciplines, str):
        return disciplines  # Возвращаем сообщение об ошибке

    return render_template('admin2.html', students=students.to_dict('records'))

@app.route('/select_disciplines_admin/<student_id>', methods=['POST'])
def select_disciplines_admin(student_id):
    students = read_students()
    disciplines = read_disciplines()
    student = students[students['student_id'].astype(str) == student_id].iloc[0]
    student_course = student['course']

    selected_disciplines = request.form.getlist('disciplines')
    students.loc[students['student_id'] == student_id, 'selected_disciplines'] = ','.join(selected_disciplines)
    save_error = save_to_excel(students, 'students')
    if save_error:
        return save_error
    
    add_log_entry(session['admin_id'], 'admin' if session['role'] == 1 else 'admin2', f'select_disciplines for {student_id}')

    return redirect(url_for('admin'))

@app.route('/select_disciplines_for_student/<student_id>', methods=['GET', 'POST'])
def select_disciplines_for_student(student_id):
    students = read_students()
    disciplines = read_disciplines()
    student = students[students['student_id'].astype(str) == student_id].iloc[0]
    student_course = student['course']

    if request.method == 'POST':
        selected_disciplines = request.form.getlist('disciplines')
        students.loc[students['student_id'] == student_id, 'selected_disciplines'] = ','.join(selected_disciplines)
        save_error = save_to_excel(students, 'students')
        if save_error:
            return save_error

        # Логирование действия администратора
        add_log_entry(session['admin_id'], 'admin', f'select disciplines for student {student_id}')
        
        return redirect(url_for('admin2'))

    available_disciplines = disciplines[disciplines['course'].astype(str) == str(student_course)]
    available_disciplines['semester'] = available_disciplines['semester'].astype(int)

    first_semester_disciplines = available_disciplines[available_disciplines['semester'] == 1].to_dict('records')
    second_semester_disciplines = available_disciplines[available_disciplines['semester'] == 2].to_dict('records')

    return render_template('select_disciplines_for_student.html',
                           first_semester_disciplines=first_semester_disciplines,
                           second_semester_disciplines=second_semester_disciplines,
                           student=student)

@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin_route():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        full_name = request.form['full_name']
        role = request.form['role']
        result = add_admin(admin_id, full_name, role)
        if result == 'Администратор добавлен':
            user_role = 'admin2' if role == '2' else 'admin'
            add_log_entry(admin_id, user_role, 'add_admin')
        return redirect(url_for('admin2'))
    return render_template('add_admin.html')


@app.route('/stats')
def stats():
    total_users = get_total_users()
    students_by_course = get_students_by_course()
    students_with_disciplines = get_students_with_disciplines()
    popular_disciplines = get_popular_disciplines()
    admin_activity = get_admin_activity()
    return render_template('stats.html', total_users=total_users, students_by_course=students_by_course,
                           students_with_disciplines=students_with_disciplines, popular_disciplines=popular_disciplines,
                           admin_activity=admin_activity)

@app.route('/logs')
def logs():
    logs_df = read_logs()
    if isinstance(logs_df, str):
        return logs_df  # Возвращаем сообщение об ошибке
    logs = logs_df.to_dict('records')
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
