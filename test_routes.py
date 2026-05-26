from flask import Blueprint
import database as db

# ===================================================================================
# МАРШРУТЫ ДЛЯ ТЕСТИРОВАНИЯ
# ===================================================================================

test_bp = Blueprint('test_routes', __name__)


@test_bp.route('/test-db')
def test_db():
    """Тестирование подключения к БД"""
    connection = db.get_connection()
    if connection:
        connection.close()
        return "✅ Подключение к базе данных db_museum успешно!"
    return "❌ Ошибка подключения к БД"


@test_bp.route('/show-tables')
def show_tables():
    """Показать все таблицы в БД"""
    try:
        result = db.execute_query('SHOW TABLES')
        if result:
            tables = [list(row.values())[0] for row in result]
            return f"<h2>Таблицы в db_museum:</h2><ul>{''.join([f'<li>{t}</li>' for t in tables])}</ul>"
        return "❌ Не удалось получить таблицы"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


@test_bp.route('/show-sessions')
def show_sessions():
    """Тестовый маршрут для проверки сеансов"""
    sessions = db.execute_query('SELECT * FROM session_schedule') or []
    result = '<h1>Данные из таблицы session_schedule:</h1>'
    for s in sessions:
        result += f'<p><strong>ID:</strong> {s["id"]}, <strong>Date:</strong> {s["session_date"]}, <strong>Time:</strong> {s["session_time"]}, <strong>Available:</strong> {s["available_tickets"]}/{s["total_tickets"]}</p>'
    return result


@test_bp.route('/show-categories')
def show_categories():
    """Тестовый маршрут для проверки категорий билетов"""
    categories = db.get_all_ticket_categories() or []
    result = '<h1>Данные из таблицы ticket_categories:</h1>'
    for cat in categories:
        result += f'<p><strong>ID:</strong> {cat["id"]}, <strong>Title:</strong> {cat["title"]}, <strong>Price:</strong> {cat["price"]} ₽, <strong>Pushkin:</strong> {cat["pushkin_card_allowed"]}</p>'
    return result


@test_bp.route('/show-columns')
def show_columns():
    """Показать структуру таблицы data_content"""
    try:
        result = db.execute_query('DESCRIBE data_content')
        if result:
            html = "<h2>Структура таблицы data_content:</h2><table border='1' style='border-collapse: collapse;'>"
            html += "<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th></tr>"
            for col in result:
                html += f"<tr><td>{col['Field']}</td><td>{col['Type']}</td><td>{col['Null']}</td><td>{col['Key']}</td></tr>"
            html += "</table>"
            return html
        return "❌ Не удалось получить структуру"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


@test_bp.route('/show-content')
def show_content():
    """Показать весь контент из data_content"""
    try:
        museums = db.get_content_by_category('museums') or []
        exhibitions = db.get_content_by_category('virtual_exhibitions') or []
        posters = db.get_content_by_category('poster') or []

        html = "<h1>Контент из БД</h1>"

        html += "<h2>Музеи:</h2><ul>"
        for m in museums:
            html += f"<li><strong>{m['title_card']}</strong> - {m['short_description_card']}<br>Изображение: {m['img_card']}</li>"
        html += "</ul>"

        html += "<h2>Виртуальные выставки:</h2><ul>"
        for e in exhibitions:
            html += f"<li><strong>{e['title_card']}</strong> - {e['img_card']}</li>"
        html += "</ul>"

        html += "<h2>Афиша:</h2><ul>"
        for p in posters:
            html += f"<li><strong>{p['title_card']}</strong> - {p['img_card']}<br>Дата: {p.get('date_of_the_event')}, Место: {p.get('location_of_the_event')}</li>"
        html += "</ul>"

        return html
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"
