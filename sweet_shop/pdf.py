import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import os

# Регистрация шрифта DejaVuSans для поддержки кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

def fetch_order_data(order_id):
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('db.db')  # Замените на путь к вашей базе данных
    cursor = conn.cursor()

    # SQL-запрос для получения данных о заказе
    query = """
    SELECT
        o.id AS ID_заказа,
        o.order_date AS Дата_заказа,
        o.total_price AS Общая_цена,
        o.status AS Статус_заказа,
        a.address AS Адрес,
        a.city AS Город,
        a.postal_code AS Почтовый_индекс,
        GROUP_CONCAT(p.id) AS ID_товара,
        GROUP_CONCAT(p.name) AS Название_товара,
        GROUP_CONCAT(p.description) AS Описание_товара,
        GROUP_CONCAT(p.price) AS Цена_товара,
        GROUP_CONCAT(p.image_url) AS Изображение_товара,
        GROUP_CONCAT(c.id) AS ID_категории,
        GROUP_CONCAT(c.name) AS Название_категории,
        GROUP_CONCAT(oi.quantity) AS Количество,
        GROUP_CONCAT(oi.price) AS Цена_позиции
    FROM
        Orders o
    JOIN
        Addresses a ON o.address_id = a.id
    JOIN
        Order_Items oi ON o.id = oi.order_id
    JOIN
        Products p ON oi.product_id = p.id
    JOIN
        Categories c ON p.category_id = c.id
    WHERE
        o.id = ?
    GROUP BY
        o.id, o.order_date, o.total_price, o.status, a.address, a.city, a.postal_code;
    """

    # Выполнение запроса
    cursor.execute(query, (order_id,))
    row = cursor.fetchone()

    # Преобразование результата в словарь
    columns = [column[0] for column in cursor.description]
    data = dict(zip(columns, row)) if row else None

    # Закрытие соединения
    conn.close()

    return data


def create_pdf_receipt(data):
    # Создаем новый PDF-документ
    c = canvas.Canvas("check.pdf", pagesize=letter)
    width, height = letter

    # Установка шрифта с поддержкой кириллицы
    c.setFont("DejaVuSans", 12)

    # Начальные координаты для печати
    y = height - 50

    # Заголовок чека
    c.drawCentredString(width / 2, y, "000 \"СуперЧек.ру\"")
    y -= 30
    c.drawCentredString(width / 2, y, f"Чек N {data['ID_заказа']}")
    y -= 30
    c.drawCentredString(width / 2, y, f"Дата заказа: {data['Дата_заказа']}")
    y -= 30
    c.drawCentredString(width / 2, y, "Кассир: Иванов")
    y -= 40

    # Адрес и другие данные
    c.drawString(100, y, f"Адрес: {data['Адрес']}")
    y -= 20
    c.drawString(100, y, f"Город: {data['Город']}")
    y -= 20
    c.drawString(100, y, f"Почтовый индекс: {data['Почтовый_индекс']}")
    y -= 40

    items = zip(
        data["Название_товара"].split(','),
        data["Название_категории"].split(','),
        data["Количество"].split(','),
        data["Цена_позиции"].split(',')
    )
    for i, (name, category, quantity, price) in enumerate(items, start=1):
        # Форматируем строку с данными о товаре
        item_line = f"{name} ({category}) - {quantity} шт. x {price} руб. = {float(price) * int(quantity)} руб."
        c.drawString(100, y, item_line)
        y -= 30  # Отступ между строками товаро

     # Итоговая сумма
    c.line(100, y, 400, y)
    y -= 30
    c.drawString(100, y, f"ИТОГ: {data['Общая_цена']}")

    # Сохраняем PDF-документ
    c.save()

def create_invoice_pdf(data, filename="invoice.pdf"):
    """
    Генерирует PDF-накладную на основе переданных данных
    
    :param data: словарь с данными для накладной
    :param filename: имя выходного файла
    :return: путь к созданному файлу
    """
    try:
        # Регистрация шрифта с поддержкой кириллицы
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        
        # Создаем новый PDF-документ
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Установка шрифта
        c.setFont("DejaVuSans", 12)
        
        # Начальные координаты для печати
        y = height - 50
        
        # Заголовок накладной
        c.drawCentredString(width / 2, y, "Приложение 1.")
        y -= 30
        c.drawCentredString(width / 2, y, "Накладная")
        y -= 40
        
        # Информация о заказе
        c.drawString(100, y, f"Номер заказа: {data['order_number']}")
        y -= 20
        c.drawString(100, y, f"Дата и время сборки: {data['assembly_date']}")
        y -= 30
        
        # Информация о покупателе
        c.drawString(100, y, f"Покупатель: {data['customer_name']}")
        y -= 20
        c.drawString(100, y, f"Телефон: {data['phone']}")
        y -= 20
        c.drawString(100, y, f"Адрес доставки: {data['delivery_address']}")
        y -= 40
        
        # Таблица с товарами
        # Заголовок таблицы
        c.drawString(100, y, "| № | Наименование товара | Кол-во | Ед. | Цена за ед. | Итоговая цена |")
        y -= 20
        c.line(100, y, width - 100, y)
        y -= 20
        
        # Строки с товарами
        for i, item in enumerate(data['items'], start=1):
            item_line = f"| {i} | {item['name']} | {item['quantity']} | {item['unit']} | {item['unit_price']} | {item['total_price']} |"
            c.drawString(100, y, item_line)
            y -= 20
        
        # Итоговая сумма
        y -= 20
        c.drawString(100, y, f"Итого: {data['total_amount']} руб.")
        y -= 30
        
        # Информация о менеджере
        c.drawString(100, y, f"Менеджер: {data['manager_name']}")
        
        # Сохраняем PDF-документ
        c.save()
        
        return os.path.abspath(filename)
    except Exception as e:
        raise Exception(f"Ошибка при создании PDF: {str(e)}")

# Главная функция
if __name__ == "__main__":
    order_id = 1
    data = fetch_order_data(order_id)
    
    if data:
        create_pdf_receipt(data)
        print("PDF-чек успешно создан!")
    else:
        print("Заказ с таким ID не найден.")