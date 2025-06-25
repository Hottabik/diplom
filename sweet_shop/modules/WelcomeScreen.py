#  widget - это имя, присваиваемое компоненту пользовательского интерфейса,
#  с которым пользователь может взаимодействовать 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (    
    QDialog, QListWidgetItem, QLabel, QListWidget, QTableWidgetItem, QMessageBox, QFormLayout, QComboBox
)
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QStackedWidget
from PyQt5.uic import loadUi # загрузка интерфейса, созданного в Qt Creator
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import pandas as pd
import sqlite3
from datetime import date
from modules.user import UserManagerWidget  # импорт твоего класса UserManagerWidget
from modules.zaivka import generate_supply_request
import os
from modules.database import showSelect
from pdf import create_pdf_receipt
from modules.naklodnaipdf import create_invoice_pdf

class WelcomeScreen(QDialog):
    """
    Это класс окна приветствия.
    """
    def __init__(self):
        """
        Это конструктор класса
        """
        super(WelcomeScreen, self).__init__()
        loadUi("views/welcomescreen.ui", self)  # загружаем интерфейс.

        # настрой таблицу (размеры, колонки и т.д.)
        self.user_manager = UserManagerWidget(
            self.tableWidget,
            self.lineEdit,
            self.lineEdit_2,
            self.comboBox,
            self.lineEdit_3,
            self.lineEdit_4,
            self.addus,
            self.apdateuser,
            self.deleteuser
        )
        self.collector_ids = {}
        self.model = showSelect()

        self.AvtorButton.clicked.connect(self.sign_out)
        self.AvtorButton.hide()
        self.stackedWidget.currentChanged.connect(self.hiddenButton)  
        self.PasswordField.setEchoMode(QLineEdit.Password)  # скрываем пароль
        self.SignInButton.clicked.connect(self.open_window)  # нажатие на кнопку и вызов функции
        self.importButton.clicked.connect(self.import_excel_to_sqlite)
        self.listWidget.itemDoubleClicked.connect(self.edit_order)
        self.search.clicked.connect(self.save_order_changes)
        self.lagPage.clicked.connect(self.product_order)
        self.add.clicked.connect(self.add_product_to_purchase)
        self.sait.clicked.connect(self.open_site)
        self.sait.clicked.connect(self.open_site)
        self.nacklad.clicked.connect(self.nackladnaya)
        self.add_2.clicked.connect(self.on_generate_supply)

        for button in self.findChildren(QtWidgets.QPushButton):
            if button.text() == "Назад":
                button.clicked.connect(self.go_to_user_page)

        # Добавляем в stackedWidget (или любой контейнер в твоём .ui)
        self.stackedWidget.addWidget(self.user_manager)
        
        # Привязываем кнопку перехода на страницу управления пользователями
        self.adduser.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.user_manager))

        self.adduser.clicked.connect(self.open_adduser_page)
   
    def on_generate_supply(self):
        """Генерация заявки на поставку без указания путей"""
        try:
            # Получаем текущую директорию приложения
            app_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(app_dir, "generated_docs")
            
            # Создаем папку для документов, если не существует
            os.makedirs(output_dir, exist_ok=True)
            
            # Генерируем заявку
            success = generate_supply_request(parent=self, output_dir=output_dir)
            
            if success:
                # Открываем папку с документами
                QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать заявку:\n{str(e)}")

    def open_adduser_page(self):
        self.stackedWidget.setCurrentWidget(self.addusers)

    def go_to_user_page(self):
        # Перейти на страницу по имени
        for i in range(self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if widget.objectName() == "user":
                self.stackedWidget.setCurrentIndex(i)
                break

    def open_site(self):
        QDesktopServices.openUrl(QUrl("https://ambar-moskow.ru/"))

    def on_cell_clicked(self, row):
        if self.typeUser == 2:
            # Выделяем всю строку
            self.tableWidget.selectRow(row)
            
            # Устанавливаем стиль выделения (зеленый фон)
            self.tableWidget.setStyleSheet(
                "QTableView::item:selected { background-color: green; color: black; }"
            )
            row_data = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # Если ячейка пуста, добавляем пустую строку
                
            # Создаем всплывающее окно с уведомлением
            msg = QMessageBox()
            msg.setWindowTitle("Чек создан")  # Заголовок окна
            msg.setText(f"Данные чека . строки {self.col_names} данные {row_data}")  # Текст сообщения
            msg.setIcon(QMessageBox.Information)  # Иконка (Information, Warning, Critical и т.д.)
            msg.setStandardButtons(QMessageBox.Ok)  # Кнопка "ОК"

            # Показываем всплывающее окно
            msg.exec_()

            create_pdf_receipt(dict(zip(self.col_names, row_data)))

    def hiddenButton(self):
        if self.stackedWidget.currentWidget() == self.Avtorisation:  
            self.AvtorButton.hide()
        else:
            self.AvtorButton.show()
    def sign_out(self):
        self.stackedWidget.setCurrentWidget(self.Avtorisation)
        
    def signupfunction(self): # создаем функцию регистрации        
        user = self.LoginField.text() # создаем пользователя и получаем из поля ввода логина введенный текст
        password = self.PasswordField.text() # создаем пароль и получаем из поля ввода пароля введенный текст
        return user, password # выводит логин и пароль       
    

    def format_order_html(self, order_data):
        """Форматирование данных заказа из агрегированной строки"""
        if not order_data:
            return ""
            
        row = order_data[0]  # Только одна строка на заказ
        order_number = row[0]
        order_date = row[1]
        status = row[2]
        due_date = row[3]
        assembler = row[4]
        city = row[5]
        address = row[6]
        product_text = row[7]  # Уже объединённая строка с товарами
        total_price = row[8]

        status_colors = {
            'новый': '#1E90FF',
            'в процессе выполнения': '#FFA500',
            'завершено': '#32CD32',
            'отсутствуют элементы': '#FF4500',
        }

        formatted_date = order_date.split()[0] if order_date else ""
        status_key = (status or '').lower()
        color = status_colors.get(status_key, '#888888')
        return f"""
        <div style="font-family:Arial; padding:15px; border-radius:8px; background:#ffffff; margin-bottom:15px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;">
                <div style="font-size:18px; font-weight:bold; color:#2c3e50;">
                    Заказ №{order_number}
                </div>
                <div style="padding:5px 10px; background:{color};; 
                    color:white; border-radius:4px; font-size:14px;">
                    {status}
                </div>
            </div>

            <div style="margin:10px 0; padding:10px; background:#f8f9fa; border-radius:4px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <div>
                        <span style="color:#555;">Дата заказа:</span> 
                        <strong>{formatted_date}</strong>
                    </div>
                    <div>
                        <span style="color:#555;">Срок выполнения:</span> 
                        <strong>{due_date if due_date else 'не указан'}</strong>
                    </div>
                </div>
                
                <div style="margin-top:5px;">
                    <span style="color:#555;">Сборщик:</span> 
                    <strong>{assembler if assembler else 'не назначен'}</strong>
                </div>
            </div>

            <div style="margin:15px 0;">
                <div style="font-weight:bold; margin-bottom:8px; color:#555;">Состав заказа:</div>
                <div>{product_text}</div>
                <div style="margin-top:10px; font-size:14px;">
                    <span style="color:#555;">Сумма:</span> <strong>{total_price} ₽</strong>
                </div>
            </div>

            <div style="margin-top:15px; padding-top:10px; border-top:1px solid #eee; color:#555;">
                <div style="font-weight:bold; margin-bottom:5px;">Адрес доставки:</div>
                <div>{city}, {address}</div>
            </div>
            <br><br>
        </div>
        """


    def add_order_item(self, order_data):
        """Добавление заказа в QListWidget"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, order_data[0])  # Сохраняем ID заказа
        
        widget = QLabel(self.format_order_html(order_data))
        widget.setContentsMargins(5, 5, 5, 5)
        widget.setWordWrap(True)
        
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def show_orders(self, list_widget, data=None):
        """Отображение списка заказов"""
        try:
            list_widget.clear()
            if data is None:
                # Получаем данные из базы
                rows = self.model.get_orders()  # Этот метод нужно реализовать в модели
                
                # Группируем данные по номеру заказа
                from collections import defaultdict
                grouped_orders = defaultdict(list)
                for row in rows:
                    grouped_orders[row[0]].append(row)  # Группируем по order_number (предполагая, что это первый элемент)

                # Для каждого заказа вызываем функцию добавления
                for order_number, order_data in grouped_orders.items():
                    self.add_order_item(order_data)
            else:
                # Если данные переданы напрямую (например, при поиске)
                # Здесь также нужно сгруппировать, если data не сгруппирована
                grouped_data = defaultdict(list)
                for row in data:
                    grouped_data[row[0]].append(row)
                    
                for order_number, order_data in grouped_data.items():
                    self.add_order_item(order_data)

        except Exception as e:
            print(f"Ошибка при отображении заказов: {e}")
            return 0
    def open_window(self):
        try:
            user, password = self.signupfunction()
            if len(user) == 0 or len(password) == 0:
                self.ErrorField.setText("Заполните все поля")
            else:
                self.ErrorField.setText(" ")
                typeUser = self.model.check_user(user, password)
                self.typeUser = typeUser[0]
                if self.typeUser is None:
                    self.ErrorField.setText("Пользователь с такими данными не найден")
                else:
                    # Передаем listWidget вместо tableWidget
                    self.show_orders(self.listWidget)
                    self.stackedWidget.setCurrentWidget(self.user)
                           
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None

   
    def search_data(self):
        result = {}
        
        # Проходим по всем элементам формы
        for row in range(self.searchFormLayout.rowCount()):
            # Получаем лейбл (если есть)
            label_item = self.searchFormLayout.itemAt(row, QFormLayout.LabelRole)
            if label_item is not None:
                label = label_item.widget().text()  # текст лейбла в нижнем регистре
                
                # Получаем поле ввода/комбобокс
                field_item = self.searchFormLayout.itemAt(row, QFormLayout.FieldRole)
                if field_item is not None:
                    widget = field_item.widget()
                    
                    # Получаем значение в зависимости от типа виджета
                    if isinstance(widget, QLineEdit):
                        value = widget.text().strip()
                    elif isinstance(widget, QComboBox):
                        value = widget.currentText()
                    else:
                        value = None
                    
                    # Добавляем в словарь только если значение не пустое
                    if value:
                        result[label] = value
        
        self.show_orders(self.listWidget)
        print("проверка")
        data = self.model.search_data_query(result)
        self.showdata(self.tableWidget, data=data)
        self.stackedWidget.setCurrentWidget(self.user)
        


    def save_order_changes(self):
        """Добавление новой записи в assembling"""
        try:
            order_number = self.orderIdInput.text().strip()
            assembler_name = self.statusComboBox.currentText().strip()

            # Пропускаем, если не выбран сборщик
            if assembler_name == "Не назначен":
                QMessageBox.warning(self, "Ошибка", "Выберите сборщика")
                return

            # Получаем telegram_id по имени
            telegram_id = self.collector_ids.get(assembler_name)

            # Вставка новой записи
            self.model.insert_issembling(order_number, telegram_id)
            self.show_orders(self.listWidget)


            QMessageBox.information(self, "Успех", "Сборщик назначен")

            self.stackedWidget.setCurrentWidget(self.user)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось назначить сборщика: {str(e)}")




    def import_excel_to_sqlite(self):
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл Excel", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return  # Пользователь отменил выбор файла
        
        try:
            # Читаем данные из Excel
            df = pd.read_excel(file_path)
            
            # Подключаемся к базе данных SQLite
            self.model.import_data(df)
            
            QMessageBox.information(
                self, 
                "Успех", 
                f"Данные успешно импортированы из {file_path}"
            )
            # Передаем listWidget вместо tableWidget
            self.show_orders(self.listWidget)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Произошла ошибка при импорте:\n{str(e)}"
            )
    def edit_order(self, item):
        """Редактирование заказа"""
        item = item
        order_number = item.data(Qt.UserRole)
        print(order_number)
        order_data = item.data(Qt.UserRole)
        if isinstance(order_data, tuple):
            order_number = order_data[0]
        else:
            order_number = order_data

        
        try:
            # Получаем данные заказа
            order = self.model.get_order(order_number)
            if not order:
                QMessageBox.warning(self, "Ошибка", "Заказ не найден")
                return
                
            # Получаем список сборщиков (role_id = 2)
            collectors = self.model.get_free_collectors()  # Стало

            # Заполняем форму данными
            self.fill_order_form(order, collectors)
            
            self.is_editing = True
            self.current_order_id = order_number
            self.stackedWidget.setCurrentWidget(self.searchPage)  # Переключаем на страницу редактирования
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def fill_order_form(self, order, collectors):
        """Заполнение формы редактирования заказа"""
        def safe_set_text(widget, value):
            widget.setText(str(value) if value is not None else "")

        # Заполняем orderIdInput
        if order is not None:
            # order — это результат запроса, обычно list/tuple, где первый элемент — сама запись
            # Если order — список строк, то order[0] — первая строка, order[0][0] — id заказа
            if isinstance(order, (list, tuple)) and len(order) > 0:
                safe_set_text(self.orderIdInput, order[0][1])
            else:
                safe_set_text(self.orderIdInput, "")
        else:
            safe_set_text(self.orderIdInput, "")

        # Заполняем combobox сборщиками
        self.statusComboBox.clear()
        self.collector_ids = {}

        # Добавляем вариант "Не назначен"
        self.statusComboBox.addItem("Не назначен")

        # collectors — список кортежей (telegram_id, name)
        for telegram_id, name in collectors:
            self.statusComboBox.addItem(name)
            self.collector_ids[name] = telegram_id

        # Если в заказе есть назначенный сборщик, поставим его в combobox
        # Допустим, order[0][...] содержит telegram_id сборщика — подставь правильный индекс
        assigned_telegram_id = None
        # пример, если в order есть поле telegram_id сборщика (например, order[0][1])
        if order and len(order) > 0 and len(order[0]) > 1:
            assigned_telegram_id = order[0][1]

        if assigned_telegram_id:
            assigned_name = None
            for name, tid in self.collector_ids.items():
                if tid == assigned_telegram_id:
                    assigned_name = name
                    break
            if assigned_name:
                idx = self.statusComboBox.findText(assigned_name)
                if idx != -1:
                    self.statusComboBox.setCurrentIndex(idx)
                else:
                    self.statusComboBox.setCurrentIndex(0)
            else:
                self.statusComboBox.setCurrentIndex(0)
        else:
            self.statusComboBox.setCurrentIndex(0)

    
    def product_order(self):
        

        # Очищаем список перед заполнением
        self.listWidget_2.clear()
        self.productcomboBox.clear()  # Очищаем комбобокс перед заполнением

        try:
            # Получаем данные о продуктах из модели
            # products: id, name, price, article, etc.
            products = self.model.get_products()  # Реализуйте этот метод в вашей модели
            for row in products:
                product_name_id = row[0]
                product_name = row[1]

                # Добавляем артикул в комбобокс
                if product_name_id:
                    self.productcomboBox.addItem(str(product_name), product_name_id)
            # purchase_product: product_id, quantity, etc.
            purchase_data = self.model.get_purchase_products()  # Реализуйте этот метод в вашей модели

            # Создаем словарь для быстрого доступа к количеству по product_id
            purchase_dict = {}
            for row in purchase_data:
                product_id = row[0]
                quantity = row[1]
                name = row[2]
            

                # Формируем строку для отображения
                display_text = f"{name} | Аритикуль: {product_id} ₽ | Кол-во: {quantity}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, product_id)
                self.listWidget_2.addItem(item)

                
            # Переключаемся на страницу с продуктами
            self.stackedWidget.setCurrentWidget(self.product)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить продукты: {str(e)}")

    def add_product_to_purchase(self):
        try:
            # Получаем выбранный продукт и количество
            product_index = self.productcomboBox.currentIndex()
            product_id = self.productcomboBox.itemData(product_index)
            quantity = self.countspinBox.value()  # Предполагается, что у вас есть QSpinBox с этим именем

            if product_id is None or quantity <= 0:
                QMessageBox.warning(self, "Ошибка", "Выберите продукт и укажите количество больше 0")
                return

            # Добавляем запись в таблицу purchase_goods через модель
            self.model.add_purchase_good(product_id, quantity)

            QMessageBox.information(self, "Успех", "Товар успешно добавлен в закупку")
            self.product_order()  # Обновляем список продуктов

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар: {str(e)}")

    def nackladnaya(self):
        try:
            order_number = self.orderIdInput.text()
            
            # Проверяем статус заказа
            order_status = self.model.get_order_status(order_number)  # Нужно реализовать этот метод в модели
            
            if order_status != "завершено":
                QMessageBox.warning(self, "Ошибка", "Накладная может быть создана только для заказов со статусом 'завершено'")
                return
                
            # Получаем данные для накладной из модели
            raw_data = self.model.get_data_check(order_number)

            if not raw_data:
                QMessageBox.warning(self, "Ошибка", "Нет данных для накладной")
                return

            # Обрабатываем сырые данные и преобразуем в нужный формат
            first_row = raw_data[0]

            # Формируем список уникальных товаров (игнорируем дубликаты сборщиков)
            unique_items = {}
            for row in raw_data:
                item_id = row[1]  # F10001, F10002 и т.д.
                if item_id not in unique_items:
                    try:
                        quantity = int(row[3])
                    except Exception:
                        quantity = 0
                    try:
                        unit_price = int(str(row[5]).replace(' ', '').replace('₽', '').strip())
                    except Exception:
                        unit_price = 0
                    unique_items[item_id] = {
                        'name': row[2],
                        'quantity': quantity,
                        'unit': row[4],
                        'unit_price': unit_price,
                        'total_price': quantity * unit_price
                    }

            # Формируем данные для накладной с безопасной проверкой индексов
            def safe_get(row, idx, default=""):
                return row[idx] if len(row) > idx and row[idx] is not None else default
            from datetime import datetime

            assembly_date = safe_get(first_row, 15)  # дата сборки из базы
            if not assembly_date:
                assembly_date = datetime.now().strftime('%Y-%m-%d')  # сегодня
            invoice_data = {
                'order_number': safe_get(first_row, 0),
                'assembly_date': assembly_date,
                'customer_name': safe_get(first_row, 6),
                'phone': safe_get(first_row, 7),
                'delivery_address': (
                    f"г. {safe_get(first_row, 8)}, ул. {safe_get(first_row, 9)}, д. {safe_get(first_row, 10)}, кв. {safe_get(first_row, 11)}"
                    if len(first_row) > 11 else ""
                ),
                'items': list(unique_items.values()),
                'total_amount': sum(item['total_price'] for item in unique_items.values()),
                'manager_name': "Петров П.П."
            }
            print(invoice_data)

            # Генерируем PDF-файл накладной
            pdf_path = create_invoice_pdf(invoice_data)

            QMessageBox.information(self, "Успех", f"Накладная успешно создана:\n{pdf_path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать накладную: {str(e)}")
