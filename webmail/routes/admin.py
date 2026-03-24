from flask import Blueprint, request, render_template, session, current_app, redirect, url_for
from webmail.db import run_raw_query

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('mailbox.dashboard'))

    db_path = current_app.config['DB_PATH']
    users = run_raw_query(db_path, 'SELECT id, username, role, department FROM users')
    return render_template('admin/users.html', users=users)


@admin_bp.route('/admin/sql', methods=['GET', 'POST'])
def admin_sql_console():
    if session.get('role') != 'admin':
        return 'Forbidden', 403

    rows = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', 'SELECT 1')
        # Преднамеренно уязвимо: raw SQL-консоль
        rows = run_raw_query(current_app.config['DB_PATH'], query)

    return render_template('admin/sql_console.html', rows=rows, query=query)
