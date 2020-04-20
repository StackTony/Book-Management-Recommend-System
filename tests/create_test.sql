SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

delete from orders where orders.buy_number = 0;
delete from book where book.average_rating = 0;


insert into admin values(1,'lkj','lkj');

insert into book values('1234567890001', 'three body', 'lcx', 9.9, '2016-03-29', 'kehuan', 10.0, 10,'book_icon.jpg','三体，写在基石之前，科幻巨制');
insert into book values('1234567890002', 'three bodyII', 'lcx', 10, '2016-03-29', 'kehuan', 12.0, 10,'book_icon.jpg','给岁月以文明，给时光以生命');
insert into book values('1234567890003', 'three bodyIII', 'lcx', 10.0, '2016-03-29', 'kehuan', 11.0, 10,'book_icon.jpg','蓝色空间号');
insert into book values('1234567890004', 'test-book1', 'lkj', 2.4, '2016-03-29', 'kehuan', 21.0, 10,'1.jpg','sladkalksjdfalksd');
insert into book values('1234567890005', 'test-book2', 'lkj', 6.4, '2016-03-29', 'kehuan', 30.0, 10,'1.jpg','1234567890123456789012345678901234567890');
insert into book values('1234567890006', 'test-book3', 'lkj', 7.4, '2016-03-29', 'kehuan', 1.0, 10,'1.jpg','mmp');

insert into user values(1,'sdf','男',11,'haiyang','sdf', '');
insert into user values(2,'kkk','男',11,'haiyang','kkk', '');

insert into comments values(1,2,'1234567890001','我对三体世界说话！','2020');
insert into comments values(2,2,'1234567890001','自然选择，前进四！','2020');

select * from book;
select * from comments;
select * from favorite;
select * from orders;
select * from rating;
select * from user;