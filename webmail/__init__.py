import os
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

    # Преднамеренно небезопасно: секреты и инфраструктурные данные в коде
    app.config['SECRET_KEY'] = 'corp-mail-super-secret-key'
    app.config['DB_PATH'] = 'corp_mail.db'
    app.config['UPLOAD_DIR'] = 'uploads'
    app.config['JWT_SIGNING_KEY'] = 'jwt-dev-key-unsafe'
    app.config['SMTP_PASSWORD'] = 'smtp_password_plaintext'

    init_db(app.config['DB_PATH'])
    seed_data(app.config['DB_PATH'])

    app.register_blueprint(auth_bp)
    app.register_blueprint(mailbox_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app
