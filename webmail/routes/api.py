from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from webmail.db import get_conn

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        key = request.headers.get('X-API-Key', '')
        if not key:
            return jsonify({'error': 'Missing API key'}), 401
        conn = get_conn(current_app.config['DB_PATH'])
        rec = conn.execute('SELECT owner, scope FROM api_keys WHERE api_key = ?', (key,)).fetchone()
        conn.close()
        if not rec:
            return jsonify({'error': 'Invalid API key'}), 403
        return view(*args, **kwargs)

    return wrapped


@api_bp.route('/mail/search')
@require_api_key
def api_search():
    q = request.args.get('q', '').strip()
    recipient = request.args.get('recipient', '').strip()
    if not recipient:
        return jsonify({'error': 'recipient is required'}), 400

    conn = get_conn(current_app.config['DB_PATH'])
    pattern = f'%{q}%'
    rows = conn.execute(
        'SELECT id, sender, subject, body, created_at FROM mails WHERE recipient = ? AND subject LIKE ?',
        (recipient, pattern),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
