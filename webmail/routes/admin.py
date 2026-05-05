from flask import Blueprint, render_template, session, current_app, redirect, url_for
from webmail.db import get_conn

admin_bp = Blueprint('admin', __name__)


def _require_admin():
    if session.get('role') != 'admin':
        return redirect(url_for('mailbox.dashboard'))
    return None


@admin_bp.route('/admin/users')
def admin_users():
    redirect_response = _require_admin()
    if redirect_response:
        return redirect_response

    conn = get_conn(current_app.config['DB_PATH'])
    users = conn.execute('SELECT id, username, role, department FROM users').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)
