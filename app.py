from flask import Flask, render_template, request, jsonify, abort
from flask import session, redirect, url_for, flash
from functools import wraps
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import json
import secrets
import database as db

# Получаем абсолютный путь к текущей директории
template_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__,
            template_folder=os.path.join(template_dir, 'templates'),
            static_folder=static_dir)

UPLOAD_FOLDER = os.path.join(static_dir, 'images/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'your-secret-key-here'


# ===================================================================================
# МАРШРУТЫ
# ===================================================================================

@app.route('/')
def homepage():
    """Главная страница с карточками из БД"""
    museums = db.get_content_by_category('museums') or []
    virtual_exhibitions = db.get_content_by_category('virtual_exhibitions') or []
    posters = db.get_content_by_category('poster') or []

    return render_template('homepage.html',
                         museums=museums,
                         virtual_exhibitions=virtual_exhibitions,
                         events=posters)


@app.route('/about-us')
@app.route('/about-us/<int:museum_id>')
def about_us(museum_id=None):
    if museum_id is None:
        museums = db.get_content_by_category('museums')
        museum = museums[0] if museums else None
    else:
        museum = db.get_content_by_id(museum_id)
        if not museum:
            abort(404)

    return render_template('about_us.html', museum=museum)


@app.route('/order')
@app.route('/order/<int:museum_id>')
def order(museum_id=None):
    """Страница заказа билетов"""
    if museum_id is None:
        museums = db.get_content_by_category('museums')
        museum = museums[0] if museums else None
    else:
        museum = db.get_content_by_id(museum_id)
        if not museum:
            abort(404)

    today = datetime.now().date()
    week_later = today + timedelta(days=7)

    sessions = db.get_active_sessions(today, week_later) or []
    ticket_categories = db.get_all_ticket_categories() or []

    return render_template('order.html',
                         museum=museum,
                         sessions=sessions,
                         ticket_categories=ticket_categories,
                         today=today)


@app.route('/create-order', methods=['POST'])
def create_order():
    """Создание заказа"""
    try:
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        country_code = request.form.get('country_code', '+7')
        subscribe_news = request.form.get('subscribe_news') == 'on'
        accept_terms = request.form.get('accept_terms') == 'on'

        session_date = request.form.get('session_date')
        session_time = request.form.get('session_time')
        tickets_data = json.loads(request.form.get('tickets_data', '{}'))

        if not all([full_name, email, phone, session_date, session_time, accept_terms]):
            return jsonify({'success': False, 'error': 'Заполните все обязательные поля'})

        if not tickets_data or sum(tickets_data.values()) == 0:
            return jsonify({'success': False, 'error': 'Выберите хотя бы один билет'})

        session = db.get_session_by_date_time(session_date, session_time)
        if not session:
            return jsonify({'success': False, 'error': 'Сеанс не найден'})

        total_tickets = sum(int(qty) for qty in tickets_data.values())
        if session['available_tickets'] < total_tickets:
            return jsonify({'success': False, 'error': 'Недостаточно доступных билетов'})

        total_amount = 0
        for category_id, quantity in tickets_data.items():
            category = db.get_ticket_category_by_id(int(category_id))
            if category:
                total_amount += float(category['price']) * int(quantity)

        booking_code = secrets.token_hex(8).upper()
        booking_id = db.create_booking(
            session_id=session['id'],
            ticket_category_id=None,
            user_email=email,
            user_phone=phone,
            quantity=total_tickets,
            total_price=total_amount,
            payment_method=None,
            booking_code=booking_code
        )

        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        qr_token = secrets.token_urlsafe(32)

        order_id = db.create_order(
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,
            subscribe_news=subscribe_news,
            accept_terms=accept_terms,
            booking_id=booking_id,
            order_number=order_number,
            qr_code_token=qr_token,
            total_amount=total_amount
        )

        new_available = session['available_tickets'] - total_tickets
        new_reserved = session['reserved_tickets'] + total_tickets
        db.update_session_tickets(session['id'], new_available, new_reserved)

        return jsonify({
            'success': True,
            'order_id': order_id,
            'order_number': order_number,
            'total_amount': float(total_amount)
        })

    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


# --- КОНФИГУРАЦИЯ АДМИНА ---
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'  # В реальном проекте используйте хеширование!


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# --- МАРШРУТЫ АДМИНКИ ---

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин или пароль')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    # Статистика для дашборда
    orders = db.get_all_orders() or []
    count_museums = len(db.get_content_by_category('museums') or [])
    count_orders = len(orders)
    recent_orders = orders[:5]

    return render_template('admin/content_list.html',
                           title_page="Дашборд (Музеи)",
                           items=db.get_content_by_category('museums'),
                           category='museums')  # Для простоты перенаправляем на список музеев, можно сделать отдельный dashboard.html


@app.route('/admin/content/<category>')
@login_required
def admin_content(category):
    titles = {
        'museums': 'Музеи',
        'virtual_exhibitions': 'Виртуальные выставки',
        'poster': 'Афиша'
    }
    items = db.get_content_by_category(category) or []
    return render_template('admin/content_list.html',
                           items=items,
                           category=category,
                           title_page=titles.get(category, category))


@app.route('/admin/edit/<category>/<int:content_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(category, content_id):
    item = None
    if content_id > 0:
        item = db.get_content_by_id(content_id)

    if request.method == 'POST':
        # 1. Сбор текстовых полей
        title = request.form.get('title')
        short_desc = request.form.get('short_desc')
        main_text = request.form.get('main_text')  # Было full_desc, стало main_text как в БД

        b_txt1 = request.form.get('block_text_1')
        b_txt2 = request.form.get('block_text_2')
        b_txt3 = request.form.get('block_text_3')

        # 2. Вспомогательная функция для сохранения файлов
        def save_file(file_obj, current_path):
            if file_obj and file_obj.filename:
                filename = secure_filename(file_obj.filename)
                file_obj.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return f"images/uploads/{filename}"
            return current_path

        # 3. Обработка всех картинок
        # Карточка
        img_card = save_file(request.files.get('img_card_file'), request.form.get('current_img_card'))

        # Главная страница
        main_image = save_file(request.files.get('main_image_file'), request.form.get('current_main_image'))

        # Блоки 1-3
        b_img1 = save_file(request.files.get('block_image_1_file'), request.form.get('current_block_image_1'))
        b_img2 = save_file(request.files.get('block_image_2_file'), request.form.get('current_block_image_2'))
        b_img3 = save_file(request.files.get('block_image_3_file'), request.form.get('current_block_image_3'))

        # 4. Сохранение в БД
        if content_id == 0:
            db.insert_content(category, title, short_desc, img_card, main_image, main_text,
                              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3)
        else:
            db.update_content(content_id, title, short_desc, img_card, main_image, main_text,
                              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3)

        return redirect(url_for('admin_content', category=category))

    return render_template('admin/edit_form.html', item=item, category=category)


@app.route('/admin/delete/<int:id>')
@login_required
def admin_delete(id):
    db.delete_content(id)
    return redirect(request.referrer or url_for('admin_dashboard'))


@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = db.get_all_orders()

    return render_template('admin/orders_list.html', orders=orders)


@app.route('/virtual-exhibition')
def virtual_exhibition():
    return render_template('virtual-exhi.html')

@app.route('/poster')
def poster():
    museums_for_poster = db.get_content_by_category('museums') or []
    return render_template('poster.html', museums=museums_for_poster)

@app.route('/about_the_museum')
def about_the_museum():
    return render_template('about_the_museum.html')


# ===================================================================================
# ВСПОМОГАТЕЛЬНЫЕ МАРШРУТЫ ДЛЯ ТЕСТИРОВАНИЯ
# ===================================================================================

@app.route('/test-db')
def test_db():
    """Тестирование подключения к БД"""
    connection = db.get_connection()
    if connection:
        connection.close()
        return "✅ Подключение к базе данных db_museum успешно!"
    return "❌ Ошибка подключения к БД"


@app.route('/show-tables')
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


@app.route('/show-sessions')
def show_sessions():
    """Тестовый маршрут для проверки сеансов"""
    sessions = db.execute_query('SELECT * FROM session_schedule') or []
    result = '<h1>Данные из таблицы session_schedule:</h1>'
    for s in sessions:
        result += f'<p><strong>ID:</strong> {s["id"]}, <strong>Date:</strong> {s["session_date"]}, <strong>Time:</strong> {s["session_time"]}, <strong>Available:</strong> {s["available_tickets"]}/{s["total_tickets"]}</p>'
    return result


@app.route('/show-categories')
def show_categories():
    """Тестовый маршрут для проверки категорий билетов"""
    categories = db.get_all_ticket_categories() or []
    result = '<h1>Данные из таблицы ticket_categories:</h1>'
    for cat in categories:
        result += f'<p><strong>ID:</strong> {cat["id"]}, <strong>Title:</strong> {cat["title"]}, <strong>Price:</strong> {cat["price"]} ₽, <strong>Pushkin:</strong> {cat["pushkin_card_allowed"]}</p>'
    return result


@app.route('/show-columns')
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


@app.route('/show-content')
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
            html += f"<li><strong>{p['title_card']}</strong> - {p['img_card']}</li>"
        html += "</ul>"

        return html
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
