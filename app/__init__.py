from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    # static_url_path表示用户浏览器访问的url是什么样子，static_folder参数是你实际的文件路径
    app = Flask(__name__,static_url_path="/sticker/static")
    # app.config["APPLICATION_ROOT"] = "/static"
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/sticker')
    #也可以再mian文件里面main = Blueprint('main', __name__,url_prefix='/sticker')
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/sticker/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/sticker/api/v1')

    return app
