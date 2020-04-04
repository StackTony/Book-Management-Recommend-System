# -*- coding: utf-8 -*-
class Config(object):
    pass

class DevConfig(Config):
    DEBUG = True
    SECRET_KEY = '66666'
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False  # 这个配置可以确保http请求返回的json数据中正常显示中文
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:712519@localhost:3306/book_manage?charset=utf8mb4"  # mysql+pymysql://用户名:密码@localhost:3306/数据库名?charset=utf8mb4
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
