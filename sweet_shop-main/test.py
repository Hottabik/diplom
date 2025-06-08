import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Пример таблицы с кликом")
        self.setGeometry(100, 100, 400, 300)

        # Создаем таблицу
        self.table = QTableWidget(self)
        self.table.setRowCount(3)
        self.table.setColumnCount(2)

        # Заполняем таблицу данными
        self.table.setItem(0, 0, QTableWidgetItem("Строка 1"))
        self.table.setItem(0, 1, QTableWidgetItem("Значение 1"))
        self.table.setItem(1, 0, QTableWidgetItem("Строка 2"))
        self.table.setItem(1, 1, QTableWidgetItem("Значение 2"))
        self.table.setItem(2, 0, QTableWidgetItem("Строка 3"))
        self.table.setItem(2, 1, QTableWidgetItem("Значение 3"))

        # Подключаем сигнал clicked к слоту
        self.table.cellClicked.connect(self.on_cell_clicked)

        # Устанавливаем таблицу в главное окно
        self.setCentralWidget(self.table)

    def on_cell_clicked(self, row, column):
        # Получаем данные из ячейки
        item = self.table.item(row, column)
        if item:
            print(f"Вы нажали на строку {row}, столбец {column}: {item.text()}")

            # Здесь можно открыть страницу или выполнить другое действие
            # Например, открыть URL:
            # import webbrowser
            # webbrowser.open("https://example.com")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())