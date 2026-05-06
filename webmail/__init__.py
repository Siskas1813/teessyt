import os
import secrets
from flask import Flask

from .db import init_db, seed_data
from .routes.auth import auth_bp
from .routes.mailbox import mailbox_bp
from .routes.admin import admin_bp
from .routes.api import api_bp


def create_app() -> Flask:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')

    app = Flask(__name__, template_folder=template_dir)

    # Конфигурационные параметры вынесены из исходного кода
    # и могут задаваться через переменные окружения.
    instance_dir = os.path.join(base_dir, 'instance')
    upload_dir = os.environ.get('UPLOAD_DIR', os.path.join(base_dir, 'uploads'))
    db_path = os.environ.get('DB_PATH', os.path.join(instance_dir, 'corp_mail.db'))

    os.makedirs(instance_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    app.config['DB_PATH'] = db_path
    app.config['UPLOAD_DIR'] = upload_dir
    app.config['JWT_SIGNING_KEY'] = os.environ.get('JWT_SIGNING_KEY') or secrets.token_urlsafe(32)
    app.config['SMTP_PASSWORD'] = os.environ.get('SMTP_PASSWORD', '')

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')
        response.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=()'
        )
        response.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'"
        )
        return response

    init_db(app.config['DB_PATH'])
    seed_data(app.config['DB_PATH'])

    app.register_blueprint(auth_bp)
    app.register_blueprint(mailbox_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app