from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from webmail.db import get_conn

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def login_page():
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = get_conn(current_app.config['DB_PATH'])
    c = conn.cursor()
    # Преднамеренно уязвимо: SQL Injection
    row = c.execute(
        f"SELECT username, role, full_name, department FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"
    ).fetchone()
    conn.close()

    if row:
        session['username'] = row['username']
        session['role'] = row['role']
        session['full_name'] = row['full_name']
        session['department'] = row['department']
        return redirect(url_for('mailbox.dashboard'))

    return 'Неверный логин/пароль'


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))
