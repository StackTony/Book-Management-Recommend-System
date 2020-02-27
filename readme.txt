基于python3和mysql的图书推荐管理系统

运行环境：python 3.7

数据库：MySQL

框架：后端使用flask框架，基于蓝图方式开发；前端采用layui框架

运行方式：首先创建相应的mysql数据库，运行models.py连接数据库，并创建表；然后运行manage.py文件，访问http://127.0.0.1:5000/ 即可

一、数据库表

读者用户表 User *用户编号ID（主） *姓名 *性别 *年龄 *位置信息 *密码

管理员表 Admin *管理员编号ID（主） *姓名 *密码

书籍表 Book *书籍编号ID（主） *图书名 *作者 *出版日期 *出版社 *图书价格

评分表 Rating *评分编号ID（主） *用户编号ID（外） *图书编号ID（外） *评分

订单表 Cart *订单编号ID（主） *用户编号ID（外） *图书编号ID（外） *订购数量 *总价

二、文件框架

-app #程序的主要依赖文件，采用MTV模式

-—— main #主文件夹

-———— init.py

-———— view.py #视图

-———— form.py #表单

-—— static #存放css、js等文件

-—— templates #存放静态html文件

-—— init.py

-—— models.py #数据库表

-data #存放数据的文件夹

-tests #存放测试文件的文件夹

-config.py #配置信息文件

-manage.py #运行app的入口文件

三、各个功能使用方法

四、运行效果演示图