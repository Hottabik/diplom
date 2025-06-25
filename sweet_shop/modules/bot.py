import sqlite3
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

TOKEN = '8006570487:AAGwycHDTkolHmKizoidMysCZ09XsjfHeAU'

dp = Dispatcher()
loop = asyncio.get_event_loop()

# Хранилище для пользователей, ожидающих ввода недостающих товаров
state = {}

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    return conn


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply('''/orders - список заказов''')

async def second(bot):
    while True:
        try:
            conn = get_db_connection()
            new_orders = conn.execute('''
                SELECT 
                    o.order_number, 
                    a.telegram_id,
                    (
                        SELECT GROUP_CONCAT(product_info, '\n   • ')
                        FROM (
                            SELECT DISTINCT
                                product_name || ' (' || quantity || ' ' || unit || ')' AS product_info
                            FROM orders o2
                            WHERE o2.order_number = o.order_number
                        )
                    ) AS products_list
                FROM assembling a
                JOIN orders o ON a.order_id = o.id
                WHERE a.id_status = 1
                GROUP BY o.order_number, a.telegram_id
            ''').fetchall()

            if new_orders:
                for order in new_orders:
                    user_id = order['telegram_id']
                    order_number = order['order_number']
                    products_list = order['products_list'] or ''
                    message_text = (
                        f"🎉 У вас новый заказ!\n\n"
                        f"🔹 Номер заказа: {order_number}\n"
                        f"📦 Товары:\n   • {products_list}"
                    )

                    conn.execute('''
                        UPDATE assembling
                        SET id_status = 2
                        WHERE order_id = (SELECT id FROM orders WHERE order_number = ?) AND telegram_id = ?
                    ''', (order_number, user_id))
                    conn.commit()
                    await bot.send_message(chat_id=user_id, text=message_text)

            conn.close()
            await asyncio.sleep(10)

        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
            await asyncio.sleep(10)



@dp.message(Command("orders"))
async def show_user_orders(message: types.Message):
    conn = get_db_connection()
    try:
        orders = conn.execute('''
SELECT 
    o.order_number,
    MIN(o.order_date) AS order_date,
    MAX(os.status) AS status,
    (
        SELECT GROUP_CONCAT(product_info, ', ')
        FROM (
            SELECT DISTINCT
                product_name || ' (' || quantity || ' ' || unit || ')' AS product_info
            FROM orders o2
            WHERE o2.order_number = o.order_number
        )
    ) AS products_list
FROM orders o
JOIN assembling a ON o.id = a.order_id
LEFT JOIN orders_status os ON a.id_status = os.id_status
WHERE a.telegram_id = ? AND a.id_status = 2
GROUP BY o.order_number
ORDER BY order_date DESC;
        ''', (message.from_user.id,)).fetchall()

        if not orders:
            await message.answer("📭 У вас нет активных заказов.")
            return

        for order in orders:
            # Разбиваем строку товаров по запятой и добавляем переносы с маркером
            products_lines = order['products_list'].split(', ')
            products_text = "\n   • ".join(products_lines)

            response = (
                f"🔹 Номер заказа: {order['order_number']}\n"
                f"📅 Дата заказа: {order['order_date']}\n"
                f"🟢 Статус: {order['status']}\n"
                f"📦 Товары:\n   • {products_text}\n"
                "────────────────────"
            )

            buttons = [
                [InlineKeyboardButton(text="Завершить заказ", callback_data=f"succesfull_{order['order_number']}")],
                [InlineKeyboardButton(text="Отложить заказ", callback_data=f"cancelled_{order['order_number']}")]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(response, reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"Произошла ошибка при получении заказов: {str(e)}")
    finally:
        conn.close()



@dp.callback_query(lambda c: c.data.startswith("succesfull_"))
async def handle_succesfull_order(callback_query: CallbackQuery):
    order_number = callback_query.data.split("_")[1]
    conn = get_db_connection()
    try:
        conn.execute('UPDATE users SET isFree = "Y" WHERE telegram_id = ?', (callback_query.from_user.id,))
        conn.execute('''
            UPDATE assembling 
            SET id_status = 3 
            WHERE order_id = (SELECT id FROM orders WHERE order_number = ?)
        ''', (order_number,))
        conn.commit()

        # Формируем сообщение для менеджеров
        sender = callback_query.from_user.username or f"id: {callback_query.from_user.id}"
        notify_text = f"✅ Заказ №{order_number} был собран пользователем @{sender}."

        # Получаем всех менеджеров (role_id = 1)
        managers = conn.execute('SELECT telegram_id FROM users WHERE role_id = 1').fetchall()

        if not managers:
            await callback_query.answer("⚠️ Менеджеры не найдены в базе.", show_alert=True)
            return

        # Отправляем уведомление менеджерам
        for manager in managers:
            try:
                await bot.send_message(chat_id=manager['telegram_id'], text=notify_text)
            except Exception as e:
                logging.warning(f"Не удалось отправить сообщение менеджеру {manager['telegram_id']}: {e}")

        await callback_query.answer("✅ Заказ завершён. Менеджеры уведомлены.")

    except Exception as e:
        logging.error(f"Ошибка при завершении заказа: {e}")
        await callback_query.answer("❗ Произошла ошибка при завершении заказа.", show_alert=True)

    finally:
        conn.close()


@dp.callback_query(lambda c: c.data.startswith("cancelled_"))
async def handle_cancelled_order(callback_query: CallbackQuery):
    order_number = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    state[user_id] = order_number
    await callback_query.message.answer(
        f"✏️ Укажите список недостающих товаров для заказа {order_number}, через запятую:"
    )
    await callback_query.answer()


@dp.message()
async def handle_missing_input(message: types.Message):
    user_id = message.from_user.id
    if user_id not in state:
        return

    order_number = state.pop(user_id)
    missing_raw = message.text.strip()
    missing_items = [item.strip() for item in missing_raw.split(",") if item.strip()]

    if not missing_items:
        await message.reply("❗ Вы не указали ни одного товара.")
        return

    product_list = "\n".join(f"❌ {name}" for name in missing_items)
    sender = message.from_user.username or f"id: {user_id}"
    message_text = (
        f"📦 Заказ № {order_number} от @{sender}\n"
        f"⛔ Недостающие товары:\n\n{product_list}"
    )

    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE assembling 
            SET id_status = 4 
            WHERE order_id = (SELECT id FROM orders WHERE order_number = ?)
        ''', (order_number,))
        conn.execute('UPDATE users SET isFree = "Y" WHERE telegram_id = ?', (user_id,))
        managers = conn.execute('SELECT telegram_id FROM users WHERE role_id = 1').fetchall()
        conn.commit()
        conn.close()

        if not managers:
            await message.reply("❗ Менеджеры не найдены в базе.")
            return

        for manager in managers:
            try:
                await bot.send_message(chat_id=manager['telegram_id'], text=message_text)
            except Exception as e:
                logging.warning(f"Не удалось отправить сообщение менеджеру {manager['telegram_id']}: {e}")

        await message.reply("✅ Заказ отложен и информация отправлена менеджеру(ам).")

    except Exception as e:
        logging.error(f"Ошибка при отправке недостающих товаров: {e}")
        await message.reply("Произошла ошибка при обработке заказа.")


async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.create_task(second(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
