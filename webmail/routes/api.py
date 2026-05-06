import time

from flask import Blueprint, current_app, jsonify, request, session
from itsdangerous import URLSafeTimedSerializer

from webmail.db import get_conn

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def _require_authenticated_user():
    username = session.get('username')
    if not username:
        return None
    return username


@api_bp.route('/token')
def token():
    username = _require_authenticated_user()
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    serializer = URLSafeTimedSerializer(current_app.config['JWT_SIGNING_KEY'])
    token_value = serializer.dumps(
        {
            'sub': username,
            'role': session.get('role'),
            'iat': int(time.time()),
        },
        salt='api-token'
    )

    return jsonify(
        {
            'token': token_value,
            'token_type': 'signed',
        }
    )


@api_bp.route('/mail/search')
def api_search():
    username = _require_authenticated_user()
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    q = request.args.get('q', '').strip()[:100]
    requested_recipient = request.args.get('recipient', username).strip()

    if requested_recipient != username and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    like_query = f'%{q}%'

    conn = get_conn(current_app.config['DB_PATH'])
    rows = conn.execute(
        """
        SELECT id, sender, subject, body, created_at
        FROM mails
        WHERE recipient = ? AND subject LIKE ?
        ORDER BY created_at DESC
        """,
        (requested_recipient, like_query)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@api_bp.route('/config')
def safe_config_status():
    username = _require_authenticated_user()
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    if session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    return jsonify(
        {
            'db_configured': bool(current_app.config.get('DB_PATH')),
            'upload_dir_configured': bool(current_app.config.get('UPLOAD_DIR')),
            'smtp_configured': bool(current_app.config.get('SMTP_PASSWORD')),
            'token_signing_configured': bool(current_app.config.get('JWT_SIGNING_KEY')),
        }
    )