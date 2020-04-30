import xlrd

xlrd.Book.encoding = "utf-8"
books_file = "C:\\Users\\lkj\\Desktop\\Python\\Projects\\Book-Management-System\\data\\douban\\booksInfo.xls"
data=xlrd.open_workbook(books_file)
table=data.sheets()[0]
nrows=table.nrows   #行数
ncols=table.ncols   #列数
#print(data.index)#获取行的索引名称
#print(data.columns)#获取列的索引名称
#print(data['书籍名'])#获取列名为姓名这一列的内容
colnameindex=0
colnames=table.row_values(colnameindex)   #首行列名写入数组
book_name = []
book_id = []
author = []
publish_date = []
publish_name = []
average_rating = []
book_photo = []
for i in range(1,nrows):
    book_name.append(table['书籍名'][i])
    book_id.append(table['URL入口'][i][31:38])
print(book_id,"  ",book_name)