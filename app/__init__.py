# -*- coding: utf-8 -*-
#创建对象
from flask import Flask
from flask_login import LoginManager

from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

login_manager = LoginManager()
#login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'main.login'
login_manager.login_message = u"请先登录。"
def create_app():

    app = Flask(__name__)
    app.config.from_object(DevConfig)
    login_manager.init_app(app)
    db.init_app(app)
    # 附加路由
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

