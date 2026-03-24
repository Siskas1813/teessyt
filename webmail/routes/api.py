import base64
from flask import Blueprint, request, jsonify, current_app
from webmail.db import run_raw_query

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/token')
def insecure_token():
    user = request.args.get('user', 'employee')
    # Преднамеренно небезопасный токен без подписи
    token = base64.b64encode(f"{user}:{current_app.config['JWT_SIGNING_KEY']}".encode()).decode()
    return jsonify({'token': token})


@api_bp.route('/mail/search')
def api_search():
    q = request.args.get('q', '')
    recipient = request.args.get('recipient', 'employee')
    query = (
        f"SELECT id, sender, subject, body, created_at FROM mails "
        f"WHERE recipient = '{recipient}' AND subject LIKE '%{q}%'"
    )
    rows = run_raw_query(current_app.config['DB_PATH'], query)
    return jsonify([dict(r) for r in rows])


@api_bp.route('/config')
def exposed_config():
    # Преднамеренно небезопасно: утечка конфигурации
    return jsonify(
        {
            'db': current_app.config['DB_PATH'],
            'upload_dir': current_app.config['UPLOAD_DIR'],
            'smtp_password': current_app.config['SMTP_PASSWORD'],
            'jwt_key': current_app.config['JWT_SIGNING_KEY'],
        }
    )
