from PyQt5 import QtWidgets, QtCore
from modules.database import showSelect  # Импорт модели
from PyQt5.QtWidgets import (    
    QDialog, QListWidgetItem, QLabel, QListWidget, QTableWidgetItem, QMessageBox, QFormLayout, QComboBox
)
from modules.database import showSelect
from PyQt5.QtWidgets import QHeaderView
class UserManagerWidget(QtWidgets.QWidget):
    def __init__(self, tableWidget, telegram_input, name_input, role_input,
                 login_input, password_input, add_button, update_button, delete_button, parent=None):
        super().__init__(parent)
        self.tableWidget = tableWidget
        self.telegram_input = telegram_input
        self.name_input = name_input
        self.role_input = role_input
        self.login_input = login_input
        self.password_input = password_input
        self.add_button = add_button
        self.update_button = update_button
        self.delete_button = delete_button

        self.model = showSelect()
        self.populate_roles()


        self.connect_signals()
        self.load_users_into_table()  # загружаем данные в таблицу сразу
    
    def populate_roles(self):
        roles = self.model.get_roles()
        self.role_input.clear()
        for role_id, role_name in roles:
            self.role_input.addItem(role_name, role_id)


    def load_users_into_table(self):
        users = self.model.get_users()

        self.tableWidget.setRowCount(len(users))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["Телеграм ID", "Имя", "ID Роли", "Логин", "Пароль", "Свободен"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Вот это добавь
        for row_index, row_data in enumerate(users):
            for col_index, value in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_user)
        self.update_button.clicked.connect(self.update_user)
        self.delete_button.clicked.connect(self.delete_user)
        self.tableWidget.itemClicked.connect(self.load_user_info)


    def load_users(self):
        self.tableWidget.clear()
        users = self.model.get_users()

        self.tableWidget.setRowCount(len(users))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["Телеграм ID", "Имя", "ID Роли", "Логин", "Пароль", "Свободен"])

        for row_index, row_data in enumerate(users):
            for col_index, value in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def load_user_info(self, item):
        telegram_id = item.data(QtCore.Qt.UserRole)
        user = self.model.get_user_info(telegram_id)
        if user:
            self.telegram_input.setText(str(user[0]))
            self.name_input.setText(user[1])
            role_id = int(user[2])
            index = self.role_input.findData(role_id)
            if index != -1:
                self.role_input.setCurrentIndex(index)
            self.login_input.setText(user[3] or "")
            self.password_input.setText(user[4] or "")

    def add_user(self):
        try:
            self.model.add_user(
                self.telegram_input.text(),
                self.name_input.text(),
                self.role_input.currentData(),  # <- здесь
                self.login_input.text() or None,
                self.password_input.text() or None
            )
            self.load_users()
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def update_user(self):
        self.model.update_user(
            self.telegram_input.text(),
            self.name_input.text(),
            self.role_input.currentData(),
            self.login_input.text() or None,
            self.password_input.text() or None
        )
        self.load_users()

    def delete_user(self):
        telegram_id = self.telegram_input.text()
        if not telegram_id:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return

        # Создаем сообщение вручную
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText(f"Удалить пользователя с ID {telegram_id}?")
        msg_box.setIcon(QtWidgets.QMessageBox.Question)

        # Добавляем кнопки и сохраняем ссылки
        yes_button = msg_box.addButton("Да", QtWidgets.QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QtWidgets.QMessageBox.NoRole)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            self.model.delete_user(telegram_id)
            self.load_users()
            self.clear_inputs()


    def clear_inputs(self):
        self.telegram_input.clear()
        self.name_input.clear()
        self.role_input.setCurrentIndex(0)
        self.login_input.clear()
        self.password_input.clear()
    
    def get_free_collectors(self):
        return self.execute_query('''
            SELECT telegram_id, name FROM users
            WHERE role_id = 2 AND isFree = 'Y'
        ''')

