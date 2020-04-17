# -*- coding: utf-8 -*-

import time, datetime
import os
import numpy as np
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from sqlalchemy import and_
from flask_login import login_user, logout_user, login_required, current_user, login_manager
from werkzeug.utils import secure_filename

from .form import LoginForm, RegisterForm, SearchUserForm, SearchBookForm, AddNewBookForm, \
    AddBookStoreForm, ChangePasswordForm, UserInfoForm, ChangePhotoForm
from .. import db
from . import main
from ..models import User, Admin, Book, Rating, Orders, Inventory, Favorite, Comment


# 首页   √
@main.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    session['admin_id'] = ''
    session['admin_name'] = ''
    session['user_id'] = ''
    session['user_name'] = ''
    return render_template('base.html', name='')


# 热门图书（列出所有图书，按照评分高低排序）  √
@main.route('/hot_book', methods=['GET', 'POST'])
def hot_book():
    books = Book.query.order_by(Book.average_rating.desc()).limit(5).all()
    if session['user_name'] == '' and session['admin_name'] == '':
        return render_template('hot_book.html', name='', books=books)
    elif session['user_name'] != '':
        return render_template('hot_book.html', name=session['user_name'], books=books)
    else:
        return render_template('hot_book.html', name=session['admin_name'], books=books)


# 不需要根据特定类别名查询，将所有书籍信息返回前端
@main.route('/list_all_book', methods=['GET', 'POST'])
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


# 按类别进行书籍信息查询   √
@main.route('/search_book', methods=['GET', 'POST'])
def search_book():
    form = SearchBookForm()
    if session.get('admin_name') != '':
        return render_template('search_book.html', name=session.get('admin_name'), form=form)
    elif session.get('user_name') != '':
        return render_template('search_book.html', name=session.get('user_name'), form=form)
    else:
        return render_template('search_book.html', name='', form=form)


# 根据信息查询书籍并返回前台从而显示查询结果
@main.route('/find_book', methods=['GET', 'POST'])
def find_book():
    content = request.form.get('content')  # 表单中提交过来的，一定非None，故接下来不用判断了

    # 分别根据content内容进行数据库查询
    def find_book_id():
        return Book.query.filter(Book.book_id.contains(content)).all()

    def find_book_name():
        return Book.query.filter(Book.book_name.like('%' + content + '%')).all()

    def find_author():
        return Book.query.filter(Book.author.like('%' + content + '%')).all()

    def find_publish_date():
        return Book.query.filter(Book.publish_date.like('%' + content + '%')).all()

    def find_average_rating():
        return Book.query.filter(Book.average_rating == content).all()

    def find_price():
        return Book.query.filter(Book.price == content).all()

    # 不带括号的函数调用，如a=find_XXX，则a代表函数体而非结果，是一个函数对象，不须等该函数执行完成。
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
    books = methods[method]()  # 加上()即调用了函数，返回的是结果了，即返回了列表
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


#####################管理员功能区   √  ########################

# 管理员登录后的页面   √
@main.route('/base_admin')
@login_required
def base_admin():
    return render_template('base_admin.html', name=session.get('admin_name'))


# 管理员-图书管理-添加书籍-新书入库   √
@main.route('/add_new_book', methods=['GET', 'POST'])
@login_required
def add_new_book():
    form = AddNewBookForm()
    if form.validate_on_submit():
        book_id = request.form.get('book_id')
        exist_id = Book.query.filter_by(book_id=book_id).first()
        if exist_id is None:
            book = Book()
            book.book_id = request.form.get('book_id')
            book.book_name = request.form.get('book_name')
            book.author = request.form.get('author')
            book.average_rating = 0.0
            book.publish_date = request.form.get('publish_date')
            book.publish_name = request.form.get('publish_name')
            book.price = request.form.get('price')
            book.store_number = request.form.get('store_number')
            book.detail = request.form.get('detail')
            db.session.add(book)
            db.session.commit()
            flash(u'新书入库成功！')
            return redirect(url_for('main.add_new_book'))
        else:
            flash(u'图书已存在，请直接进行库存更新操作！')
            return redirect(url_for('main.add_book_store'))

    return render_template('/Admin/add_new_book.html', name=session.get('admin_name'), form=form)


# 管理员-图书管理-添加书籍-库存补充   √
@main.route('/add_book_store', methods=['GET', 'POST'])
@login_required
def add_book_store():
    form = AddBookStoreForm()
    if form.validate_on_submit():
        book_id = request.form.get('book_id')
        exist_id = Book.query.filter_by(book_id=book_id).first()
        if exist_id is not None:  # 书在库存内仍有数目
            # 产生新的bar_id 确保产生的bar_id作为主键是唯一的
            new_bar_id = np.random.randint(0, 50000000)
            exist_bar_id = Inventory.query.filter_by(bar_id=new_bar_id).first()
            while (exist_bar_id is not None):
                new_bar_id = np.random.randint(0, 50000000)
                exist_bar_id = Inventory.query.filter_by(bar_id=new_bar_id).first()
            # 新建inventory清单，加入库存操作清单的数据库表
            newstore = Inventory()
            newstore.bar_id = new_bar_id
            newstore.book_id = request.form.get('book_id')
            newstore.location = request.form.get('location')
            newstore.storage_number = request.form.get('number')
            newstore.storage_date = session['admin_id']  # 需要改成时间类型，再议！！！！！
            newstore.admin_id = session['admin_id']

            # 将图书库存管理信息更改至图书表的剩余库存中
            book = Book.query.filter_by(book_id=book_id).first()
            operation_num = int(newstore.storage_number)
            store_num = int(book.store_number)
            # 库中没有多余的书删除
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
    return render_template('/Admin/add_book_store.html', name=session.get('admin_name'), form=form)


# 管理员-图书管理-修改图书基本信息   √
# （含编辑和删除）（涉及库存的不能直接更改）
@main.route('/modify_book', methods=['GET', 'POST'])
@login_required
def modify_book():
    form = SearchBookForm()
    # 利用ajax传值获取信息进行后台操作，放到delete_book和edit_book中
    return render_template('/Admin/modify_book.html', name=session.get('admin_name'), form=form)

#管理员-图书管理-修改图书详情页
@main.route('/change_book_info', methods=['GET', 'POST'])
@login_required
def change_book_info():
    if request.method == 'POST':
        data = ''
        book_id = session['book_id']
        book = Book.query.filter_by(book_id=book_id).first()

        book_name = request.values.get("book_name")
        author = request.values.get("author")
        price = request.values.get("price")
        store_number = request.values.get("store_number")
        publish_name = request.values.get("publish_name")
        publish_date = request.values.get("publish_date")
        detail = request.values.get("detail")
        if int(store_number) >= 0:
            book.book_name = book_name
            book.author = author
            book.price = price
            book.store_number = store_number
            book.publish_name = publish_name
            book.publish_date = publish_date
            book.detail = detail
            db.session.commit()
            data = 'ok'
        return jsonify(data);
    else:
        book_id = request.args.get('book_id')
        book = Book.query.filter_by(book_id=book_id).first()
        session['book_id'] = book_id
        return render_template('/Admin/book_info.html',name=session.get('admin_name'),book=book)

# 管理员-图书管理-修改图书基本信息
# 删除图书
@main.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    data = ''
    if request.method == 'POST':
        book_id = request.values.get('book_id')
        book = Book.query.filter_by(book_id=book_id).first()
        if book is not None:
            db.session.delete(book)
            db.session.commit()
            data = 'success'
    return jsonify(data)


# 管理员-图书管理-修改图书基本信息
# 编辑图书
@main.route('/edit_book', methods=['GET', 'POST'])
@login_required
def edit_book():
    data = ''
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


# 管理员-显示订单信息   √
@main.route('/list_order_info', methods=['GET', 'POST'])
@login_required
def list_order_info():
    return render_template('/Admin/list_order_info.html', name=session.get('admin_name'))


# 管理员-搜索订单信息返回前端显示
@main.route('/search_order', methods=['GET', 'POST'])
@login_required
def search_order():
    data = []
    orders = Orders.query.all()
    for order in orders:
        book_id = order.book_id
        book = Book.query.filter_by(book_id=book_id).first()
        user_id = order.user_id
        user_name = User.query.filter_by(user_id=user_id).first().user_name
        if book is not None:
            book_name = book.book_name
            book_price = book.price
            item = {
                'order_id': order.order_id,
                'book_id': book_id,
                'book_name': book_name,
                'user_id': user_id,
                'user_name': user_name,
                'buy_number': order.buy_number,
                'buy_date': order.buy_date,
                'price': book_price,
                'total_price': order.total_price
            }
            data.append(item)

    return jsonify(data)


# 管理员-显示历史库存操作记录   √
@main.route('/list_add_operation', methods=['GET', 'POST'])
@login_required
def list_add_operation():
    return render_template('/Admin/list_add_operation.html', name=session.get('admin_name'))


# 搜索库存操作的记录数据返还给前端显示
@main.route('/search_operation', methods=['GET', 'POST'])
@login_required
def search_operation():
    data = []
    # 查询到的库存操作的operations列表, 按照操作员id升序排序
    operations = Inventory.query.order_by(Inventory.admin_id).all()
    for op in operations:
        book_id = op.book_id
        book_name = Book.query.filter_by(book_id=book_id).first().book_name
        admin_id = op.admin_id
        admin_name = Admin.query.filter_by(admin_id=admin_id).first().admin_name
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


# 管理员-用户管理-用户删除   √
@main.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = SearchUserForm()
    return render_template('/Admin/delete_user.html', name=session.get('admin_name'), form=form)


# 管理员-删除用户
@main.route('/del_user', methods=['GET', 'POST'])
@login_required
def del_user():
    data = ''
    if request.method == 'POST':
        user_id = request.values.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        if user is not None:
            db.session.delete(user)
            db.session.commit()
            data = 'success'
    return jsonify(data)


# 管理员-用户管理-用户信息查询   √
@main.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():
    form = SearchUserForm()
    return render_template('/Admin/search_user.html', name=session.get('admin_name'), form=form)


# 直接返回前台显示查询用户(基本)信息的结果
@main.route('/list_user', methods=['GET', 'POST'])
@login_required
def list_user():
    data = []
    users = User.query.all()
    for user in users:
        user_id = user.user_id
        item = {
            # 用户信息
            'user_id': user_id,
            'user_name': user.user_name,
            'sex': user.sex,
            'age': user.age,
            'local': user.local,
            'password': user.password
        }
        data.append(item)
    return jsonify(data)


# 直接返回前台显示查询用户(包括订单)信息的结果
@main.route('/list_user_info', methods=['GET', 'POST'])
@login_required
def list_user_info():
    data = []
    users = User.query.all()
    for user in users:
        user_id = user.user_id
        orders = Orders.query.filter_by(user_id=user_id).all()
        if len(orders) != 0:
            for order in orders:
                book_id = order.book_id
                book = Book.query.filter_by(book_id=book_id).first()
                book_name = book.book_name
                book_price = book.price
                user_name = User.query.filter_by(user_id=user_id).first().user_name
                item = {
                    'user_id': user_id,
                    'user_name': user_name,
                    'sex': user.sex,
                    'age': user.age,
                    'local': user.local,
                    'password': user.password,
                    'order_id': order.order_id,
                    'book_id': book_id,
                    'book_name': book_name,
                    'buy_number': order.buy_number,
                    'buy_date': order.buy_date,
                    'price': book_price,
                    'total_price': order.total_price
                }
                data.append(item)
        else:
            item = {
                # 用户信息
                'user_id': user_id,
                'user_name': user.user_name,
                'sex': user.sex,
                'age': user.age,
                'local': user.local,
                'password': user.password,
                'order_id': '——',
                'book_id': '——',
                'book_name': '——',
                'buy_number': '——',
                'buy_date': '——',
                'price': '——',
                'total_price': '——'
            }
            data.append(item)
    return jsonify(data)


# 根据用户信息查询用户及其订单等信息并返回前台显示查询结果
@main.route('/find_user', methods=['GET', 'POST'])
@login_required
def find_user():
    content = request.form.get('content')  # 表单中提交过来的，一定非None，故接下来不用判断了

    # 分别根据content内容进行数据库查询
    def find_user_id():
        return User.query.filter(User.user_id.contains(content)).all()

    def find_user_name():
        return User.query.filter(User.user_name.like('%' + content + '%')).all()

    def find_age():
        return User.query.filter(User.age == content).all()

    def find_local():
        return User.query.filter(User.local.like('%' + content + '%')).all()

    # 不带括号的函数调用，如a=find_XXX，则a代表函数体而非结果，是一个函数对象，不须等该函数执行完成。
    methods = {
        'user_id': find_user_id,
        'user_name': find_user_name,
        'age': find_age,
        'local': find_local
    }
    method = request.form.get('method')
    # 根据类别查询到的有关用户的user列表
    users = methods[method]()  # 加上()即调用了函数，返回的是结果了，即返回了列表
    data = []
    for user in users:
        user_id = user.user_id
        item = {
            # 用户信息
            'user_id': user_id,
            'user_name': user.user_name,
            'sex': user.sex,
            'age': user.age,
            'local': user.local,
            'password': user.password
        }
        data.append(item)
    return jsonify(data)


###########################用户功能区#############################


# 用户-注册   √
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
        """
        #用户id若不是自增需要随机产生
        user_id = np.random.randint(0, 100000)
        # 确保产生的user_id作为主键是唯一的
        exist_id = User.query.filter_by(user_id=user_id).first()
        while (exist_id is not None):
            user_id = np.random.randint(0, 100000)
            exist_id = User.query.filter_by(user_id=user_id).first()
        """
        # 产生新用户，并插入数据库
        new_user = User(name, sex, age, local, pwd)
        if new_user.verify_password(pwd2) is True:
            # db是SQLAlchemy()实例化对象，用于数据库操作
            db.session.add(new_user)
            db.session.commit()
            flash("注册成功！")
            # 放入login_user中，否则会由于login_manage程序跳转到登录界面
            login_user(new_user)
            session['user_id'] = new_user.user_id
            session['user_name'] = new_user.user_name
            return redirect(url_for('main.base_user'))
        else:
            flash("两次密码不一致！")
            return redirect(url_for('main.register'))
    return render_template('/User/register.html', form=form)


# 用户登录后的主页   √
@main.route('/base_user', methods=['GET', 'POST'])
@login_required
def base_user():
    return render_template('base_user.html', name=session.get('user_name'))


# 图书商城
@main.route('/book_shop', methods=['GET', 'POST'])
@login_required
def book_shop():
    books = Book.query.all()
    return render_template('/User/book_shop.html', name=session.get('user_name'), books=books)


# 图书详情页
@main.route('/book_info', methods=['GET', 'POST'])
@login_required
def book_info():
    book_id = request.args.get('book_id')
    session['book_id'] = book_id  # 将book_id加入当前session
    book = Book.query.filter_by(book_id=book_id).first()
    user_id = session['user_id']
    favorite = Favorite.query.filter_by(user_id=user_id).all()
    loves = []
    for favor in favorite:
        loves.append(favor.book_id)

    love = '0'
    if book_id in loves:
        love = '1'
    else:
        love = '0'
    return render_template('/User/book_info.html', name=session.get('user_name'), book=book, love=love)


# 查看/发表评论
@main.route('/show_comment', methods=['GET', 'POST'])
@login_required
def show_comment():
    book_id = session['book_id']
    book = Book.query.filter_by(book_id=book_id).first()
    discuss = Comment.query.filter_by(book_id=book_id).all()
    comments = []
    for dis in discuss:
        comment_user_id = dis.user_id
        comment_user = User.query.filter_by(user_id=comment_user_id).first()
        item = {
            "user_id": comment_user_id,
            "user_name": comment_user.user_name,
            "comment_time": dis.comment_time,
            "comment": dis.comment
        }
        comments.append(item)
    return render_template('/User/show_comment.html', comments=comments, book=book)


# 添加对book的评论
@main.route('/add_comment', methods=['GET', 'POST'])
@login_required
def add_comment():
    data = ''
    if request.method == 'POST':
        user_id = session['user_id']
        book_id = session['book_id']
        comment_content = request.values.get('comment')
        discuss = Comment()
        discuss.user_id = user_id
        discuss.book_id = book_id
        discuss.comment = comment_content
        discuss.comment_time = 'suibian-test'
        db.session.add(discuss)
        db.session.commit()
        data = 'ok'
    return jsonify(data)


# 添加到书架（收藏）
@main.route('/add_favorite', methods=['GET', 'POST'])
@login_required
def add_favorite():
    data = ''
    if request.method == 'POST':
        book_id = session['book_id']
        user_id = session['user_id']
        flag = request.values.get('love')
        if flag == '1':
            love = Favorite()
            love.book_id = book_id
            love.user_id = user_id

            db.session.add(love)
            db.session.commit()
            data = 'add'
            # flash(u'添加收藏成功')
        elif flag == '0':
            condition1 = (Favorite.book_id == book_id)
            condition2 = (Favorite.user_id == user_id)
            love = Favorite.query.filter(and_(condition1, condition2)).first()

            db.session.delete(love)
            db.session.commit()
            data = 'cancel'
            # flash(u'取消收藏成功')
    return jsonify(data)


# 点击后创建订单并返回给前端
@main.route('/create_order', methods=['GET', 'POST'])
@login_required
def create_order():
    # 产生order_id
    # id若不是自增需要随机产生
    order_id = np.random.randint(0, 1000000)
    # 确保产生的order_id作为主键是唯一的
    exist_id = Orders.query.filter_by(order_id=order_id).first()
    while (exist_id is not None):
        order_id = np.random.randint(0, 1000000)
        exist_id = Orders.query.filter_by(order_id=order_id).first()
    session['order_id'] = order_id
    book_id = session['book_id']
    book = Book.query.filter_by(book_id=book_id).first()

    order = Orders()
    order.order_id = order_id
    order.user_id = session['user_id']
    order.book_id = book_id
    order.buy_number = 0
    order.total_price = float(book.price) * int(order.buy_number)
    order.buy_date = 'test'
    order.local = ''
    # 此时不能加入数据库
    item = {
        # 图书信息
        'book_id': book_id,
        'book_name': book.book_name,
        'author': book.author,
        'price': book.price,
        'average_rating': book.average_rating,
        'publish_name': book.publish_name,
        'publish_date': book.publish_date,
        'store_number': book.store_number,
        'detail': book.detail,
        # 订单信息
        'order_id': order_id,
        'buy_number': order.buy_number,
        'buy_date': order.buy_date,
        'total_price': order.total_price,
        'local': order.local
    }
    return jsonify(item)


# 下订单页
@main.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    return render_template('/User/add_order.html', name=session['user_name'])


# 订单详情页
@main.route('/order_info', methods=['GET', 'POST'])
@login_required
def order_info():
    order_id = request.args.get('order_id')
    order = Orders.query.filter_by(order_id=order_id).first()
    session['order_id'] = order_id
    session['book_id'] = order.book_id
    return render_template('/User/order_info.html', name=session['user_name'], order=order)


# 获取订单信息
@main.route('/get_order_info', methods=['GET', 'POST'])
@login_required
def get_order_info():
    book_id = session['book_id']
    order_id = session['order_id']
    book = Book.query.filter_by(book_id=book_id).first()
    order = Orders.query.filter_by(order_id=order_id).first()
    item = {
        # 图书信息
        'book_id': book_id,
        'book_name': book.book_name,
        'author': book.author,
        'price': book.price,
        'average_rating': book.average_rating,
        'publish_name': book.publish_name,
        'publish_date': book.publish_date,
        'store_number': book.store_number,
        'detail': book.detail,
        # 订单信息
        'order_id': order_id,
        'buy_number': order.buy_number,
        'buy_date': order.buy_date,
        'total_price': order.total_price,
        'local': order.local
    }
    return jsonify(item)


# 表单中修改订单（数量+配送地址）
@main.route('/modify_my_order', methods=['GET', 'POST'])
@login_required
def modify_my_order():
    data = ''
    if request.method == 'POST':
        book_id = session['book_id']
        order_id = session['order_id']
        user_id = session['user_id']
        book = Book.query.filter_by(book_id=book_id).first()
        order = Orders.query.filter_by(order_id=order_id).first()

        local = request.values.get('local')
        want_buy_number = request.values.get('buy_number')
        left_store = int(book.store_number)

        if order is None:
            if book is None:
                # flash('该图书已经被管理员下架，订单失效！')
                data = 'case1'
            else:
                if int(want_buy_number) <= int(left_store):
                    new_order = Orders()
                    new_order.order_id = order_id
                    new_order.user_id = user_id
                    new_order.book_id = book_id
                    new_order.buy_date = 'test'
                    new_order.buy_number = want_buy_number
                    new_order.local = local
                    new_order.total_price = int(want_buy_number) * float(book.price)
                    db.session.add(new_order)
                    db.session.commit()
                    data = 'ok1'
                else:
                    # 购买的大于库存
                    # flash('库存不足，无法提供所需数目的图书')
                    data = 'case2'
        else:
            old_want_buy_number = order.buy_number
            opera_num = int(want_buy_number) - int(old_want_buy_number)
            if int(opera_num) > int(left_store):
                # 购买的大于库存
                # flash('库存不足，无法提供所需数目的图书')
                data = 'case2'
            else:
                if int(opera_num) < 0:
                    # 返还书籍入库
                    book.store_number = left_store + abs(int(opera_num))
                elif int(opera_num) == int(left_store):
                    # 全部购买，不能直接删除书籍
                    book.store_number = 0
                else:
                    book.store_number = left_store - abs(int(opera_num))

                order.buy_number = want_buy_number
                order.local = local
                order.total_price = int(want_buy_number) * float(book.price)
                db.session.commit()
                data = 'ok2'
                db.session.commit()
    return jsonify(data)


# 列表中编辑修改订单
@main.route('/edit_order', methods=['GET', 'POST'])
@login_required
def edit_order():
    data = ''
    if request.method == 'POST':
        order_id = request.values.get('order_id')
        field = request.values.get('edit_field')
        value = request.values.get('new_value')
        order = Orders.query.filter_by(order_id=order_id).first()
        old_value = order.buy_number
        if order is not None:
            book_id = order.book_id
            book = Book.query.filter_by(book_id=book_id).first()
            if book is None:
                # flash('该图书已经被管理员下架，订单失效！')
                data = 'case1'
                db.session.delete(order)
                db.session.commit()
            elif field == 'buy_number':
                price = book.price
                left_store = book.store_number
                opera_num = int(value) - int(old_value)
                if int(opera_num) > int(left_store):
                    # 购买的大于库存
                    # flash('库存不足，无法提供所需数目的图书')
                    data = 'case2'
                else:
                    if int(opera_num) < 0:
                        # 返还书籍入库
                        book.store_number = left_store + abs(int(opera_num))
                    elif int(opera_num) == int(left_store):
                        # 全部购买，不能直接删除书籍
                        book.store_number = 0
                    else:
                        book.store_number = left_store - abs(int(opera_num))

                    order.buy_number = value
                    order.total_price = int(value) * float(price)
                    db.session.commit()
                    data = 'ok'
            elif field == 'local':
                order.local = value;
                db.session.commit()
                data = 'ok'

    return jsonify(data)


# 获取图书信息
@main.route('/get_book_info', methods=['GET', 'POST'])
@login_required
def get_book_info():
    book_id = session['book_id']
    book = Book.query.filter_by(book_id=book_id).first()
    item = {
        # 图书信息
        'book_id': book_id,
        'book_name': book.book_name,
        'author': book.author,
        'price': book.price,
        'average_rating': book.average_rating,
        'publish_name': book.publish_name,
        'publish_date': book.publish_date,
        'store_number': book.store_number,
        'detail': book.detail
    }
    return jsonify(item)


# 我的账户-查看用户个人信息（可编辑修改基本信息，不含密码的修改）  √
@main.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    form = UserInfoForm()
    user_id = session['user_id']
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        f = request.files["files"]
        base_path = os.getcwd()
        app_path = os.path.join(base_path, 'app/')
        static_path = os.path.join(app_path, 'static/')
        upload_path = os.path.join(static_path,'users/')
        file_path = upload_path + secure_filename(f.filename)
        #保存文件
        f.save(file_path)
        #删除原来图片
        os.remove(upload_path + user.photo)
        user.photo = f.filename
        db.session.add(user)
        db.session.commit()
    return render_template('/User/user_info.html', name=session.get('user_name'), form=form, user=user)


# 我的账户-查看用户个人信息（可编辑修改基本信息，不含密码的修改）  √
@main.route('/my_books', methods=['GET', 'POST'])
@login_required
def my_books():
    user_id = session['user_id']
    favorite_books = Favorite.query.filter_by(user_id=user_id).all()
    favor_books = []
    for favor in favorite_books:
        book = Book.query.filter_by(book_id=favor.book_id).first()
        item = {
            "book_id": book.book_id,
            "book_name": book.book_name,
            "author": book.author,
            'price': book.price,
            'average_rating': book.average_rating,
            'publish_name': book.publish_name,
            'publish_date': book.publish_date,
            'store_number': book.store_number,
            'detail': book.detail
        }
        favor_books.append(item)

    order_books = Orders.query.filter_by(user_id=user_id).all()
    buy_books = []
    for buy in order_books:
        book = Book.query.filter_by(book_id=buy.book_id).first()
        item = {
            "book_id": book.book_id,
            "book_name": book.book_name,
            "author": book.author,
            'price': book.price,
            'average_rating': book.average_rating,
            'publish_name': book.publish_name,
            'publish_date': book.publish_date,
            'store_number': book.store_number,
            'detail': book.detail
        }
        buy_books.append(item)
    return render_template('/User/my_books.html', favor_books=favor_books, buy_books=buy_books)


# 我的账户-根据用户id返回个人信息数据给前台（可编辑修改基本信息，不含密码的修改）
@main.route('/get_my_info', methods=['GET', 'POST'])
@login_required
def get_my_info():
    user_id = session['user_id']
    user = User.query.filter_by(user_id=user_id).first()
    item = {
        # 用户信息
        'user_id': user_id,
        'user_name': user.user_name,
        'sex': user.sex,
        'age': user.age,
        'local': user.local,
        'password': user.password
    }
    return jsonify(item)


# 我的账户-获取修改后的个人信息数据
@main.route('/modify_my_info', methods=['GET', 'POST'])
@login_required
def modify_my_info():
    data = ''
    if request.method == 'POST':
        user_id = session['user_id']
        user = User.query.filter_by(user_id=user_id).first()
        user.user_name = request.values.get('user_name')
        user.sex = request.values.get('sex')
        user.age = request.values.get('age')
        user.local = request.values.get('local')
        db.session.add(user)
        db.session.commit()
        data = 'success'
    return jsonify(data)


# 我的账户-查看用户订单信息（可编辑修改订单购买数量和删除订单）  √
@main.route('/all_order_info', methods=['GET', 'POST'])
@login_required
def all_order_info():
    return render_template('/User/all_order_info.html', name=session.get('user_name'))


# 将搜索到的用户的订单信息返回前台
@main.route('/list_order', methods=['GET', 'POST'])
@login_required
def list_order():
    data = []
    user_id = session['user_id']
    orders = Orders.query.filter_by(user_id=user_id).all()
    for order in orders:
        book_id = order.book_id
        book = Book.query.filter_by(book_id=book_id).first()
        if book is not None:
            book_name = book.book_name
            book_price = book.price
            user_name = User.query.filter_by(user_id=user_id).first().user_name
            item = {
                'order_id': order.order_id,
                'book_id': book_id,
                'book_name': book_name,
                'user_id': user_id,
                'user_name': user_name,
                'buy_number': order.buy_number,
                'buy_date': order.buy_date,
                'price': book_price,
                'total_price': order.total_price,
                'local': order.local
            }
            data.append(item)
    return jsonify(data)


# 删除订单
@main.route('/delete_order', methods=['GET', 'POST'])
@login_required
def delete_order():
    data = ''
    if request.method == 'POST':
        order_id = request.values.get('order_id')
        order = Orders.query.filter_by(order_id=order_id).first()
        if order is not None:
            # 回退库存数目
            book_id = order.book_id
            number = order.buy_number
            book = Book.query.filter_by(book_id=book_id).first()
            book.store_number = book.store_number + number

            db.session.delete(order)
            db.session.commit()
            data = 'success'
    return jsonify(data)


# 我的账户-修改用户的密码    √
@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.password.data != form.password2.data:
        flash(u'两次密码不一致！')
    if form.validate_on_submit():
        if form.password.data == form.old_password.data:
            flash(u'新密码与原密码一致！')
            return redirect(url_for('main.base_user'))
        user_id = session['user_id']
        user = User.query.filter_by(user_id=user_id).first()
        if user.verify_password(form.old_password.data):
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash(u'已成功修改密码！')
            return redirect(url_for('main.base_user'))
        else:
            flash(u'原密码输入错误，修改失败！')
    return render_template('/User/change_password.html', name=session.get('user_name'), form=form)


##############################用户/管理员公用区##############################


# 用户/管理员-登录   √
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # 等价于if form.validate_on_submit():
    if form.validate_on_submit():
        name = form.user_name.data
        pwd = form.password.data
        user_tmp1 = User.query.filter_by(user_name=name, password=pwd).first()
        user_tmp2 = Admin.query.filter_by(admin_name=name, password=pwd).first()
        # 在User和Admin表中均未找到，则说明输入无效
        if user_tmp1 is None and user_tmp2 is None:
            flash('账号或密码错误！')
            return redirect(url_for('main.login'))
        # 在用户表中匹配到
        if user_tmp1 is not None:
            login_user(user_tmp1)
            session['user_id'] = user_tmp1.user_id
            session['user_name'] = user_tmp1.user_name
            flash("用户登录成功！")
            return redirect(url_for('main.base_user'))
        # 在管理员表中匹配到
        elif user_tmp2 is not None:
            login_user(user_tmp2)
            session['admin_id'] = user_tmp2.admin_id
            session['admin_name'] = user_tmp2.admin_name
            flash("管理员登录成功！")
            return redirect(url_for('main.base_admin'))
    return render_template('login.html', form=form)


# 用户/管理员-注销   √
@main.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.login'))


# 测试页面
@main.route("/test", methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        f = request.files["files"]
        base_path = getcwd()
        f_path = path.join(base_path, 'app/')
        upload_path = path.join(f_path, 'static/')
        file_name = upload_path + secure_filename(f.filename)
        f.save(file_name)

    return render_template('/User/test.html')
