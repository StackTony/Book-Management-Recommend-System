# -*- coding: utf-8 -*-
#定义表单
from flask_wtf import FlaskForm, validators
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField, FloatField
from wtforms.validators import DataRequired, EqualTo, Length

# DataRequired对字段进行限制之后，如果我们限制填写的字段为空，将无法提交表单。
# Length对字段长度进行限制，如果我们限制填写的字段长度不在1~32个字符之内，将无法提交表单。
# EqualTo常用来判断两个字段是否相等，它含有两个参数，参数1是字段2的名称，参数2是当两个字段不相等时给出的提示信息：


#用户/管理员-登录表单
class LoginForm(FlaskForm):
    user_name = StringField(u'用户名', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'登录')

#用户-注册表单
class RegisterForm(FlaskForm):
    user_name = StringField(u'用户名', validators=[DataRequired()])
    #methods = [('男', '男'), ('女', '女')]
    #sex = SelectField(u'性别', choices=methods, validators=[DataRequired()], coerce=str)
    sex = StringField(u'性别', validators=[DataRequired()])
    age = IntegerField(u'年龄', validators=[DataRequired()])
    local = StringField(u'位置', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'两次密码必须一致！')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

#用户-修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'原密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[DataRequired(), EqualTo('password2', message=u'两次密码必须一致！')])
    password2 = PasswordField(u'确认新密码', validators=[DataRequired()])
    submit = SubmitField(u'确认修改')

#用户/管理员-搜索图书表单
class SearchBookForm(FlaskForm):
    #类别
    methods = [('book_id', '图书编号'), ('book_name', '图书名'), ('author', '作者'),
               ('publish_date', '出版日期'), ('average_rating','评分'), ('price','价格')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    #查询内容
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')

#管理员-搜索用户表单
class SearchUserForm(FlaskForm):
    # 类别
    methods = [('user_id', '用户编号'), ('user_name', '用户名'), ('age', '年龄'), ('local', '位置')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    # 查询内容
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')

#管理员-添加书籍-新书入库表单
class AddNewBookForm(FlaskForm):
    book_id = StringField(validators=[DataRequired(), Length(13)])
    book_name = StringField(validators=[DataRequired(), Length(1, 64)])
    author = StringField(validators=[DataRequired(), Length(1, 64)])
    publish_date = StringField(validators=[DataRequired(), Length(1, 64)])
    publish_name = StringField(validators=[DataRequired(), Length(1, 64)])
    price = FloatField(validators=[DataRequired()])
    submit = SubmitField(u'添加')

#管理员-添加书籍-库存更新表单
class AddBookStoreForm(FlaskForm):
    book_id = StringField(validators=[DataRequired(), Length(13)])
    number = IntegerField(validators=[DataRequired()]) #可正可负
    location = StringField(validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'添加')
