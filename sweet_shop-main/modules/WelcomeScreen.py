#  widget - это имя, присваиваемое компоненту пользовательского интерфейса,
#  с которым пользователь может взаимодействовать 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (    
    QDialog, QListWidgetItem, QLabel, QListWidget, QTableWidgetItem, QMessageBox, QFormLayout, QComboBox
)
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QStackedWidget
from PyQt5.uic import loadUi # загрузка интерфейса, созданного в Qt Creator
from PyQt5.QtCore import Qt, QSize

import sqlite3
from datetime import date

from modules.database import showSelect
from pdf import create_pdf_receipt
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
        self.model = showSelect()
        self.AvtorButton.clicked.connect(self.sign_out)
        self.AvtorButton.hide()
        self.stackedWidget.currentChanged.connect(self.hiddenButton)  
        self.PasswordField.setEchoMode(QLineEdit.Password)  # скрываем пароль
        self.SignInButton.clicked.connect(self.open_window)  # нажатие на кнопку и вызов функции

        self.insert_button.clicked.connect(self.insert)  # нажатие на кнопку и вызов функци
        self.edit_button.clicked.connect(self.update)
        self.delete_button.clicked.connect(self.delete)
        self.searchButton.clicked.connect(self.open_search_page)


        self.tableWidget.cellClicked.connect(self.on_cell_clicked)
        self.searchButton.hide()
        self.search.clicked.connect(self.search_data)

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
        self.searchButton.hide()
        self.stackedWidget.setCurrentWidget(self.Avtorisation)
        
    def signupfunction(self): # создаем функцию регистрации        
        user = self.LoginField.text() # создаем пользователя и получаем из поля ввода логина введенный текст
        password = self.PasswordField.text() # создаем пароль и получаем из поля ввода пароля введенный текст
        return user, password # выводит логин и пароль       
    
    def hide_label(self, count):
        line_edits = []
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.verticalLayout_3.count()):
            item = self.verticalLayout_3.itemAt(i)
            widget = item.widget()
            widget.hide()
            
            # Проверяем, является ли виджет QLineEdit
            if isinstance(widget, QLineEdit):
                line_edits.append(widget)
        # Теперь line_edits содержит список всех QLineEdit в QVBoxLayout
        self.lines = line_edits[count:]
        for i in line_edits[count:]:
            i.show()

    def hide_buttons(self, role):
        button_edits = []
        
        # Проходим по всем элементам в QVBoxLayout
        for i in range(self.verticalLayout_2.count()):
            item = self.verticalLayout_2.itemAt(i)
            widget = item.widget()
            
            # Проверяем, является ли виджет QPushButton
            if isinstance(widget, QPushButton):
                button_edits.append(widget)
        
        # Если role == True, показываем все кнопки
        if role:
            for button in button_edits:
                button.show()
        # Если role == False, скрываем все кнопки
        else:
            for button in button_edits:
                button.hide()
                self.searchButton.show()
    def showdata(self, table_widget, typeUser = None, data = None):
        try:
            if data is None:
                # Получаем данные из базы данных
                data = self.model.take_data(typeUser)
            col_names = [i[0] for i in data.description]
            self.col_names = col_names
            data_rows = data.fetchall()

            table_widget.setColumnCount(len(col_names))
            table_widget.setHorizontalHeaderLabels(col_names)
            table_widget.setRowCount(0)

            for i, row in enumerate(data_rows):
                table_widget.setRowCount(table_widget.rowCount() + 1)
                for j, elem in enumerate(row):
                    table_widget.setItem(i, j, QTableWidgetItem(str(elem)))

            table_widget.resizeColumnsToContents()
            print("Столбцов:", len(col_names))
            return len(col_names)
        except Exception as e:
            print(f"Ошибка при отображении данных: {e}")
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
                    cols = self.showdata(self.tableWidget, self.typeUser)
                    self.stackedWidget.setCurrentWidget(self.user)
                    self.hide_buttons(self.model.pages[self.typeUser]['buttons'])
                    if self.typeUser == 2:
                        self.hide_label(16)
                    else:
                        self.hide_label(11 - cols)                
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return None

    def insert(self):
   
        values = [i.text() for i in self.lines]

        self.model.insert(self.typeUser, values)
        self.showdata(self.tableWidget, self.typeUser)
    
    def update(self):
        values = [i.text() for i in self.lines]  # Получаем все значения полей
        
        # Предполагаем, что id находится в values[0], а остальные 5 полей — name, description, price, category_id, manufacturer
        id = values[0]  
        data_values = values[1:6]  # Берём только 5 значений (без id)
        
        # Передаём typeUser, id и 5 значений
        self.model.update(self.typeUser, id, data_values)
        self.showdata(self.tableWidget, self.typeUser)
        
    def delete(self):
        values = [i.text() for i in self.lines]

        id = values[0]
        self.model.delete(self.typeUser, id)
        self.showdata(self.tableWidget, self.typeUser)
    
    def open_search_page(self):
        self.stackedWidget.setCurrentWidget(self.searchPage)
   
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
        data = self.model.search_data_query(result)
        self.showdata(self.tableWidget, data=data)
        self.stackedWidget.setCurrentWidget(self.user)
        