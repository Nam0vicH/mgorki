import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'db_museum',
    'port': 3306
}


def get_connection():
    """Получить соединение с БД"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


def execute_query(query, params=None, fetch=True):
    """Выполнить запрос и вернуть результат"""
    connection = get_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
        return result
    except Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ===================================================================================
# ФУНКЦИИ ДЛЯ data_content
# ===================================================================================

def get_content_by_category(category):
    """Получить контент по категории"""
    query = "SELECT * FROM data_content WHERE category = %s"
    return execute_query(query, (category,))


def get_content_by_id(content_id):
    """Получить контент по ID"""
    query = "SELECT * FROM data_content WHERE id = %s"
    result = execute_query(query, (content_id,))
    return result[0] if result else None


# ===================================================================================
# ФУНКЦИИ ДЛЯ ticket_categories
# ===================================================================================

def get_all_ticket_categories():
    """Получить все категории билетов"""
    query = "SELECT * FROM ticket_categories"
    return execute_query(query)


def get_ticket_category_by_id(category_id):
    """Получить категорию билета по ID"""
    query = "SELECT * FROM ticket_categories WHERE id = %s"
    result = execute_query(query, (category_id,))
    return result[0] if result else None


# ===================================================================================
# ФУНКЦИИ ДЛЯ session_schedule
# ===================================================================================

def get_active_sessions(start_date, end_date):
    """Получить активные сеансы в диапазоне дат"""
    query = """
        SELECT * FROM session_schedule
        WHERE is_active = 1
        AND session_date >= %s
        AND session_date <= %s
        ORDER BY session_date, session_time
    """
    return execute_query(query, (start_date, end_date))


def get_session_by_date_time(session_date, session_time):
    """Получить сеанс по дате и времени"""
    query = "SELECT * FROM session_schedule WHERE session_date = %s AND session_time = %s"
    result = execute_query(query, (session_date, session_time))
    return result[0] if result else None


def update_session_tickets(session_id, available, sold):
    """Обновить количество билетов сеанса (ИСПРАВЛЕНО: reserved -> sold)"""
    query = """
        UPDATE session_schedule
        SET available_tickets = %s, sold_tickets = %s
        WHERE id = %s
    """
    return execute_query(query, (available, sold, session_id), fetch=False)


# ===================================================================================
# ФУНКЦИИ ДЛЯ ticket_bookings
# ===================================================================================

def create_booking(session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_code):
    """Создать бронирование"""
    # ticket_category_id и payment_method теперь обязательны в SQL
    query = """
        INSERT INTO ticket_bookings
        (session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_status, booking_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s)
    """
    return execute_query(query, (session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_code), fetch=False)


# ===================================================================================
# ФУНКЦИИ ДЛЯ orders
# ===================================================================================

def create_order(full_name, email, phone, country_code, booking_id, order_number, qr_code_token, total_amount):
    """Создать заказ (ИСПРАВЛЕНО: удалены subscribe_news и accept_terms)"""
    query = """
        INSERT INTO orders
        (full_name, email, phone, country_code, booking_id, order_number, order_status, qr_code_token, qr_code_url, total_amount, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, 'new', %s, %s, %s, 'unpaid')
    """
    qr_code_url = f"/qr/{qr_code_token}"
    return execute_query(query, (full_name, email, phone, country_code, booking_id, order_number, qr_code_token, qr_code_url, total_amount), fetch=False)


def get_order_by_id(order_id):
    """Получить заказ по ID"""
    query = "SELECT * FROM orders WHERE id = %s"
    result = execute_query(query, (order_id,))
    return result[0] if result else None

# ===================================================================================
# ФУНКЦИИ ДЛЯ АДМИНКИ
# ===================================================================================

def insert_content(category, title, short_desc, img_card, main_image, main_text,
                  b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3):
    """Добавить новый контент"""
    query = """
        INSERT INTO data_content 
        (category, title_card, short_description_card, img_card, 
         main_image, main_text,
         block_image_1, block_text_1,
         block_image_2, block_text_2,
         block_image_3, block_text_3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (category, title, short_desc, img_card, main_image, main_text,
              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3)
    return execute_query(query, params, fetch=False)

def update_content(content_id, title, short_desc, img_card, main_image, main_text,
                  b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3):
    """Обновить контент"""
    query = """
        UPDATE data_content 
        SET title_card=%s, short_description_card=%s, img_card=%s,
            main_image=%s, main_text=%s,
            block_image_1=%s, block_text_1=%s,
            block_image_2=%s, block_text_2=%s,
            block_image_3=%s, block_text_3=%s
        WHERE id=%s
    """
    params = (title, short_desc, img_card, main_image, main_text,
              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3, content_id)
    return execute_query(query, params, fetch=False)

def delete_content(content_id):
    """Удалить контент"""
    query = "DELETE FROM data_content WHERE id = %s"
    return execute_query(query, (content_id,), fetch=False)

def get_all_orders():
    """Получить все заказы для админки"""
    query = "SELECT * FROM orders ORDER BY id DESC"
    return execute_query(query)

def update_order_status(order_id, status):
    """Обновить статус заказа"""
    query = "UPDATE orders SET order_status = %s WHERE id = %s"
    return execute_query(query, (status, order_id), fetch=False)