# -*- coding: utf-8 -*-
#导入对象
"""
Created on Wed Feb  5 17:21:09 2020

@author: 23363
"""
from app import db, login_manager, create_app
from flask_login import UserMixin

"""
读者用户表 User
*编号ID（主）
*姓名
*性别
*年龄
*密码
"""
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(32))
    sex = db.Column(db.String(10))
    age = db.Column(db.Integer)
    local = db.Column(db.String(30))
    password = db.Column(db.String(24))

    def __init__(self, user_id, user_name, sex, age, local, password):
        self.user_id = user_id
        self.user_name = user_name
        self.sex = sex
        self.age = age
        self.local = local
        self.password = password
    def get_id(self):
        return self.user_id
    def get_name(self):
        return self.user_name
    def verify_password(self, password):
        if self.password == password:
            return True
        else:
            return False

    def __repr__(self):
        return '<User %r>' % self.user_name

"""
管理员表 Admin
*编号ID（主）
*姓名
*密码
"""
class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(32))
    password = db.Column(db.String(24))

    def __init__(self, admin_id, admin_name, password):
        self.admin_id = admin_id
        self.admin_name = admin_name
        self.password = password
    def get_id(self):
        return self.admin_id
    def get_name(self):
        return self.admin_name
    def verify_password(self,password):
        if self.password == password:
            return True
        else:
            return False

    def __repr__(self):
        return '<Admin %r>' % self.admin_name

"""
书籍表 Book
*编号ID（主）
*图书名
*作者
*平均评分
*出版日期
*出版社
*图书价格
*库存数量
"""
class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.String(13), primary_key=True)
    book_name = db.Column(db.String(64))
    author = db.Column(db.String(64))
    average_rating = db.Column(db.Float(2))
    publish_date = db.Column(db.String(32))
    publish_name = db.Column(db.String(64))
    price = db.Column(db.Float(3))
    store_number = db.Column(db.Integer)

    def __repr__(self):
        return '<Book %r>' % self.book_name

"""
评分表 Rating（评分代表用户书架上有该书）
*评分编号ID（主）
*用户编号ID（外）
*图书编号ID（外）
*评分
"""
class Rating(db.Model):
    __tablename__ = 'rating'
    rating_id = db.Column(db.String(10),primary_key=True)
    user_id = db.Column(db.ForeignKey('user.user_id'))
    book_id = db.Column(db.ForeignKey('book.book_id'))
    rate = db.Column(db.Integer)

    def __repr__(self):
        return '<Rating %r>' % self.rating_id

"""
订单表 Cart
*订单编号ID（主）
*用户编号ID（外）
*图书编号ID（外）
*订购数量
*总价
"""
class Cart(db.Model):
    __tablename__ =  'cart'
    cart_id = db.Column(db.String(10), primary_key=True)
    user_id = db.Column(db.ForeignKey('user.user_id'))
    book_id = db.Column(db.ForeignKey('book.book_id'))
    buy_number = db.Column(db.Integer)
    total_price = db.Column(db.Float(5))

    def __repr__(self):
        return '<Cart %r>' % self.cart_id

"""
库存操作清单 Inventory
*库存操作编号（主）
*图书编号
*本批次图书修改数量
*本批次图书存放位置
*本批次图书存放日期
*本次的入库操作员
"""
class Inventory(db.Model):
    __tablename__ = 'inventory'
    bar_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(13))
    storage_number = db.Column(db.Integer) #可正可负
    storage_date = db.Column(db.String(13))
    location = db.Column(db.String(32))
    admin_id = db.Column(db.ForeignKey('admin.admin_id'))  # 入库操作员

    def __repr__(self):
        return '<Inventory %r>' % self.barcode

"""
@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))
"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    db.metadata.clear()
    db.create_all(app = create_app())