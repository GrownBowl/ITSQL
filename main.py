from datetime import datetime

import fdb
from flask import Flask, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

auth_database = 'введение значение'
auth_user = 'введение значение'
auth_password = 'введение значение'
auth_conn = fdb.connect(database=auth_database, user=auth_user, password=auth_password, charset='UTF8')

stud_database = 'введение значение'
stud_user = 'введение значение'
stud_password = 'введение значение'
stud_conn = fdb.connect(database=stud_database, user=stud_user, password=stud_password, charset='UTF8')

adm_stud_database = 'введение значение'
adm_stud_user = 'введение значение'
adm_stud_password = 'введение значение'
adm_stud_conn = fdb.connect(database=stud_database, user=stud_user, password=stud_password, charset='UTF8')

app = Flask(__name__)
app.config['SECRET_KEY'] = "введение значение"


@app.route('/')
def index():
    if not session.get('student_id'):
        return redirect('/sign_in')

    return render_template('task.html')


@app.route('/go_query', methods=['GET', 'POST'])
def go_query():
    req = request.json
    sql_query = req['sql_query']

    cur = stud_conn.cursor()
    result = cur.execute(sql_query).fetchall()

    # дальше передать json с ответом


@app.route('check_answer', methods=['GET', 'POST'])
def check_answer():
    req = request.json
    sql_query = req['sql_query']
    number = req['number']

    adm_cur = stud_conn.cursor()
    correct_answer = adm_cur.execute("SELECT CORRECTANSWER FROM TASKS WHERE TASKID = ?", (number,)).fetchone()[0]

    stud_cur = stud_conn.cursor()
    stud_answer = stud_cur.execute(sql_query).fetchone()[0]

    if correct_answer == stud_answer:
        answer_is_correct = True
    else:
        answer_is_correct = False

    adm_cur.execute("INSERT INTO STUDENTANSWERS (studentid, studentanswer, iscorrect, answerdatetime) VALUES",
                    (session['student_id'], stud_answer, answer_is_correct, datetime.now()))
    return jsonify({})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        req = request.json
        name, surname = req['userName'].split()
        group = req['group']
        user_password = req['password']

        hash_passwd = generate_password_hash(user_password)

        cur = auth_conn.cursor()
        cur.execute("INSERT INTO users (lastname, firstname, groupname, password) VALUES (?, ?, ?, ?)",
                    (surname, name, group, hash_passwd))
        auth_conn.commit()

        return jsonify({})

    return render_template('register.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        req = request.json
        name_from_form, surname_from_form = req['userName'].split()
        group_from_form = req['group']
        password_from_form = req['password']

        cur = auth_conn.cursor()
        hash_passwd = cur.execute("SELECT PASSWORD FROM users WHERE LASTNAME = ? AND FIRSTNAME = ? AND GROUPNAME = ?",
                                  (surname_from_form, name_from_form, group_from_form)).fetchone()
        student_id = cur.execute("SELECT ID FROM users WHERE LASTNAME = ? AND FIRSTNAME = ? AND GROUPNAME = ?",
                                 (surname_from_form, name_from_form, group_from_form)).fetchone()

        if not hash_passwd:
            return jsonify({"error": "пользователь не найден"})

        if check_password_hash(hash_passwd[0], password_from_form):
            session['first_name'] = name_from_form
            session['last_name'] = surname_from_form
            session['group'] = group_from_form
            session['student_id'] = student_id[0]

            return jsonify({})

        else:
            return jsonify({"error": "пароли не совпадают"})

    return render_template('sign_in.html')


if __name__ == '__main__':
    app.run(debug=True)
