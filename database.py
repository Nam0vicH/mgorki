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


def update_session_tickets(session_id, available, reserved):
    """Обновить количество билетов сеанса"""
    query = """
        UPDATE session_schedule
        SET available_tickets = %s, reserved_tickets = %s
        WHERE id = %s
    """
    return execute_query(query, (available, reserved, session_id), fetch=False)


# ===================================================================================
# ФУНКЦИИ ДЛЯ ticket_bookings
# ===================================================================================

def create_booking(session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_code):
    """Создать бронирование"""
    query = """
        INSERT INTO ticket_bookings
        (session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_status, booking_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s)
    """
    return execute_query(query, (session_id, ticket_category_id, user_email, user_phone, quantity, total_price, payment_method, booking_code), fetch=False)


# ===================================================================================
# ФУНКЦИИ ДЛЯ orders
# ===================================================================================

def create_order(full_name, email, phone, country_code, subscribe_news, accept_terms, booking_id, order_number, qr_code_token, total_amount):
    """Создать заказ"""
    query = """
        INSERT INTO orders
        (full_name, email, phone, country_code, subscribe_news, accept_terms, booking_id, order_number, order_status, qr_code_token, qr_code_url, total_amount, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'new', %s, %s, %s, 'unpaid')
    """
    qr_code_url = f"/qr/{qr_code_token}"
    return execute_query(query, (full_name, email, phone, country_code, subscribe_news, accept_terms, booking_id, order_number, qr_code_token, qr_code_url, total_amount), fetch=False)


def get_order_by_id(order_id):
    """Получить заказ по ID"""
    query = "SELECT * FROM orders WHERE id = %s"
    result = execute_query(query, (order_id,))
    return result[0] if result else None