from PyQt5.QtWidgets import (
    QLabel, 
    QLineEdit, 
    QMessageBox, 
    QWidget
)
from PyQt5.QtCore import Qt
from ui import Ui

class EditPage():
    def __init__(self):
        pass
    def open_edit_window(self, item, user_type):
        try:
            # Получаем ID записи
            self.current_edit_id = item.data(Qt.UserRole)
            self.current_user_type = user_type
            
            # Переключаемся на страницу редактирования
            self.stackedWidget.setCurrentWidget(self.ui.lv_edit)
            
            # Очищаем предыдущие поля
            for child in self.ui.edit_form_layout.children():
                if isinstance(child, QWidget):
                    child.deleteLater()
            
            # Загружаем данные записи
            data = self.model.get_single_record(self.current_edit_id, user_type)
            row = data.fetchone()
            
            # Создаем поля ввода динамически
            self.edit_fields = []
            for idx, (col_name, value) in enumerate(zip(data.description, row)):
                if idx == 0:  # Пропускаем ID
                    continue
                    
                label = QLabel(col_name[0] + ":")
                edit = QLineEdit(str(value))
                self.ui.edit_form_layout.addRow(label, edit)
                self.edit_fields.append(edit)
            
            # Настраиваем кнопки
            self.btn_save.clicked.connect(self.save_changes)
            self.btn_cancel.clicked.connect(lambda: 
                self.ui.stackedWidget.setCurrentWidget(self.ui.list_page)
            )

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные для редактирования")

    def save_changes(self):
        try:
            new_values = [field.text() for field in self.edit_fields]
            if self.model.update_record(self.current_edit_id, new_values, self.current_user_type):
                QMessageBox.information(self, "Успех", "Изменения сохранены")
                self.stackedWidget.setCurrentWidget(self.ui.list_page)
                # Обновляем список
                self.showdata(self.ui.listWidget, self.current_user_type)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изменения")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")