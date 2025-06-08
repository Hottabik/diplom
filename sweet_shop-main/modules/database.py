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
            Первый столбец первой строки, если fetch_one равно True и результат существует; иначе None.
        """
        try:
            cursor = self.connection.cursor()
            data = cursor.execute(query, args)
            
            if fetch_one:
                result = data.fetchone()
                if result is not None:
                    return result
                else:
                    return None
            self.connection.commit()
            return data
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
            2:{
            'buttons': False,
            'select':"""select * from sborshick;"""},
       3: {
           'buttons': True,
           'select': 'select * from Products',
           'insert': '''insert into Products 
                            (id, name, description, price, category_id, manufacturer) 
                        values (?,?,?,?,?,?)''',
           'update': '''UPDATE Products 
                            SET name=?, description=?, price=?, category_id=?, manufacturer=?
                            WHERE id=?''',
            'delete': '''delete from Products where id = ?'''
       }
}   
    def take_data(self, type_user):
        print(self.pages[type_user]['select'])
        result = self.execute_query(query=self.pages[type_user]['select'])

        return result


    def check_user(self, user, password):
        result = self.execute_query('SELECT role FROM Users WHERE email=(?) and password=(?)', user, password, fetch_one=True) 

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