from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def create_invoice_pdf(invoice_data):
    # Регистрируем шрифты с поддержкой кириллицы
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'font\DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'font\DejaVuSans-Bold.ttf'))
    
    filename = f"Накладная_{invoice_data['order_number']}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Шапка
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(30, height - 40, 'ООО "ВК Тандем"')
    c.setFont("DejaVuSans", 10)
    c.drawString(30, height - 55, 'ИНН 7704404323   КПП 772901001')
    c.drawString(30, height - 70, '119530, г. Москва, ш. Очаковское, д. 36, этаж 1 пом 4')

    # Название документа
    c.setFont("DejaVuSans-Bold", 14)
    c.drawCentredString(width / 2, height - 100, f"НАКЛАДНАЯ № {invoice_data['order_number']} от {invoice_data['assembly_date']}")

    # Инфо о покупателе
    y = height - 130
    c.setFont("DejaVuSans", 10)
    c.drawString(30, y, f"Покупатель: {invoice_data['customer_name']}")
    y -= 15
    c.drawString(30, y, f"Телефон: {invoice_data['phone']}")
    y -= 15
    c.drawString(30, y, f"Адрес доставки: {invoice_data['delivery_address']}")

    # Таблица товаров
    y -= 40
    data = [['№', 'Наименование', 'Кол-во', 'Ед.', 'Цена за ед.', 'Сумма руб.']]
    for i, item in enumerate(invoice_data['items'], 1):
        name = item['name']
        if len(name) > 40:
            name = name[:40] + "..."  # обрезаем длинные названия
        data.append([
            str(i),
            name,
            str(item['quantity']),
            item['unit'],
            f"{item['unit_price']}",
            f"{item['total_price']}"
        ])

    table = Table(data, colWidths=[25*mm, 65*mm, 25*mm, 20*mm, 30*mm, 30*mm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    table.wrapOn(c, width, height)
    table_height = 20 * len(data)
    table.drawOn(c, 30, y - table_height)

    # Итоги
    y = y - table_height - 20
    c.setFont("DejaVuSans-Bold", 11)
    c.drawString(30, y, f"Итого к оплате: {invoice_data['total_amount']} ₽")
    y -= 20
    c.setFont("DejaVuSans", 10)
    c.drawString(30, y, f"Менеджер: {invoice_data['manager_name']}")

    # Подписи
    y -= 40
    c.drawString(30, y, "Ответственный: ______________________ /" + invoice_data['manager_name'] + "/")
    y -= 20
    c.drawString(30, y, "Получил: _____________________________ /_____________/")

    c.save()
    return filename
