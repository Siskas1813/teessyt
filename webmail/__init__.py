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
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-change-me')
    app.config['DB_PATH'] = os.path.join(base_dir, 'corp_mail.db')
    app.config['UPLOAD_DIR'] = os.path.join(base_dir, 'uploads')

    init_db(app.config['DB_PATH'])
    seed_data(app.config['DB_PATH'])

    app.register_blueprint(auth_bp)
    app.register_blueprint(mailbox_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app
