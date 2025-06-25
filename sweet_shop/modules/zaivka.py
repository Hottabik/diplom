import os
import sqlite3
import random
import string
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

DB_PATH = 'db.db'
FONT_DIR = 'font'

def register_fonts():
    """Регистрация шрифтов с поддержкой кириллицы"""
    try:
        # Проверяем существование папки со шрифтами
        if not os.path.exists(FONT_DIR):
            os.makedirs(FONT_DIR)
            
        # Пути к файлам шрифтов (без дублирования 'font' в пути)
        font_path = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
        font_bold_path = os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')
        
        # Проверяем существование файлов шрифтов
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")
        if not os.path.exists(font_bold_path):
            raise FileNotFoundError(f"Файл шрифта не найден: {font_bold_path}")
        
        # Регистрируем шрифты
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
        
        # Проверяем успешность регистрации
        if 'DejaVuSans' not in pdfmetrics.getRegisteredFontNames():
            raise Exception("Не удалось зарегистрировать шрифт DejaVuSans")
            
        return True
    except Exception as e:
        print(f"Ошибка регистрации шрифтов: {e}")
        # Используем стандартные шрифты, которые точно есть в ReportLab
        try:
            pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica'))
            pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold'))
            return True
        except:
            # Если даже стандартные шрифты не работают, используем встроенные
            return False

def create_supply_request_pdf(items, output_dir="."):
    """Создание PDF с заявкой на поставку"""
    try:
        # Регистрируем шрифты
        fonts_registered = register_fonts()
        
        # Определяем какие шрифты использовать
        if fonts_registered and 'DejaVuSans' in pdfmetrics.getRegisteredFontNames():
            font_normal = 'DejaVuSans'
            font_bold = 'DejaVuSans-Bold'
        elif 'Helvetica' in pdfmetrics.getRegisteredFontNames():
            font_normal = 'Helvetica'
            font_bold = 'Helvetica-Bold'
        else:
            # Используем встроенные шрифты ReportLab
            font_normal = 'Times-Roman'
            font_bold = 'Times-Bold'

        # Создаем папку для документов
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"Заявка_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
        
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Шапка документа
        c.setFont(font_bold, 14)
        c.drawString(40*mm, height-30*mm, f"ЗАЯВКА НА ПОСТАВКУ ТОВАРОВ № {generate_request_number()}")
        
        # Параметры таблицы
        table_top = height - 50*mm
        col_widths = [10*mm, 25*mm, 95*mm, 20*mm, 15*mm]  # Ширина колонок
        line_height = 6*mm
        header_height = 8*mm
        
        # Заголовок таблицы
        c.setFont(font_bold, 10)
        headers = ["№", "Артикул", "Наименование", "Кол-во", "Ед."]
        
        # Рисуем линии таблицы вручную (более надежный способ)
        # Горизонтальные линии
        c.line(20*mm, table_top, 185*mm, table_top)  # Верхняя линия
        c.line(20*mm, table_top - header_height, 185*mm, table_top - header_height)  # Линия под заголовком
        c.line(20*mm, table_top - header_height - len(items)*line_height, 
              185*mm, table_top - header_height - len(items)*line_height)  # Нижняя линия
        
        # Вертикальные линии
        x_positions = [20*mm, 30*mm, 55*mm, 150*mm, 170*mm, 185*mm]
        for x in x_positions:
            c.line(x, table_top, x, table_top - header_height - len(items)*line_height)
        
        # Заполняем заголовки
        for i, header in enumerate(headers):
            c.drawString(x_positions[i] + 2*mm, table_top - header_height + 2*mm, header)
        
        # Заполняем данные
        c.setFont(font_normal, 9)
        for row, item in enumerate(items, 1):
            y_position = table_top - header_height - (row * line_height) + 2*mm
            c.drawString(x_positions[0] + 2*mm, y_position, str(row))
            c.drawString(x_positions[1] + 2*mm, y_position, item['articul'])
            c.drawString(x_positions[2] + 2*mm, y_position, item['name'][:40])  # Обрезаем длинные названия
            c.drawRightString(x_positions[3] + col_widths[3] - 2*mm, y_position, str(item['quantity']))
            c.drawString(x_positions[4] + 2*mm, y_position, item['unit'])
        
        # Подпись
        y_bottom = table_top - header_height - (len(items)+1)*line_height
        c.drawString(20*mm, y_bottom - 10*mm, f"Дата заявки: {datetime.now().strftime('%d.%m.%Y')}")
        c.drawString(20*mm, y_bottom - 20*mm, "Ответственный: ______________________ /_____________/")
        
        c.save()
        return filename
    except Exception as e:
        print(f"Ошибка создания PDF: {e}")
        return None

# Остальные функции остаются без изменений
def fetch_purchase_data(db_path=DB_PATH):
    """Получение данных о закупках из БД"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
    SELECT 
        pg.id,
        p.id_articul,
        p.name,
        pg.quantity,
        COALESCE(
            (SELECT unit FROM orders o WHERE o.articul = p.id_articul LIMIT 1),
            'шт.'
        ) as unit
    FROM purchase_goods pg
    JOIN products p ON pg.id_articul = p.id_articul
    ORDER BY p.name;
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [{
        'record_id': row[0],
        'articul': row[1],
        'name': row[2],
        'quantity': row[3],
        'unit': row[4]
    } for row in rows]

def generate_supply_request(parent=None, output_dir=None):
    """Основная функция генерации заявки"""
    try:
        # Определяем путь для сохранения
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_docs")
        
        items = fetch_purchase_data()
        if not items:
            QMessageBox.warning(parent, "Ошибка", "Нет товаров для формирования заявки!")
            return False
        
        pdf_path = create_supply_request_pdf(items, output_dir)
        if not pdf_path:
            QMessageBox.warning(parent, "Ошибка", "Не удалось создать файл заявки!")
            return False
            
        # Удаляем обработанные товары
        record_ids = [item['record_id'] for item in items]
        if not delete_processed_items(record_ids):
            QMessageBox.warning(parent, "Предупреждение", "Заявка создана, но не удалось очистить список товаров!")
        
        QMessageBox.information(parent, "Успех", f"Заявка успешно создана:\n{pdf_path}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(output_dir)))
        return True
    except Exception as e:
        QMessageBox.critical(parent, "Ошибка", f"Ошибка генерации:\n{str(e)}")
        return False

def generate_request_number():
    return ''.join(random.choice(string.digits) for _ in range(8))

def delete_processed_items(record_ids, db_path=DB_PATH):
    try:
        if record_ids:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM purchase_goods WHERE id IN ({','.join(['?']*len(record_ids))})", record_ids)
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка удаления товаров: {e}")
    finally:
        conn.close() if 'conn' in locals() else None
    return False