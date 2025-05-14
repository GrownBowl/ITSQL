from datetime import datetime

import fdb
from flask import Flask, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

admins = [14]  # ID учетных записей администраторов

auth_database = 'введите значение'
auth_user = 'введите значение'
auth_password = 'введите значение'
auth_conn = fdb.connect(database=auth_database, user=auth_user, password=auth_password, charset='UTF8')

stud_database = 'введите значение'
stud_user = 'введите значение'
stud_password = 'введите значение'
stud_conn = fdb.connect(database=stud_database, user=stud_user, password=stud_password, charset='UTF8')

adm_stud_database = 'введите значение'
adm_stud_user = 'введите значение'
adm_stud_password = 'введите значение'
adm_stud_conn = fdb.connect(database=adm_stud_database, user=adm_stud_user, password=adm_stud_password, charset='UTF8')

app = Flask(__name__)
app.config['SECRET_KEY'] = "введите значение"


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


@app.route('/check_answer', methods=['GET', 'POST'])
def check_answer():
    req = request.json
    sql_query = req['sql_query']
    number = int(req['number'])

    adm_cur = adm_stud_conn.cursor()
    correct_answer = adm_cur.execute("SELECT CORRECTANSWER FROM TASKS WHERE TASKID = ?", (number,)).fetchone()[0]

    stud_cur = stud_conn.cursor()
    stud_answer = stud_cur.execute(sql_query).fetchone()[0]

    if str(correct_answer) == str(stud_answer):
        answer_is_correct = True
    else:
        answer_is_correct = False

    adm_cur.execute(
        "INSERT INTO STUDENTANSWERS (studentid, studentanswer, iscorrect, answerdatetime, ANSWERNUMBER) VALUES (?, ?, ?, ?, ?)",
        (14, stud_answer, answer_is_correct, datetime.now(), number))
    adm_stud_conn.commit()

    return jsonify({})


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    adm_cur = adm_stud_conn.cursor()
    tasks = adm_cur.execute("SELECT TASKID, TASKTEXT FROM TASKS").fetchall()

    task_list = []
    for task in tasks:
        task_list.append({
            "number": task[0],
            "text": task[1]
        })

    response = {"tasks": task_list}

    return jsonify(response)


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
            session['student_id'] = int(student_id[0])

            return jsonify({})

        else:
            return jsonify({"error": "пароли не совпадают"})

    return render_template('sign_in.html')


@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html')


@app.route('/result_table', methods=['GET'])
def result_table():
    if session['student_id'] in admins:
        return render_template('result.html')
    return "Доступ ограничен"


@app.route('/get_result')
def get_result():
    adm_cur = adm_stud_conn.cursor()
    results = adm_cur.execute("select STUDENTID, ISCORRECT, ANSWERNUMBER from STUDENTANSWERS where STUDENTID = ?",
                              (session['student_id'],)).fetchall()

    count_correct_answer = 0

    for res in results:
        stud_id = int(res[0])
        is_correct = res[1]

        if stud_id == session['student_id'] and is_correct:
            count_correct_answer += 1

    return jsonify({"result": count_correct_answer})


# @app.route('/get_result_table')
# def get_result_table():
#     adm_cur = adm_stud_conn.cursor()
#     results = adm_cur.execute("select STUDENTID, ISCORRECT, ANSWERNUMBER from STUDENTANSWERS").fetchall()
#
#     auth_cur = auth_conn.cursor()
#     all_users = auth_cur.execute("select ID, LASTNAME, FIRSTNAME, GROUPNAME from USERS").fetchall()
#
#     users_id = {}
#     for user in all_users:
#         users_id[str(user[0])] = f"{user[1]} {user[2]} {user[3]}"
#
#     answers = []
#     for res in results:
#         print(res)
#
#     return "Нет ошибкам!"


@app.route('/logout')
def logout():
    session.pop('first_name')
    session.pop('last_name')
    session.pop('group')
    session.pop('student_id')

    return redirect("/sign_in")


if __name__ == '__main__':
    app.run(debug=True)
