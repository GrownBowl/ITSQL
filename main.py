from datetime import datetime

import fdb
from flask import Flask, request, jsonify, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

AUTH_USERS_FILE = "auth_users.txt"

admins = [1]  # ID учетных записей администраторов

auth_database = '172.52.52.2/3050:/db/authorization.fdb'
auth_user = 'SYSDBA'
auth_password = 'masterkey'
auth_conn = fdb.connect(database=auth_database, user=auth_user, password=auth_password, charset='UTF8')

stud_database = '172.52.52.2/3050:/db/study_platform.fdb'
stud_user = 'student'
stud_password = 'student_password'
stud_conn = fdb.connect(database=stud_database, user=stud_user, password=stud_password, charset='UTF8')

adm_stud_database = '172.52.52.2/3050:/db/study_platform.fdb'
adm_stud_user = 'SYSDBA'
adm_stud_password = 'masterkey'
adm_stud_conn = fdb.connect(database=adm_stud_database, user=adm_stud_user, password=adm_stud_password, charset='UTF8')

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "yandexliceumsecretkey"


def write_user_id_to_file(user_id: str):
    with open(AUTH_USERS_FILE, "a") as f:
        f.write(user_id + "\n")


def remove_user_id_from_file(user_id: str):
    with open(AUTH_USERS_FILE, "r") as f:
        lines = f.readlines()

    with open(AUTH_USERS_FILE, "w") as f:
        for line in lines:
            if line.strip() != user_id:
                f.write(line)


def user_is_authorized(user_id: str):
    with open(AUTH_USERS_FILE, "r") as f:
        lines = f.readlines()

    with open(AUTH_USERS_FILE, "r") as f:
        for line in lines:
            if line.strip() == user_id:
                return True

        return False


def sort_by_correct_answers(data):
    scored_data = []
    for item in data:
        parts = item.split(":")

        if len(parts) > 1:
            score_str = parts[1].strip()
            score = int(score_str)
        else:
            score = 0

        scored_data.append((score, item))

    scored_data.sort(key=lambda x: x[0], reverse=True)

    sorted_data = [item[1] for item in scored_data]

    return sorted_data


def user_is_finished(user_id):
    adm_cur = adm_stud_conn.cursor()
    res = adm_cur.execute("select * from STUDENTISFINISHED where STUDENTID = ?", (user_id,)).fetchone()

    return res is not None


@app.route('/')
def index():
    if not session.get('student_id'):
        return redirect('/sign_in')

    if user_is_finished(session.get('student_id')):
        return redirect('/result')

    return render_template('task.html')


@app.route('/go_query', methods=['GET', 'POST'])
def go_query():
    req = request.json
    sql_query = req['request']

    try:
        cur = stud_conn.cursor()
        result = cur.execute(sql_query).fetchall()
        print(f"Студент с id: {session['student_id']} использовал такой запрос: {sql_query}")

        return result

    except fdb.fbcore.DatabaseError as err:
        sql_code = err.args[1]

        if sql_code == -206:
            return jsonify({"error": "Ошибка: Неизвестный столбец"})

        elif sql_code == -104:
            return jsonify({"error": "Ошибка синтаксиса SQL."})

        elif sql_code == -204:
            return jsonify({"error": "Ошибка: неизвестная таблица"})

        elif sql_code == -551:
            return jsonify({"error": " Куда это мы полезли? Об этом будет доложено системному Администратору!"})

        elif sql_code == -607:
            return jsonify({"error": "Я тебе дропну таблицу  >:/"})

        else:
            print(err)
            return jsonify({"error": "Неизвестная ошибка"})


@app.route('/check_answer', methods=['GET', 'POST'])
def check_answer():
    req = request.json

    sql_query = req['request']
    number = int(req['number'])
    print(f"Студент с id: {session['student_id']} ответил на вопрос номер: {number} таким запросом: {sql_query}")

    try:
        adm_cur = adm_stud_conn.cursor()
        correct_query = adm_cur.execute("SELECT CORRECTANSWER FROM TASKS WHERE TASKID = ?", (number,)).fetchone()[0]
        correct_answer = adm_cur.execute(correct_query).fetchall()

        stud_cur = stud_conn.cursor()
        stud_answer = stud_cur.execute(sql_query).fetchall()

        if correct_answer == stud_answer:
            answer_is_correct = True
        else:
            answer_is_correct = False

        answer_already = adm_cur.execute("select * from STUDENTANSWERS where STUDENTID = ? and ANSWERNUMBER = ?",
                                         (session["student_id"], number)).fetchall()

        if answer_already:
            adm_cur.execute("delete from STUDENTANSWERS where STUDENTID = ? and ANSWERNUMBER = ?",
                            (session["student_id"], number))

        adm_cur.execute(
            "INSERT INTO STUDENTANSWERS (studentid, studentanswer, iscorrect, answerdatetime, ANSWERNUMBER) VALUES (?, ?, ?, ?, ?)",
            (session["student_id"], stud_answer[0], answer_is_correct, datetime.now(), number))
        adm_stud_conn.commit()

        return jsonify({})

    except fdb.fbcore.DatabaseError as err:
        sql_code = err.args[1]

        if sql_code == -206:
            return jsonify({"error": "Ошибка: Неизвестный столбец"})

        elif sql_code == -104:
            return jsonify({"error": "Ошибка синтаксиса SQL."})

        elif sql_code == -204:
            return jsonify({"error": "Ошибка: неизвестная таблица"})

        elif sql_code == -551:
            return jsonify({"error": " Куда это мы полезли? Об этом будет доложено системному Администратору!"})

        elif sql_code == -607:
            return jsonify({"error": "Я тебе дропну таблицу  >:/"})

        else:
            print(err)
            return jsonify({"error": "Неизвестная ошибка"})


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

    return jsonify(task_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        req = request.json
        surname, name = req['userName'].split()
        group = req['group']
        user_password = req['password']
        auth_cur = auth_conn.cursor()
        res = auth_cur.execute("select * from USERS where FIRSTNAME = ? and LASTNAME = ? and GROUPNAME = ?", (name, surname, group)).fetchone()

        print(res)
        if res:
            return jsonify({"to_user": "Такой пользователь уже зарегестрирован"})

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
        surname_from_form, name_from_form = req['userName'].split()
        group_from_form = req['group']
        password_from_form = req['password']

        cur = auth_conn.cursor()
        student_id = cur.execute("SELECT ID FROM users WHERE LASTNAME = ? AND FIRSTNAME = ? AND GROUPNAME = ?",
                                 (surname_from_form, name_from_form, group_from_form)).fetchone()
	
        if student_id is None:
            return jsonify({"to_user": "Пользователь не найден"})

        if user_is_authorized(str(student_id[0])):
            return jsonify({"to_user": "Пользователь уже авторизован"})

        hash_passwd = cur.execute("SELECT PASSWORD FROM users WHERE LASTNAME = ? AND FIRSTNAME = ? AND GROUPNAME = ?",
                                  (surname_from_form, name_from_form, group_from_form)).fetchone()

        if not hash_passwd:
            return jsonify({"to_user": "Пользователь не найден"})

        if check_password_hash(hash_passwd[0], password_from_form):
            session['first_name'] = name_from_form
            session['last_name'] = surname_from_form
            session['group'] = group_from_form
            session['student_id'] = int(student_id[0])

            write_user_id_to_file(str(student_id[0]))

            return jsonify({})

        else:
            return jsonify({"to_user": "пароли не совпадают"})

    return render_template('sign_in.html')


@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html')


@app.route('/result_table', methods=['GET'])
def result_table():
    if session['student_id'] in admins:
        return render_template('result_table.html')
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


@app.route('/get_result_table')
def get_result_table():
    adm_cur = adm_stud_conn.cursor()
    result = adm_cur.execute("select STUDENTID, ISCORRECT, ANSWERNUMBER from STUDENTANSWERS").fetchall()

    finished_students = adm_cur.execute("select * from STUDENTISFINISHED").fetchall()

    auth_cur = auth_conn.cursor()
    all_users = auth_cur.execute("select ID, LASTNAME, FIRSTNAME, GROUPNAME from USERS").fetchall()
    answers = {}
    users_id = {}
    for user in all_users:
        id = str(user[0])
        lastname = user[1]
        firstname = user[2]
        groupname = user[3]

        for el in finished_students:
            if int(id) == el[0]:
                users_id[id] = f"+ {lastname} {firstname} {groupname}"
            else:
                users_id[id] = f"- {lastname} {firstname} {groupname}"

        answers[id] = 0

    for res in result:
        id = str(res[0])
        is_correct_answer = res[1]

        if is_correct_answer:
            answers[id] += 1
    print(users_id)
    results = []
    for id, res in answers.items():
        results.append(f"{users_id[id]}: {res}")

    results = sort_by_correct_answers(results)

    return results


@app.route('/finish', methods=['GET', 'POST'])
def finish():
    adm_cur = adm_stud_conn.cursor()
    adm_cur.execute("insert into STUDENTISFINISHED (studentid, isfinished) VALUES (?, ?)",
                    (session['student_id'], True))
    adm_stud_conn.commit()

    return jsonify({})

@app.route('/logout')
def logout():
    remove_user_id_from_file(str(session["student_id"]))
    session.pop('first_name')
    session.pop('last_name')
    session.pop('group')
    session.pop('student_id')

    return redirect("/sign_in")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
