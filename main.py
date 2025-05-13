import fdb
from flask import Flask, request, jsonify, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

auth_database = 'введите значение'
auth_user = 'введите значение'
auth_password = 'введите значение'

auth_conn = fdb.connect(database=auth_database, user=auth_user, password=auth_password, charset='UTF8')

app = Flask(__name__)
app.config['SECRET_KEY'] = "введите значение"

@app.route('/')
def index():
    return render_template('task.html')


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

        if not hash_passwd:
            return jsonify({"error": "пользователь не найден"})

        if check_password_hash(hash_passwd[0], password_from_form):
            session['first_name'] = name_from_form
            session['last_name'] = surname_from_form
            session['group'] = group_from_form
            return jsonify({})

        else:
            return jsonify({"error": "пароли не совпадают"})

    return render_template('sign_in.html')


if __name__ == '__main__':
    app.run(debug=True)
