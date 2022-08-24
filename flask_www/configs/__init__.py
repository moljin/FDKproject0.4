from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

from flask_www.configs.apps import related_app
from flask_www.configs.config import TEMPLATE_ROOT, STATIC_ROOT, DevelopmentConfig, ProductionConfig
from flask_www.configs.routes import routes_init

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name=None):
    application = Flask(__name__, template_folder=TEMPLATE_ROOT, static_folder=STATIC_ROOT)

    if not config_name:
        if application.config['DEBUG']:
            config_name = DevelopmentConfig()
        else:
            config_name = ProductionConfig()
    application.config.from_object(config_name)

    csrf.init_app(application)
    db.init_app(application)
    if application.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(application, db, render_as_batch=True)
    else:
        migrate.init_app(application, db)
    from flask_www.accounts import models

    login_manager.init_app(application)
    login_manager.login_view = 'login'
    mail.init_app(application)

    @login_manager.user_loader
    def load_user(_id):
        from flask_www.accounts.models import User
        user = User.query.get(int(_id))
        return user

    routes_init(application)
    related_app(application)

    return application


app = create_app()
safe_time_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])