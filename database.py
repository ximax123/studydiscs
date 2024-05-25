# -*- coding: utf-8 -*-
import pandas as pd
import os

DB_FILE = 'database.xlsx'

def init_db():
    if not os.path.exists(DB_FILE):
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            # Создание листа для студентов
            students_df = pd.DataFrame(columns=['student_id', 'full_name', 'group', 'faculty', 'course', 'selected_disciplines'])
            students_df.to_excel(writer, index=False, sheet_name='students')
            
            # Создание листа для дисциплин
            disciplines_df = pd.DataFrame(columns=['discipline_id', 'name', 'description', 'link', 'course', 'semester'])
            disciplines_df.to_excel(writer, index=False, sheet_name='disciplines')
            
            # Создание листа для администраторов
            admins_df = pd.DataFrame(columns=['admin_id', 'full_name', 'role'])
            admins_df.to_excel(writer, index=False, sheet_name='admins')

            # Создание листа для логов
            logs_df = pd.DataFrame(columns=['timestamp', 'user_id', 'user_role', 'action'])
            logs_df.to_excel(writer, index=False, sheet_name='logs')

            # Создание листа для статистики
            stats_df = pd.DataFrame(columns=['metric', 'value'])
            stats_df.to_excel(writer, index=False, sheet_name='statistics')
    else:
        with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            if 'students' not in writer.book.sheetnames:
                students_df = pd.DataFrame(columns=['student_id', 'full_name', 'group', 'faculty', 'course', 'selected_disciplines'])
                students_df.to_excel(writer, index=False, sheet_name='students')
            if 'disciplines' not in writer.book.sheetnames:
                disciplines_df = pd.DataFrame(columns=['discipline_id', 'name', 'description', 'link', 'course', 'semester'])
                disciplines_df.to_excel(writer, index=False, sheet_name='disciplines')
            if 'admins' not in writer.book.sheetnames:
                admins_df = pd.DataFrame(columns=['admin_id', 'full_name', 'role'])
                admins_df.to_excel(writer, index=False, sheet_name='admins')
            if 'logs' not in writer.book.sheetnames:
                logs_df = pd.DataFrame(columns=['timestamp', 'user_id', 'user_role', 'action'])
                logs_df.to_excel(writer, index=False, sheet_name='logs')
            if 'statistics' not in writer.book.sheetnames:
                stats_df = pd.DataFrame(columns=['metric', 'value'])
                stats_df.to_excel(writer, index=False, sheet_name='statistics')

def read_students():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        students_df = pd.read_excel(DB_FILE, sheet_name='students', dtype=str)
        students_df['selected_disciplines'] = students_df['selected_disciplines'].fillna('')
        print("Содержимое таблицы студентов:", students_df)
        return students_df
    except Exception as e:
        print("Ошибка при чтении таблицы студентов:", e)
        return 'error 404'

def read_disciplines():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        disciplines_df = pd.read_excel(DB_FILE, sheet_name='disciplines')
        print("Содержимое таблицы дисциплин:", disciplines_df)
        return disciplines_df
    except Exception as e:
        print("Ошибка при чтении таблицы дисциплин:", e)
        return 'error 404'

def read_admins():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        admins_df = pd.read_excel(DB_FILE, sheet_name='admins')
        print("Содержимое таблицы администраторов:", admins_df)
        return admins_df
    except Exception as e:
        print("Ошибка при чтении таблицы администраторов:", e)
        return 'error 404'

def read_logs():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        logs_df = pd.read_excel(DB_FILE, sheet_name='logs')
        return logs_df
    except Exception as e:
        return f'Ошибка при чтении таблицы логов: {e}'

def read_statistics():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        stats_df = pd.read_excel(DB_FILE, sheet_name='statistics')
        return stats_df
    except Exception as e:
        return f'Ошибка при чтении таблицы статистики: {e}'

def add_student(student_id, full_name, group, faculty, course):
    students_df = read_students()
    if isinstance(students_df, str):
        return students_df
    
    new_student = {'student_id': student_id, 'full_name': full_name, 'group': group, 'faculty': faculty, 'course': course, 'selected_disciplines': ''}
    students_df = students_df._append(new_student, ignore_index=True)
    
    with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        students_df.to_excel(writer, index=False, sheet_name='students')
    
    return 'Студент добавлен'

def add_discipline(discipline_id, name, description, link, course, semester):
    disciplines_df = read_disciplines()
    if isinstance(disciplines_df, str):
        return disciplines_df
    
    new_discipline = {'discipline_id': discipline_id, 'name': name, 'description': description, 'link': link, 'course': course, 'semester': semester}
    disciplines_df = disciplines_df._append(new_discipline, ignore_index=True)
    
    with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        disciplines_df.to_excel(writer, index=False, sheet_name='disciplines')
    
    return 'Дисциплина добавлена'

def add_admin(admin_id, full_name, role):
    admins_df = read_admins()
    if isinstance(admins_df, str):
        return admins_df
    
    new_admin = {'admin_id': admin_id, 'full_name': full_name, 'role': role}
    admins_df = admins_df._append(new_admin, ignore_index=True)
    
    with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        admins_df.to_excel(writer, index=False, sheet_name='admins')
    
    return 'Администратор добавлен'

def add_log_entry(user_id, user_role, action):
    logs_df = read_logs()
    if isinstance(logs_df, str):
        return logs_df

    new_log = {'timestamp': pd.Timestamp.now(), 'user_id': user_id, 'user_role': user_role, 'action': action}
    logs_df = logs_df._append(new_log, ignore_index=True)
    
    with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        logs_df.to_excel(writer, index=False, sheet_name='logs')

    return 'Лог добавлен'

def read_logs():
    if not os.path.exists(DB_FILE):
        return 'Базы данных нет'
    
    try:
        logs_df = pd.read_excel(DB_FILE, sheet_name='logs')
        print("Содержимое таблицы логов:", logs_df)
        return logs_df
    except Exception as e:
        print("Ошибка при чтении таблицы логов:", e)
        return 'error 404'

def update_statistics(metric, value):
    stats_df = read_statistics()
    if isinstance(stats_df, str):
        return stats_df

    if metric in stats_df['metric'].values:
        stats_df.loc[stats_df['metric'] == metric, 'value'] = value
    else:
        new_stat = {'metric': metric, 'value': value}
        stats_df = stats_df._append(new_stat, ignore_index=True)

    with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        stats_df.to_excel(writer, index=False, sheet_name='statistics')

    return 'Статистика обновлена'

def get_total_users():
    students = read_students()
    admins = read_admins()
    if isinstance(students, str) or isinstance(admins, str):
        return 'error'
    total_students = len(students)
    total_admins = len(admins)
    return {'total_students': total_students, 'total_admins': total_admins}

def get_students_by_course():
    students = read_students()
    if isinstance(students, str):
        return 'error'
    students_by_course = students['course'].value_counts().to_dict()
    return students_by_course

def get_students_with_disciplines():
    students = read_students()
    if isinstance(students, str):
        return 'error'
    students_with_disciplines = students[students['selected_disciplines'] != ''].shape[0]
    return students_with_disciplines

def get_popular_disciplines():
    students = read_students()
    disciplines = read_disciplines()
    if isinstance(students, str) or isinstance(disciplines, str):
        return 'error'
    all_selected_disciplines = students['selected_disciplines'].str.split(',').explode()
    popular_disciplines = all_selected_disciplines.value_counts().head(5).to_dict()
    return popular_disciplines

def get_logins_by_period(start_date, end_date):
    logs = read_logs()
    if isinstance(logs, str):
        return 'error'
    logins = logs[(logs['action'] == 'login') & (logs['timestamp'] >= start_date) & (logs['timestamp'] <= end_date)]
    total_logins = len(logins)
    return total_logins

def get_admin_activity():
    logs = read_logs()
    if isinstance(logs, str):
        return 'error'
    admin_activity = logs[logs['user_role'] == 'admin']['action'].value_counts().to_dict()
    return admin_activity

