from flask import Flask, render_template, request, redirect, url_for, flash
import re
import sqlite3
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Для flash повідомлень

# Константа для назви бази даних
DB_NAME = 'points.db'

def get_ects_grade(value):
    """Визначає ECTS оцінку за числовим значенням"""
    if value is None:
        return None
    if value >= 90:
        return 'A'
    elif value >= 82:
        return 'B'
    elif value >= 74:
        return 'C'
    elif value >= 65:
        return 'D'
    elif value >= 60:
        return 'E'
    else:
        return 'F'

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        comment = request.form.get("comment")
        errors = []
        if not name:
            errors.append("Поле Ім'я не може бути порожнім.")
        if not email:
            errors.append("Поле Email не може бути порожнім.")
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if email and not re.match(email_regex, email):
            errors.append("Неправильний формат Email.")
        if not age:
            errors.append("Поле Вік не може бути порожнім.")
        if age and not age.isdigit():
            errors.append("Поле Вік повинно містити тільки цифри.")
        if not comment:
            errors.append("Поле Коментар не може бути порожнім.")
        if errors:
            return render_template("form.html", errors=errors, name=name, email=email, age=age, comment=comment)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"submission_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Ім'я: {name}\n")
            file.write(f"Email: {email}\n")
            file.write(f"Вік: {age}\n")
            file.write(f"Коментар: {comment}\n")
        return redirect(url_for("result", name=name, email=email, age=age, comment=comment, filename=filename))
    return render_template("form.html")

@app.route("/result")
def result():
    name = request.args.get("name", "")
    email = request.args.get("email", "")
    age = request.args.get("age", "")
    comment = request.args.get("comment", "")
    filename = request.args.get("filename", "")
    return render_template("result.html", name=name, email=email, age=age, comment=comment, filename=filename)

@app.route("/points")
def points():
    """Сторінка перегляду всіх оцінок студентів"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, s.name, c.title, c.semester, p.value
        FROM points p
        JOIN student s ON p.id_student = s.id
        JOIN course c ON p.id_course = c.id
        ORDER BY s.name, c.semester, c.title
    ''')
    grades = cursor.fetchall()
    conn.close()
    return render_template("points.html", grades=grades)

@app.route("/students")
def students():
    """Сторінка списку студентів з посиланнями на індивідуальні оцінки"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM student ORDER BY name')
    students = cursor.fetchall()
    conn.close()
    return render_template("students.html", students=students)

@app.route("/student/<int:student_id>")
def student_grades(student_id):
    """Сторінка перегляду оцінок конкретного студента"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Отримуємо ім'я студента
    cursor.execute('SELECT name FROM student WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return "Студент не знайдено", 404
    
    # Отримуємо оцінки студента
    cursor.execute('''
        SELECT c.title, c.semester, p.value
        FROM points p
        JOIN course c ON p.id_course = c.id
        WHERE p.id_student = ?
        ORDER BY c.semester, c.title
    ''', (student_id,))
    grades = cursor.fetchall()
    conn.close()
    return render_template("student_grades.html", student_name=student[0], grades=grades)

@app.route("/courses")
def courses():
    """Сторінка списку дисциплін"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, semester FROM course ORDER BY semester, title')
    courses = cursor.fetchall()
    conn.close()
    return render_template("courses.html", courses=courses)

@app.route("/course/<int:course_id>")
def course_ranking(course_id):
    """Сторінка рейтингового списку студентів за вибраною дисципліною"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Отримуємо назву дисципліни
    cursor.execute('SELECT title, semester FROM course WHERE id = ?', (course_id,))
    course = cursor.fetchone()
    if not course:
        conn.close()
        return "Дисципліна не знайдена", 404
    
    # Отримуємо рейтинг студентів за цією дисципліною
    cursor.execute('''
        SELECT s.id, s.name, p.value
        FROM points p
        JOIN student s ON p.id_student = s.id
        WHERE p.id_course = ?
        ORDER BY p.value DESC, s.name
    ''', (course_id,))
    rankings = cursor.fetchall()
    conn.close()
    return render_template("course_ranking.html", course_title=course[0], course_semester=course[1], rankings=rankings)

@app.route("/add_grade", methods=["GET", "POST"])
def add_grade():
    """Форма внесення нової оцінки"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == "POST":
        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        grade_value = request.form.get("grade")
        
        errors = []
        
        # Валідація
        if not student_id:
            errors.append("Оберіть студента.")
        if not course_id:
            errors.append("Оберіть дисципліну.")
        if not grade_value:
            errors.append("Введіть оцінку.")
        elif not grade_value.isdigit():
            errors.append("Оцінка повинна бути числом.")
        else:
            grade_value = int(grade_value)
            if grade_value < 0 or grade_value > 100:
                errors.append("Оцінка повинна бути від 0 до 100.")
        
        # Перевірка існування студента та дисципліни
        if student_id and not errors:
            cursor.execute('SELECT id FROM student WHERE id = ?', (student_id,))
            if not cursor.fetchone():
                errors.append("Обраний студент не існує.")
        
        if course_id and not errors:
            cursor.execute('SELECT id FROM course WHERE id = ?', (course_id,))
            if not cursor.fetchone():
                errors.append("Обрана дисципліна не існує.")
        
        if errors:
            # Отримуємо списки для відображення форми з помилками
            cursor.execute('SELECT id, name FROM student ORDER BY name')
            students = cursor.fetchall()
            cursor.execute('SELECT id, title FROM course ORDER BY title')
            courses = cursor.fetchall()
            conn.close()
            return render_template("add_grade.html", 
                                 students=students, 
                                 courses=courses, 
                                 errors=errors,
                                 student_id=student_id,
                                 course_id=course_id,
                                 grade=grade_value if isinstance(grade_value, int) else grade_value)
        
        # Збереження оцінки в базу даних
        try:
            cursor.execute('''
                INSERT INTO points (id_student, id_course, value)
                VALUES (?, ?, ?)
            ''', (student_id, course_id, grade_value))
            conn.commit()
            conn.close()
            return redirect(url_for('points'))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Помилка при збереженні: {str(e)}", 500
    
    # GET запит - показуємо форму
    cursor.execute('SELECT id, name FROM student ORDER BY name')
    students = cursor.fetchall()
    cursor.execute('SELECT id, title FROM course ORDER BY title')
    courses = cursor.fetchall()
    conn.close()
    return render_template("add_grade.html", students=students, courses=courses)

@app.route("/average_grades")
def average_grades():
    """Сторінка середніх балів по кожній дисципліні"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.title, c.semester, 
               ROUND(AVG(p.value), 2) as avg_grade,
               COUNT(p.value) as count_grades
        FROM course c
        LEFT JOIN points p ON c.id = p.id_course
        GROUP BY c.id, c.title, c.semester
        ORDER BY c.semester, c.title
    ''')
    averages = cursor.fetchall()
    conn.close()
    return render_template("average_grades.html", averages=averages)

@app.route("/ects_grades")
def ects_grades():
    """Сторінка підрахунку кількості оцінок за шкалою ECTS по кожній дисципліні"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Отримуємо всі оцінки з дисциплінами
    cursor.execute('''
        SELECT c.id, c.title, c.semester, p.value
        FROM course c
        LEFT JOIN points p ON c.id = p.id_course
        ORDER BY c.semester, c.title, p.value DESC
    ''')
    all_data = cursor.fetchall()
    conn.close()
    
    # Групуємо дані за дисципліною та ECTS оцінкою
    ects_stats = {}
    ects_order = ['A', 'B', 'C', 'D', 'E', 'F']
    
    for row in all_data:
        course_id, course_title, semester, value = row
        key = (course_id, course_title, semester)
        
        if key not in ects_stats:
            ects_stats[key] = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'total': 0}
        
        if value is not None:
            ects_grade = get_ects_grade(value)
            if ects_grade:
                ects_stats[key][ects_grade] += 1
                ects_stats[key]['total'] += 1
    
    # Перетворюємо в список для шаблону
    result = []
    for (course_id, course_title, semester), stats in sorted(ects_stats.items(), key=lambda x: (x[0][2], x[0][1])):
        result.append({
            'id': course_id,
            'title': course_title,
            'semester': semester,
            'A': stats['A'],
            'B': stats['B'],
            'C': stats['C'],
            'D': stats['D'],
            'E': stats['E'],
            'F': stats['F'],
            'total': stats['total']
        })
    
    return render_template("ects_grades.html", ects_data=result, ects_order=ects_order)

@app.route("/ects_students")
def ects_students():
    """Сторінка підрахунку кількості оцінок за шкалою ECTS по кожному студенту для кожного семестру"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Отримуємо всі оцінки з інформацією про студента та семестр
    cursor.execute('''
        SELECT s.id, s.name, c.semester, p.value
        FROM points p
        JOIN student s ON p.id_student = s.id
        JOIN course c ON p.id_course = c.id
        WHERE p.value IS NOT NULL
        ORDER BY s.name, c.semester, p.value DESC
    ''')
    all_data = cursor.fetchall()
    conn.close()
    
    # Групуємо дані за студентом та семестром
    ects_stats = {}
    
    for row in all_data:
        student_id, student_name, semester, value = row
        key = (student_id, student_name, semester)
        
        if key not in ects_stats:
            ects_stats[key] = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'total': 0}
        
        if value is not None:
            ects_grade = get_ects_grade(value)
            if ects_grade:
                ects_stats[key][ects_grade] += 1
                ects_stats[key]['total'] += 1
    
    # Перетворюємо в список для шаблону, групуємо за студентом
    students_data = {}
    for (student_id, student_name, semester), stats in ects_stats.items():
        if student_id not in students_data:
            students_data[student_id] = {
                'id': student_id,
                'name': student_name,
                'semesters': {}
            }
        students_data[student_id]['semesters'][semester] = {
            'A': stats['A'],
            'B': stats['B'],
            'C': stats['C'],
            'D': stats['D'],
            'E': stats['E'],
            'F': stats['F'],
            'total': stats['total']
        }
    
    # Сортуємо студентів за ім'ям
    result = []
    for student_id in sorted(students_data.keys()):
        student = students_data[student_id]
        # Сортуємо семестри та створюємо список для шаблону
        sorted_semesters = sorted(student['semesters'].keys())
        semester_list = []
        for sem in sorted_semesters:
            semester_list.append({
                'number': sem,
                'stats': student['semesters'][sem]
            })
        result.append({
            'id': student['id'],
            'name': student['name'],
            'semesters': semester_list
        })
    
    return render_template("ects_students.html", students_data=result, ects_order=['A', 'B', 'C', 'D', 'E', 'F'])

@app.route("/edit_grade/<int:grade_id>", methods=["GET", "POST"])
def edit_grade(grade_id):
    """Форма редагування існуючої оцінки"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == "POST":
        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        grade_value = request.form.get("grade")
        
        errors = []
        
        # Валідація
        if not student_id:
            errors.append("Оберіть студента.")
        if not course_id:
            errors.append("Оберіть дисципліну.")
        if not grade_value:
            errors.append("Введіть оцінку.")
        elif not grade_value.isdigit():
            errors.append("Оцінка повинна бути числом.")
        else:
            grade_value = int(grade_value)
            if grade_value < 0 or grade_value > 100:
                errors.append("Оцінка повинна бути від 0 до 100.")
        
        # Перевірка існування студента та дисципліни
        if student_id and not errors:
            cursor.execute('SELECT id FROM student WHERE id = ?', (student_id,))
            if not cursor.fetchone():
                errors.append("Обраний студент не існує.")
        
        if course_id and not errors:
            cursor.execute('SELECT id FROM course WHERE id = ?', (course_id,))
            if not cursor.fetchone():
                errors.append("Обрана дисципліна не існує.")
        
        # Перевірка існування оцінки
        cursor.execute('SELECT id FROM points WHERE id = ?', (grade_id,))
        if not cursor.fetchone():
            conn.close()
            return "Оцінка не знайдена", 404
        
        if errors:
            # Отримуємо списки для відображення форми з помилками
            cursor.execute('SELECT id, name FROM student ORDER BY name')
            students = cursor.fetchall()
            cursor.execute('SELECT id, title FROM course ORDER BY title')
            courses = cursor.fetchall()
            conn.close()
            return render_template("edit_grade.html", 
                                 students=students, 
                                 courses=courses, 
                                 errors=errors,
                                 student_id=student_id,
                                 course_id=course_id,
                                 grade=grade_value if isinstance(grade_value, int) else grade_value,
                                 grade_id=grade_id)
        
        # Оновлення оцінки в базі даних
        try:
            cursor.execute('''
                UPDATE points 
                SET id_student = ?, id_course = ?, value = ?
                WHERE id = ?
            ''', (student_id, course_id, grade_value, grade_id))
            conn.commit()
            conn.close()
            return redirect(url_for('points'))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"Помилка при оновленні: {str(e)}", 500
    
    # GET запит - показуємо форму з поточними значеннями
    cursor.execute('SELECT id_student, id_course, value FROM points WHERE id = ?', (grade_id,))
    grade_data = cursor.fetchone()
    
    if not grade_data:
        conn.close()
        return "Оцінка не знайдена", 404
    
    current_student_id, current_course_id, current_grade = grade_data
    
    cursor.execute('SELECT id, name FROM student ORDER BY name')
    students = cursor.fetchall()
    cursor.execute('SELECT id, title FROM course ORDER BY title')
    courses = cursor.fetchall()
    conn.close()
    
    return render_template("edit_grade.html", 
                         students=students, 
                         courses=courses,
                         student_id=current_student_id,
                         course_id=current_course_id,
                         grade=current_grade,
                         grade_id=grade_id)

@app.route("/delete_grade/<int:grade_id>", methods=["POST"])
def delete_grade(grade_id):
    """Видалення оцінки з підтвердженням"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Перевірка існування оцінки
    cursor.execute('SELECT id FROM points WHERE id = ?', (grade_id,))
    if not cursor.fetchone():
        conn.close()
        flash('Оцінка не знайдена', 'error')
        return redirect(url_for('points'))
    
    try:
        # Видалення оцінки
        cursor.execute('DELETE FROM points WHERE id = ?', (grade_id,))
        conn.commit()
        conn.close()
        flash('Оцінку успішно видалено', 'success')
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        flash(f'Помилка при видаленні: {str(e)}', 'error')
    
    return redirect(url_for('points'))

@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = "script-src 'self'"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)