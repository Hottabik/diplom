import sqlite3

class Model:
    def __init__(self) -> None:
        self.db = 'db.db'
        self.connection = self.connect()

    def connect(self):
        try:
            return sqlite3.connect(self.db)
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None
        
    def execute_query(self, query: str, *args, fetch_one: bool = False) -> any:
        """
        Выполняет запрос к базе данных.

        Параметры:
            query (str): SQL-запрос для выполнения.
            *args: Параметры для подстановки в запрос.
            fetch_one (bool): Нужно ли извлечь один результат.

        Возвращает:
            Одну строку (tuple), если fetch_one=True; иначе список строк.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, args)

            if fetch_one:
                return cursor.fetchone()

            result = cursor.fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None

            

class showSelect(Model):
    def __init__(self):
        super().__init__()  # Наследуем функциональность выполнения запросов

        self.pages = {
            1: {
                'select':''
            },
            2: {
                'buttons': False,
                'select': """SELECT * FROM sborshick;""",
                'update': """UPDATE sborshick SET Сборщик = ? WHERE id = ?"""
            },

       3: {
           'buttons': True,
           'select': 'select * from Products',
           'insert': '''insert into Products 
                            (id, name, description, price, category_id, image_url) 
                        values (?,?,?,?,?,?)''',
           'update': '''UPDATE Products 
                            SET name=?, description=?, price=?, category_id=?, image_url=?
                            WHERE id=?''',
            'delete': '''delete from Products where id = ?'''
       }
}   
    def take_data(self, type_user):
        print(self.pages[type_user]['select'])
        result = self.execute_query(query=self.pages[type_user]['select'])

        return result


    def check_user(self, user, password):
        result = self.execute_query('SELECT role_id FROM users WHERE login=(?) and password=(?)', user, password, fetch_one=True) 

        return result
    
    def insert(self,typeUser, values):
        result = self.execute_query(self.pages[typeUser]['insert'], *values)
        
        return result
    
    def update(self, typeUser, id, values):
    # Добавляем id в конец списка values (чтобы было 6 значений)
        full_values = values + [id]
        
        # Передаём как единый список (без распаковки *)
        result = self.execute_query(self.pages[typeUser]['update'], *full_values)
        return result
    def delete(self,typeUser, id):
        result = self.execute_query(self.pages[typeUser]['delete'], id)
        
        return result

    def search_data_query(self, params):
        """Выполняет поисковый запрос с параметрами"""
        if not params:
            return self.execute_query('SELECT * FROM sborshick')
        
        # Сопоставление русских названий с именами колонок в БД
        field_mapping = {
            "ID заказа": "ID_заказа",
            "Общая цена": "Общая_цена",
            "Статус": "Статус_заказа",
            "Город": "Город",
            "Название товара": "Название_товара"
        }
        
        conditions = []
        values = []
        
        # Формируем условия и значения для запроса
        for field, value in params.items():
            if field in field_mapping:
                column = field_mapping[field]
                conditions.append(f"{column} LIKE ?")
                values.append(f"%{value}%")  # Поиск по частичному совпадению
        
        if not conditions:
            return self.execute_query('SELECT * FROM sborshick')
        
        # Собираем полный запрос
        query = "SELECT * FROM sborshick WHERE " + " AND ".join(conditions)
        
        try:
            result = self.execute_query(query, *values)
            return result
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None
        
    def get_orders(self):
        result = self.execute_query('''
SELECT 
    o.order_number AS "Номер_заказа",
    MIN(o.order_date) AS "Дата_заказа",
    MAX(os.status) AS "Статус_заказа",
    MAX(a.due_date) AS "Срок_выполнения",
    MAX(COALESCE(u.name, CAST(a.telegram_id AS TEXT))) AS "Сборщик",
    MIN(o.city) AS "Город",
    MIN(
        o.street || ', д.' || o.house_number || 
        CASE 
            WHEN o.apartment IS NOT NULL THEN ', кв.' || o.apartment 
            ELSE '' 
        END
    ) AS "Адрес",

    (
        SELECT GROUP_CONCAT(tov, ', ')
        FROM (
            SELECT DISTINCT 
                p.name || ' (' || oo.quantity || ' ' || oo.unit || ')' AS tov
            FROM orders oo
            JOIN products p ON oo.articul = p.id_articul
            WHERE oo.order_number = o.order_number
        )
    ) AS "Товары",

    SUM(
        CAST(REPLACE(REPLACE(o.unit_price, '₽', ''), ' ', '') AS REAL) *
        CAST(REPLACE(o.quantity, ' ', '') AS REAL)
    ) AS "Общая_цена"

FROM orders o
JOIN products p ON o.articul = p.id_articul
LEFT JOIN assembling a ON o.id = a.order_id
LEFT JOIN users u ON a.telegram_id = u.telegram_id
LEFT JOIN orders_status os ON a.id_status = os.id_status
-- УБРАЛИ ФИЛЬТР a.telegram_id IS NOT NULL
GROUP BY o.order_number
ORDER BY o.order_number;



    ''')
        
        return result
    
    def import_data(self, df) -> bool:
        """
        Импортирует данные из DataFrame в таблицу orders.
        
        Возвращает:
            bool: True если импорт успешен, False в случае ошибки.
        """
        try:
            
            with self.connection:
                cursor = self.connection.cursor()

                for _, row in df.iterrows():
                    print(row)
                    cursor.execute('''
                        INSERT INTO orders (
                            order_number, articul, product_name, quantity, unit, unit_price,
                            recipient_name, phone, city, street, house_number, apartment,
                            courier_delivery, payment_method, order_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Номер заказа'],
                        row['Артикул'],
                        row['Наименование'],
                        row['Кол-во'],
                        row['Ед. изм.'],
                        str(row['Цена за ед.']),
                        row['ФИО получателя'],
                        str(row['Телефон']),
                        row['Город'],
                        row['Улица'],
                        str(row['Дом']),
                        str(row['Кв.']),
                        row['Доставка'],
                        row['Оплата'],
                        str(row['Дата сборки'])
                    ))
            return True

        except Exception as e:
            print(f"Ошибка при импорте данных: {e}")
            return False
    def get_free_collectors(self):
        query = "SELECT telegram_id, name FROM users WHERE role_id = 2 AND isFree = 'Y'"
        return self.execute_query(query)

        
    def get_order(self, order_number):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))  # правильно
        result = cursor.fetchall()
        cursor.close()
        return result


    def update_order(self, collector_id, current_order_id):
        # collector_id может быть tuple, например (123,)
        if isinstance(collector_id, tuple):
            collector_id = collector_id[0]

        self.execute_query('''
            UPDATE assembling 
            SET telegram_id = ?
            WHERE order_number = ?
        ''', collector_id, current_order_id)

    def get_products(self):
        """Получение всех товаров из таблицы Products"""
        result = self.execute_query('SELECT * FROM products')
        return result

    def get_purchase_products(self):
        """Получение товаров, связанных с определённой покупкой"""
        result = self.execute_query('''
            SELECT
                pg.id_articul, 
                SUM(pg.quantity) as total_quantity, 
                MAX(p.name) as product_name
            FROM
                purchase_goods pg
                JOIN products p ON pg.id_articul = p.id_articul
            GROUP BY pg.id_articul;
        ''')
        return result
    
    def add_purchase_good(self, product_id, quantity):
        """
        Добавляет товар к покупке в таблицу purchase_goods.

        Аргументы:
            purchase_id (int): ID покупки.
            product_id (int): ID товара.
            quantity (int): Количество товара.

        Возвращает:
            Результат выполнения запроса.
        """
        result = self.execute_query(
            '''
            INSERT INTO purchase_goods (id_articul, quantity)
            VALUES (?, ?)
            ''',
            product_id, quantity
        )
        return result
    
    # Добавим в Model или showSelect

    def get_users(self):
        query = """
        SELECT 
            telegram_id AS "Телеграм ID", 
            name AS "Имя", 
            role_id AS "ID Роли", 
            login AS "Логин", 
            password AS "Пароль", 
            isFree AS "Свободен"
        FROM users
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_user_info(self, telegram_id):
        return self.execute_query('''
            SELECT telegram_id, name, role_id, login, password 
            FROM users WHERE telegram_id = ?
        ''', telegram_id, fetch_one=True)

    def add_user(self, telegram_id, name, role_id, login=None, password=None):
        try:
            return self.execute_query('''
                INSERT INTO users (telegram_id, name, role_id, login, password, isFree)
                VALUES (?, ?, ?, ?, ?, 'Y')
            ''', telegram_id, name, role_id, login, password)
        except sqlite3.IntegrityError as e:
            raise ValueError("Пользователь с таким Telegram ID уже существует")

    def update_user(self, telegram_id, name, role_id, login=None, password=None):
        return self.execute_query('''
            UPDATE users 
            SET name = ?, role_id = ?, login = ?, password = ?
            WHERE telegram_id = ?
        ''', name, role_id, login, password, telegram_id)

    def delete_user(self, telegram_id):
        return self.execute_query('DELETE FROM users WHERE telegram_id = ?', telegram_id)


    def get_roles(self):
        query = "SELECT Id_role, role FROM users_role"
        cursor = self.connection.cursor()
        cursor.execute(query)
        roles = cursor.fetchall()
        cursor.close()
        return roles
        
    def insert_issembling(self, order_number, telegram_id):
        try:
            # Если пришёл tuple — распаковываем
            if isinstance(order_number, tuple):
                order_number = order_number[0]
            if isinstance(telegram_id, tuple):
                telegram_id = telegram_id[0]

            cursor = self.connection.cursor()
            
            # Получаем order_id по order_number
            cursor.execute("SELECT id FROM orders WHERE order_number = ?", (order_number,))
            result = cursor.fetchone()
            if result is None:
                raise Exception(f"Заказ с номером {order_number} не найден")
            order_id = result[0]

            # Вставляем в assembling уже с order_id
            query = '''
            INSERT INTO assembling (order_id, telegram_id, due_date, id_status)
            VALUES (?, ?, "1 час", 1)
            '''
            print(f"Вставка: order_id={order_id}, telegram_id={telegram_id}")
            cursor.execute(query, (order_id, telegram_id))
            self.connection.commit()
            print("Insert успешен")

        except Exception as e:
            print(f"Ошибка вставки в assembling: {e}")




    def get_status_id(self, status_name):
        query = "SELECT id_status FROM orders_status WHERE status = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (status_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None  # или 0, если хочешь дефолтное значение

    def get_data_check(self, order_number):
        query = '''
        SELECT 
            o.order_number, 
            o.articul, 
            o.product_name, 
            o.quantity, 
            o.unit, 
            o.unit_price, 
            o.recipient_name, 
            o.phone, 
            o.city, 
            o.street, 
            o.house_number, 
            o.apartment, 
            o.courier_delivery, 
            o.payment_method, 
            o.order_date,
            i.due_date,
            u.name
        FROM Orders o
        LEFT JOIN assembling i ON o.id = i.order_id  
        LEFT JOIN Users u ON i.telegram_id = u.telegram_id
        WHERE o.order_number = ?
        '''
        return self.execute_query(query, order_number)  # Убрал fetch_one=True, если нужно несколько строк
        

    def get_order_status(self, order_number):
        query = """
        SELECT os.status 
        FROM orders o
        JOIN assembling a ON o.id = a.order_id
        JOIN orders_status os ON a.id_status = os.id_status
        WHERE o.order_number = ?
        LIMIT 1
        """
        result = self.execute_query(query, order_number, fetch_one=True)
        return result[0] if result else None