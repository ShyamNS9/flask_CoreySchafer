from flask import Flask
from blog_app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

mail = Mail()
bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'users.login_page'
login_manager.login_message_category = 'info'


def create_application(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    mail.init_app(app=app)
    bcrypt.init_app(app=app)
    db.init_app(app=app)
    login_manager.init_app(app=app)

    from blog_app.main.routes import main
    from blog_app.users.routes import users
    from blog_app.posts.routes import posts
    from blog_app.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app
