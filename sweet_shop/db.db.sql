BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "assembling" (
	"ID"	INTEGER NOT NULL,
	"order_id"	INTEGER,
	"telegram_id"	INTEGER,
	"due_date"	TEXT,
	"id_status"	INTEGER,
	PRIMARY KEY("ID"),
	FOREIGN KEY("id_status") REFERENCES "orders_status"("id_status"),
	FOREIGN KEY("order_id") REFERENCES "orders"("id"),
	FOREIGN KEY("telegram_id") REFERENCES "users"("telegram_id")
);
CREATE TABLE IF NOT EXISTS "orders" (
	"id"	INTEGER NOT NULL,
	"order_number"	TEXT,
	"articul"	TEXT,
	"product_name"	TEXT,
	"quantity"	TEXT,
	"unit"	TEXT,
	"unit_price"	TEXT,
	"recipient_name"	TEXT,
	"phone"	TEXT,
	"city"	TEXT,
	"street"	TEXT,
	"house_number"	TEXT,
	"apartment"	TEXT,
	"courier_delivery"	TEXT,
	"payment_method"	TEXT,
	"order_date"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "orders_status" (
	"id_status"	INTEGER NOT NULL,
	"status"	TEXT,
	PRIMARY KEY("id_status")
);
CREATE TABLE IF NOT EXISTS "products" (
	"id_articul"	TEXT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY("id_articul")
);
CREATE TABLE IF NOT EXISTS "purchase_goods" (
	"id"	INTEGER NOT NULL,
	"id_articul"	TEXT,
	"quantity"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("id_articul") REFERENCES "products"("id_articul")
);
CREATE TABLE IF NOT EXISTS "users" (
	"telegram_id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"role_id"	INTEGER NOT NULL,
	"login"	TEXT,
	"password"	TEXT,
	"isFree"	INTEGER NOT NULL DEFAULT 'Y',
	PRIMARY KEY("telegram_id"),
	FOREIGN KEY("role_id") REFERENCES "users_role"("Id_role")
);
CREATE TABLE IF NOT EXISTS "users_role" (
	"Id_role"	INTEGER,
	"role"	TEXT
);
INSERT INTO "assembling" VALUES (1,1,5872788846,NULL,3);
INSERT INTO "assembling" VALUES (2,4,1212333959,NULL,2);
INSERT INTO "assembling" VALUES (16,16,192837465,'1 час',1);
INSERT INTO "assembling" VALUES (24,13,192837465,'1 час',1);
INSERT INTO "assembling" VALUES (25,19,1,'1 час',1);
INSERT INTO "orders" VALUES (1,'ZAK-50001','F10001','Чай Пуэр выдержанный (1 кг)','1','уп.','6 500','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','21.06.2025');
INSERT INTO "orders" VALUES (2,'ZAK-50001','F10002','Кофе в зёрнах Colombia Premium (2 кг)','2','уп.','5 500','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','21.06.2025');
INSERT INTO "orders" VALUES (3,'ZAK-50001','F10003','Мёд Алтайский горный (3 л)','1','банка','7 200','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','21.06.2025');
INSERT INTO "orders" VALUES (4,'ZAK-50002','F10004','Орех грецкий очищенный (5 кг)','1','мешок','5 800','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','21.06.2025');
INSERT INTO "orders" VALUES (5,'ZAK-50002','F10005','Миндаль сырой (4 кг)','1','мешок','6 100','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','21.06.2025');
INSERT INTO "orders" VALUES (6,'ZAK-50002','F10006','Финики без косточек (10 кг)','1','короб','5 500','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','21.06.2025');
INSERT INTO "orders" VALUES (7,'ZAK-50001','F10001','Чай Пуэр выдержанный (1 кг)','1','уп.','6 500 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (8,'ZAK-50001','F10002','Кофе в зёрнах Colombia Premium (2 кг)','2','уп.','5 500 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (9,'ZAK-50001','F10003','Мёд Алтайский горный (3 л)','1','банка','7 200 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (10,'ZAK-50002','F10004','Орех грецкий очищенный (5 кг)','1','мешок','5 800 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (11,'ZAK-50002','F10005','Миндаль сырой (4 кг)','1','мешок','6 100 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (12,'ZAK-50002','F10006','Финики без косточек (10 кг)','1','короб','5 500 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (13,'ZAK-50003','F10007','Рис жасмин (10 кг)','1','мешок','5 300 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (14,'ZAK-50003','F10008','Макароны итальянские (12 кг)','1','ящик','6 000 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (15,'ZAK-50003','F10009','Тушёнка говяжья ГОСТ (10 банок)','1','упаковка','7 000 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (16,'ZAK-50004','F10010','Консервы рыбные (ассорти, 15 банок)','1','ящик','5 200 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (17,'ZAK-50004','F10011','Паштет мясной (24 шт.)','1','ящик','5 100 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (18,'ZAK-50004','F10012','Кукуруза консерв. (12 банок)','1','упаковка','5 300 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (19,'ZAK-50005','F10013','Гречка высший сорт (15 кг)','1','мешок','6 500 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders" VALUES (20,'ZAK-50005','F10014','Сгущёнка ГОСТ (20 банок)','1','упаковка','5 800 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders" VALUES (21,'ZAK-50005','F10015','Оливковое масло Extra Virgin (5 л)','2','бут.','5 900 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders" VALUES (22,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "orders" VALUES (23,'ZAK-50001','F10001','Чай Пуэр выдержанный (1 кг)','1','уп.','6 500 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (24,'ZAK-50001','F10002','Кофе в зёрнах Colombia Premium (2 кг)','2','уп.','5 500 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (25,'ZAK-50001','F10003','Мёд Алтайский горный (3 л)','1','банка','7 200 ₽','Иванов И.И.','79991112233','Москва','Ленина','10','15','Да','Онлайн','2025-06-25 00:00:00');
INSERT INTO "orders" VALUES (26,'ZAK-50002','F10004','Орех грецкий очищенный (5 кг)','1','мешок','5 800 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (27,'ZAK-50002','F10005','Миндаль сырой (4 кг)','1','мешок','6 100 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (28,'ZAK-50002','F10006','Финики без косточек (10 кг)','1','короб','5 500 ₽','Петрова А.А.','79992223344','Казань','Победы','5','12','Да','Наличные','2025-06-26 00:00:00');
INSERT INTO "orders" VALUES (29,'ZAK-50003','F10007','Рис жасмин (10 кг)','1','мешок','5 300 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (30,'ZAK-50003','F10008','Макароны итальянские (12 кг)','1','ящик','6 000 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (31,'ZAK-50003','F10009','Тушёнка говяжья ГОСТ (10 банок)','1','упаковка','7 000 ₽','Сидоров В.В.','79993334455','Екатеринбург','Кирова','22','3','Да','Онлайн','2025-06-27 00:00:00');
INSERT INTO "orders" VALUES (32,'ZAK-50004','F10010','Консервы рыбные (ассорти, 15 банок)','1','ящик','5 200 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (33,'ZAK-50004','F10011','Паштет мясной (24 шт.)','1','ящик','5 100 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (34,'ZAK-50004','F10012','Кукуруза консерв. (12 банок)','1','упаковка','5 300 ₽','Смирнов А.А.','79994445566','Новосибирск','Садовая','7','41','Нет','Онлайн','2025-06-28 00:00:00');
INSERT INTO "orders" VALUES (35,'ZAK-50005','F10013','Гречка высший сорт (15 кг)','1','мешок','6 500 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders" VALUES (36,'ZAK-50005','F10014','Сгущёнка ГОСТ (20 банок)','1','упаковка','5 800 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders" VALUES (37,'ZAK-50005','F10015','Оливковое масло Extra Virgin (5 л)','2','бут.','5 900 ₽','Кузнецова Н.Н.','79995556677','Самара','Лесная','12','9','Да','Онлайн','2025-06-29 00:00:00');
INSERT INTO "orders_status" VALUES (1,'новый');
INSERT INTO "orders_status" VALUES (2,'в процессе выполнения');
INSERT INTO "orders_status" VALUES (3,'завершено');
INSERT INTO "orders_status" VALUES (4,'отсутствуют элементы');
INSERT INTO "products" VALUES ('F10001','Чай Пуэр выдержанный (1 кг)');
INSERT INTO "products" VALUES ('F10002','Кофе в зёрнах Colombia Premium (2 кг)');
INSERT INTO "products" VALUES ('F10003','Мёд Алтайский горный (3 л)');
INSERT INTO "products" VALUES ('F10004','Орех грецкий очищенный (5 кг)');
INSERT INTO "products" VALUES ('F10005','Миндаль сырой (4 кг)');
INSERT INTO "products" VALUES ('F10006','Финики без косточек (10 кг)');
INSERT INTO "products" VALUES ('F10007','Рис жасмин (10 кг)');
INSERT INTO "products" VALUES ('F10008','Макароны итальянские (12 кг)');
INSERT INTO "products" VALUES ('F10009','Тушёнка говяжья ГОСТ (10 банок)');
INSERT INTO "products" VALUES ('F10010','Консервы рыбные (ассорти, 15 банок)');
INSERT INTO "products" VALUES ('F10011','Паштет мясной (24 шт.)');
INSERT INTO "products" VALUES ('F10012','Кукуруза консерв. (12 банок)');
INSERT INTO "products" VALUES ('F10013','Гречка высший сорт (15 кг)');
INSERT INTO "products" VALUES ('F10014','Сгущёнка ГОСТ (20 банок)');
INSERT INTO "products" VALUES ('F10015','Оливковое масло Extra Virgin (5 л)');
INSERT INTO "purchase_goods" VALUES (1,'F10001',1);
INSERT INTO "purchase_goods" VALUES (2,'F10002',2);
INSERT INTO "purchase_goods" VALUES (3,'F10002',5);
INSERT INTO "purchase_goods" VALUES (4,'F10002',1);
INSERT INTO "purchase_goods" VALUES (5,'F10002',9);
INSERT INTO "purchase_goods" VALUES (6,'F10001',2);
INSERT INTO "purchase_goods" VALUES (7,'F10003',1);
INSERT INTO "users" VALUES (1,'1',2,NULL,NULL,'Y');
INSERT INTO "users" VALUES (123456789,'Пользователь 1',1,'1','1','Y');
INSERT INTO "users" VALUES (192837465,'сборщик 2',2,NULL,NULL,'Y');
INSERT INTO "users" VALUES (1212333959,'сборщик 1',2,'',NULL,'Y');
INSERT INTO "users" VALUES (1277014092,'вуа',1,NULL,NULL,'Y');
INSERT INTO "users" VALUES (5872788846,'апиав',1,NULL,NULL,'Y');
INSERT INTO "users_role" VALUES (1,'менеджер');
INSERT INTO "users_role" VALUES (2,'сборщик');
COMMIT;
