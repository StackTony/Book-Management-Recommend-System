# -*- coding: utf-8 -*-

import time, datetime
import numpy as np
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user, login_manager
from .form import LoginForm, RegisterForm, SearchUserForm, SearchBookForm, AddUserForm, AddNewBookForm, \
    AddBookStoreForm
from .. import db
from . import main
from ..models import User, Admin, Book, Rating, Cart, Inventory

#首页   √
@main.route('/', methods=['GET', 'POST'])
def index():
    session['admin_id'] = ''
    session['admin_name'] = ''
    session['user_id'] = ''
    session['user_name'] = ''
    return render_template('base.html')

#热门图书（列出所有图书，按照评分高低排序）
@main.route('/hot_book', methods = ['GET','POST'])
def hot_book():
    return render_template('hot_book.html')
#不需要根据特定类别名查询，将所有书籍信息返回前端
@main.route('/list_all_book', methods = ['GET','POST'])
def list_all_book():
    data = []
    books = Book.query.order_by(Book.average_rating.desc()).all()
    for book in books:
        item = {
            'book_id': book.book_id,
            'book_name': book.book_name,
            'author': book.author,
            'average_rating': book.average_rating,
            'price': book.price,
            'publish_date': book.publish_date,
            'publish_name': book.publish_name,
            'store_number': book.store_number
        }
        data.append(item)
    return jsonify(data)

#书籍信息查询   √
@main.route('/search_book', methods=['GET', 'POST'])
def search_book():
    form = SearchBookForm()
    if session.get('admin_name') != '':
        return render_template('search_book.html', name=session.get('admin_name'), form=form)
    elif session.get('user_name') != '':
        return render_template('search_book.html', name=session.get('user_name'), form=form)
    else:
        return render_template('search_book.html', name='', form=form)
#根据信息查询书籍并返回前台从而显示查询结果
@main.route('/find_book', methods=['GET','POST'])
def find_book():
    content = request.form.get('content') #表单中提交过来的，一定非None，故接下来不用判断了
    #分别根据content内容进行数据库查询
    def find_book_id():
        return Book.query.filter(Book.book_id.contains(content)).all()
    def find_book_name():
        return Book.query.filter(Book.book_name.like('%'+content+'%')).all()
    def find_author():
        return Book.query.filter(Book.author.like('%'+content+'%')).all()
    def find_publish_date():
        return Book.query.filter(Book.publish_date.like('%'+content+'%')).all()
    def find_average_rating():
        return Book.query.filter(Book.average_rating == content).all()
    def find_price():
        return Book.query.filter(Book.price == content).all()

    #不带括号的函数调用，如a=find_XXX，则a代表函数体而非结果，是一个函数对象，不须等该函数执行完成。
    methods = {
        'book_id': find_book_id,
        'book_name': find_book_name,
        'author': find_author,
        'publish_date': find_publish_date,
        'average_rating': find_average_rating,
        'price': find_price
    }
    method = request.form.get('method')
    # 根据类别查询到的有关书籍的book列表
    books = methods[method]() #加上()即调用了函数，返回的是结果了，即返回了列表
    data = []
    for book in books:
        item = {
            'book_id': book.book_id,
            'book_name': book.book_name,
            'author': book.author,
            'average_rating': book.average_rating,
            'price': book.price,
            'publish_date': book.publish_date,
            'publish_name': book.publish_name,
            'store_number': book.store_number
        }
        data.append(item)
    return jsonify(data)

#####################管理员功能区########################

#管理员登录后的页面   √
@main.route('/base_admin')
@login_required
def base_admin():
    return render_template('base_admin.html', name=session.get('admin_name'))


#管理员-图书管理-添加书籍-新书入库   √
@main.route('/add_new_book', methods=['GET', 'POST'])
@login_required
def add_new_book():
    form = AddNewBookForm()
    if form.validate_on_submit():
        book_id = request.form.get('book_id')
        exist_id = Book.query.filter_by(book_id = book_id).first()
        if exist_id is None:
            book = Book()
            book.book_id = request.form.get('book_id')
            book.book_name = request.form.get('book_name')
            book.author = request.form.get('author')
            book.average_rating = 0.0
            book.publish_date = request.form.get('publish_date')
            book.publish_name = request.form.get('publish_name')
            book.price = request.form.get('price')
            book.store_number = 1
            db.session.add(book)
            db.session.commit()
            flash(u'新书入库成功！')
            return redirect(url_for('main.add_new_book'))
        else:
            flash(u'图书已存在，请直接进行库存更新操作！')
            return redirect(url_for('main.add_book_store'))

    return render_template('add_new_book.html', name=session.get('admin_name'), form=form)


#管理员-图书管理-添加书籍-库存补充
@main.route('/add_book_store', methods=['GET', 'POST'])
@login_required
def add_book_store():
    form = AddBookStoreForm()
    if form.validate_on_submit():
        book_id = request.form.get('book_id')
        exist_id = Book.query.filter_by(book_id = book_id).first()
        if exist_id is not None: #书在库存内仍有数目
            #产生新的bar_id 确保产生的bar_id作为主键是唯一的
            new_bar_id = np.random.randint(0, 50000000)
            exist_bar_id = Inventory.query.filter_by(bar_id=new_bar_id).first()
            while (exist_bar_id is not None):
                new_bar_id = np.random.randint(0, 50000000)
                exist_bar_id = Inventory.query.filter_by(bar_id=new_bar_id).first()
            #新建inventory清单，加入库存操作清单的数据库表
            newstore = Inventory()
            newstore.bar_id = new_bar_id
            newstore.book_id = request.form.get('book_id')
            newstore.location = request.form.get('location')
            newstore.storage_number = request.form.get('number')
            newstore.storage_date = session['admin_id']  #需要改成时间类型，再议！！！！！
            newstore.admin_id = session['admin_id']

            #将图书库存管理信息更改至图书表的剩余库存中
            book = Book.query.filter_by(book_id = book_id).first()
            operation_num = int(newstore.storage_number)
            store_num = int(book.store_number)
            #库中没有多余的书删除
            if store_num < abs(operation_num) and operation_num < 0:
                flash('库存不足以删除如此多的书！')
            elif store_num + operation_num == 0:
                db.session.add(newstore)
                db.session.commit()
                db.session.delete(book)
                db.session.commit()
                flash(u'库存更新成功(图书库存为0)！')
            else:
                book.store_number = book.store_number + operation_num
                db.session.add(newstore)
                db.session.commit()
                flash(u'库存更新成功！')
                db.session.add(book)
                db.session.commit()
            return redirect(url_for('main.add_book_store'))
        else:
            flash(u'图书不存在，请前往‘新书入库’进行添加！')
            return redirect(url_for('main.add_new_book'))
    return render_template('add_book_store.html', name=session.get('admin_name'), form=form)


#管理员-图书管理-修改图书基本信息   √
# （含编辑和删除）（涉及库存的不能直接更改）
@main.route('/modify_book', methods=['GET', 'POST'])
@login_required
def modify_book():
    form = SearchBookForm()
    # 利用ajax传值获取信息进行后台操作，放到delete_book和edit_book中
    return render_template('modify_book.html', name=session.get('admin_name'), form=form)
#管理员-图书管理-修改图书基本信息
#删除图书
@main.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    if request.method == 'POST':
        book_id = request.values.get('book_id')
        book = Book.query.filter_by(book_id=book_id).first()
        if book is not None:
            db.session.delete(book)
            db.session.commit()
            data = 'success'
            return jsonify(data)
#管理员-图书管理-修改图书基本信息
#编辑图书
@main.route('/edit_book', methods=['GET', 'POST'])
@login_required
def edit_book():
    if request.method == 'POST':
        book_id = request.values.get('book_id')
        field = request.values.get('edit_field')
        value = request.values.get('new_value')
        book = Book.query.filter_by(book_id=book_id).first()
        if book is not None:
            if field == 'book_name':
                book.book_name = value
            elif field == 'author':
                book.author = value
            elif field == 'price':
                book.price = value
            elif field == 'publish_date':
                book.publish_date = value
            elif field == 'publish_name':
                book.publish_name = value
            else:
                return jsonify('false')
            db.session.commit()
            data = 'ok'
            return jsonify(data)


#管理员-显示订单信息   √
@main.route('/list_order_info', methods=['GET','POST'])
@login_required
def list_order_info():
    return render_template('list_order_info.html', name=session.get('admin_name'))
#管理员-搜索订单信息返回前端显示
@main.route('/search_order', methods=['GET','POST'])
@login_required
def search_order():
    data = []
    orders = Cart.query.all()
    for order in orders:
        book_id = order.book_id
        book_name = Book.query.filter_by(book_id = book_id).first().book_name
        book_price = Book.query.filter_by(book_id=book_id).first().price
        user_id = order.user_id
        user_name = User.query.filter_by(user_id = user_id).first().user_name
        item = {
            'cart_id': order.cart_id,
            'book_id': book_id,
            'book_name': book_name,
            'user_id': user_id,
            'user_name': user_name,
            'buy_number': order.buy_number,
            'buy_date':order.buy_date,
            'price': book_price,
            'total_price': order.total_price
        }
        data.append(item)
    return jsonify(data)


#管理员-显示历史库存操作记录   √
@main.route('/list_add_operation', methods=['GET','POST'])
@login_required
def list_add_operation():
    return render_template('list_add_operation.html', name=session.get('admin_name'))
#搜索库存操作的记录数据返还给前端显示
@main.route('/search_operation', methods=['GET','POST'])
@login_required
def search_operation():
    data = []
    # 查询到的库存操作的operations列表, 按照操作员id升序排序
    operations = Inventory.query.order_by(Inventory.admin_id).all()
    for op in operations:
        book_id = op.book_id
        book_name = Book.query.filter_by(book_id = book_id).first().book_name
        admin_id = op.admin_id
        admin_name = Admin.query.filter_by(admin_id = admin_id).first().admin_name
        item = {
            'bar_id': op.bar_id,
            'book_id': op.book_id,
            'book_name': book_name,
            'admin_id': op.admin_id,
            'admin_name': admin_name,
            'storage_number': op.storage_number,
            'storage_date': op.storage_date,
            'location': op.location
        }
        data.append(item)
    return jsonify(data)


#管理员-用户管理-用户删除
@main.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = SearchUserForm()
    return render_template('delete_user.html', name=session.get('admin_name'), form=form)


#管理员-用户管理-添加用户
@main.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    return render_template('add_user.html', name=session.get('admin_name'), form=form)


#管理员-用户管理-用户信息查询   √
@main.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():
    form = SearchUserForm()
    return render_template('search_user.html', name=session.get('admin_name'), form=form)
#根据用户信息查询用户及其订单等信息并返回前台显示查询结果
@main.route('/find_user', methods=['GET','POST'])
@login_required
def find_user():
    content = request.form.get('content') #表单中提交过来的，一定非None，故接下来不用判断了
    #分别根据content内容进行数据库查询
    def find_user_id():
        return User.query.filter(User.user_id.contains(content)).all()
    def find_user_name():
        return User.query.filter(User.user_name.like('%'+content+'%')).all()
    def find_age():
        return User.query.filter(User.age == content).all()
    def find_local():
        return User.query.filter(User.local.like('%'+content+'%')).all()

    #不带括号的函数调用，如a=find_XXX，则a代表函数体而非结果，是一个函数对象，不须等该函数执行完成。
    methods = {
        'user_id': find_user_id,
        'user_name': find_user_name,
        'age': find_age,
        'local': find_local
    }
    method = request.form.get('method')
    # 根据类别查询到的有关用户的user列表
    users = methods[method]() #加上()即调用了函数，返回的是结果了，即返回了列表
    data = []
    for user in users:
        user_id = user.user_id
        carts = Cart.query.filter(user_id == user_id).all()
        for cart in carts:
            book_id = cart.book_id
            book = Book.query.filter(book_id == book_id).first()
            item = {
                #用户信息
                'user_id': user_id,
                'user_name': user.user_name,
                'sex': user.sex,
                'age': user.age,
                'local': user.local,
                'password': user.password,
                # 订单信息
                'cart_id': cart.cart_id,
                'buy_number': cart.buy_number,
                'buy_date': cart.buy_date,
                'total_price': cart.total_price,
                #图书信息
                'book_id': book.book_id,
                'book_name': book.book_name,
                'author': book.author,
                'average_rating': book.average_rating,
                'price': book.price,
                'publish_date': book.publish_date,
                'publish_name': book.publish_name,
                'store_number': book.store_number
            }
            data.append(item)
    return jsonify(data)


###########################用户功能区#############################

"""
#图框
#顶部：        用户注册
#分列：  用户名：【请输入用户名】
#         性别：o男  o女
#         年龄：【】
#         位置：【】
#         密码：【请输入密码】
#       确认密码：【请确认密码】
#底部：          注册
"""
#用户-注册   √
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.user_name.data
        sex = form.sex.data
        age = form.age.data
        local = form.local.data
        pwd = form.password.data
        pwd2 = form.password2.data
        user_id = np.random.randint(0,100000)
        #确保产生的user_id作为主键是唯一的
        exist_id = User.query.filter_by(user_id = user_id).first()
        while(exist_id is not None):
            user_id = np.random.randint(0, 100000)
            exist_id = User.query.filter_by(user_id = user_id).first()
        #产生新用户，并插入数据库
        new_user = User(user_id, name, sex, age, local, pwd)
        if new_user.verify_password(pwd2) is True:
            # db是SQLAlchemy()实例化对象，用于数据库操作
            db.session.add(new_user)
            db.session.commit()
            flash("注册成功！")
            #放入login_user中，否则会由于login_manage程序跳转到登录界面
            login_user(new_user)
            session['user_id'] = new_user.user_id
            session['user_name'] = new_user.user_name
            return redirect(url_for('main.base_user'))
        else:
            flash("两次密码不一致！")
            return redirect(url_for('main.register'))
    return render_template('register.html', form=form)


#用户登录后的主页
@main.route('/base_user')
@login_required
def base_user():
    return render_template('base_user.html', name = session.get('user_name'))


#######################用户/管理员公用区###########################

"""
#图框
#顶部：          登录
#分列：  用户名：【请输入用户名】
#        密码：【请输入密码】
#底部：          登录
#底部：   忘记密码（请联系管理员）
"""
#用户/管理员-登录   √
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #等价于if form.validate_on_submit():
    if form.validate_on_submit():
        name = form.user_name.data
        pwd = form.password.data
        user_tmp1 = User.query.filter_by(user_name=name, password=pwd).first()
        user_tmp2 = Admin.query.filter_by(admin_name=name, password=pwd).first()
        #在User和Admin表中均未找到，则说明输入无效
        if user_tmp1 is None and user_tmp2 is None:
            flash('账号或密码错误！')
            return redirect(url_for('main.login'))
        #在用户表中匹配到
        if user_tmp1 is not None:
            login_user(user_tmp1)
            session['user_id'] = user_tmp1.user_id
            session['user_name'] = user_tmp1.user_name
            flash("用户登录成功！")
            return redirect(url_for('main.base_user'))
        #在管理员表中匹配到
        elif user_tmp2 is not None:
            login_user(user_tmp2)
            session['admin_id'] = user_tmp2.admin_id
            session['admin_name'] = user_tmp2.admin_name
            flash("管理员登录成功！")
            return redirect(url_for('main.base_admin'))
    return render_template('login.html', form=form)


#用户/管理员-注销   √
@main.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))


