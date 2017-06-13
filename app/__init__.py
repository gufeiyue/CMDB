from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager



db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)

    app.secret_key = "gufy"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@192.168.5.2:3306/superlight'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .admin import admin as admin_buleprint
    app.register_blueprint(admin_buleprint)

    from .config import config as config_buleprint
    app.register_blueprint(config_buleprint, url_prefix='/config')

    from .auth import auth as auth_buleprint
    app.register_blueprint(auth_buleprint, url_prefix='/auth')

    from .asset import asset as asset_buleprint
    app.register_blueprint(asset_buleprint, url_prefix='/asset')

    from .api import api as api_buleprint
    app.register_blueprint(api_buleprint, url_prefix='/api')

    return app
