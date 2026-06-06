import json
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, abort,
    session, redirect, url_for, flash
)
from werkzeug.utils import secure_filename
from test_routes import test_bp

import database as db

# Получаем абсолютный путь к текущей директории
template_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.abspath(os.path.join(template_dir, 'static'))

app = Flask(__name__,
            template_folder=os.path.join(template_dir, 'templates'),
            static_folder=static_dir)

app.register_blueprint(test_bp)

UPLOAD_FOLDER = os.path.join(static_dir, 'images/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'your-secret-key-here'

# Автоматически генерируем расписание сеансов на 7 дней вперед при запуске проекта
try:
    db.generate_weekly_schedule()
except Exception as e:
    print(f"Не удалось сгенерировать расписание при запуске: {e}")


# ===================================================================================
# МАРШРУТЫ
# ===================================================================================

@app.route('/')
def homepage():
    """Главная страница с карточками из БД"""
    museums = db.get_content_by_category('museums') or []
    virtual_exhibitions = db.get_content_by_category('virtual_exhibitions') or []
    posters = db.get_content_by_category('poster') or []
    hero_images = db.get_content_by_category('hero_section') or []

    return render_template('homepage.html',
                           museums=museums,
                           virtual_exhibitions=virtual_exhibitions,
                           events=posters,
                           hero_images=hero_images)


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

    event_id = museum['id'] if museum else 1
    sessions = db.get_active_sessions(event_id, today, week_later) or []
    
    event_category = museum['category'] if museum else 'museums'
    ticket_cat_type = 'poster' if event_category == 'poster' else 'museum'
    
    ticket_categories = db.get_ticket_categories_by_type(ticket_cat_type) or []

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
        # subscribe_news = request.form.get('subscribe_news') == 'on'
        accept_terms = request.form.get('accept_terms') == 'on'
        payment_method = request.form.get('payment_method', 'bank_card')

        session_date = request.form.get('session_date')
        session_time = request.form.get('session_time')
        museum_id = request.form.get('museum_id')
        tickets_data = json.loads(request.form.get('tickets_data', '{}'))

        if not all([full_name, email, phone, session_date, session_time, museum_id, accept_terms]):
            return jsonify({'success': False, 'error': 'Заполните все обязательные поля'})

        import re
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return jsonify({'success': False, 'error': 'Введите корректный E-mail (например, ivan@mail.ru)'})
            
        if len(phone) < 18:
            return jsonify({'success': False, 'error': 'Введите корректный номер телефона полностью'})
            
        if len(full_name.strip().split()) < 2:
            return jsonify({'success': False, 'error': 'Введите Фамилию и Имя полностью'})

        if not tickets_data or sum(tickets_data.values()) == 0:
            return jsonify({'success': False, 'error': 'Выберите хотя бы один билет'})

        session_obj = db.get_session_by_date_time(museum_id, session_date, session_time)
        if not session_obj:
            return jsonify({'success': False, 'error': 'Сеанс не найден'})

        total_tickets = sum(int(qty) for qty in tickets_data.values())
        if session_obj['available_tickets'] < total_tickets:
            return jsonify({'success': False, 'error': 'Недостаточно доступных билетов'})

        total_amount = 0
        first_category_id = None

        for category_id, quantity in tickets_data.items():
            if int(quantity) > 0:

                if first_category_id is None:
                    first_category_id = int(category_id)

                category = db.get_ticket_category_by_id(int(category_id))
                if category:
                    total_amount += float(category['price']) * int(quantity)

        booking_code = secrets.token_hex(8).upper()
        booking_id = db.create_booking(
            session_id=session_obj['id'],
            ticket_category_id=first_category_id,
            user_email=email,
            user_phone=phone,
            quantity=total_tickets,
            total_price=total_amount,
            payment_method=payment_method,
            booking_code=booking_code
        )

        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        qr_token = secrets.token_urlsafe(32)

        order_id = db.create_order(
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,
            booking_id=booking_id,
            order_number=order_number,
            qr_code_token=qr_token,
            total_amount=total_amount
        )

        new_available = session_obj['available_tickets'] - total_tickets
        current_sold = session_obj.get('sold_tickets', 0)
        new_sold = current_sold + total_tickets

        db.update_session_tickets(session_obj['id'], new_available, new_sold)

        return jsonify({
            'success': True,
            'order_id': order_id,
            'order_number': order_number,
            'total_amount': float(total_amount)
        })

    except Exception as err:
        print(f"Error creating order: {str(err)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(err)})


@app.route('/payment/<int:order_id>')
def payment(order_id):
    """Страница оплаты заказа"""
    order_data = db.get_order_by_id(order_id)
    if not order_data:
        abort(404)
    if order_data.get('payment_status') == 'paid':
        return redirect(url_for('ticket', order_id=order_id))
    return render_template('payment.html', order=order_data)


@app.route('/process-payment/<int:order_id>', methods=['POST'])
def process_payment(order_id):
    """Обработка оплаты (демонстрация)"""
    order_data = db.get_order_by_id(order_id)
    if not order_data:
        abort(404)

    # Обновляем статус оплаты в БД
    db.execute_query("UPDATE orders SET payment_status = 'paid' WHERE id = %s", (order_id,), fetch=False)

    return redirect(url_for('ticket', order_id=order_id))


@app.route('/ticket/<int:order_id>')
def ticket(order_id):
    """Страница с билетом и QR-кодом после успешной оплаты"""
    order_data = db.get_order_by_id(order_id)
    if not order_data:
        abort(404)
    if order_data.get('payment_status') != 'paid':
        return redirect(url_for('payment', order_id=order_id))

    # Формируем URL для QR-кода на основе токена
    qr_data = request.host_url.rstrip('/') + url_for('verify_qr', token=order_data.get('qr_code_token'))
    # Используем публичный API для генерации картинки QR
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_data}"

    return render_template('ticket.html', order=order_data, qr_image_url=qr_image_url)


@app.route('/qr/<token>')
def verify_qr(token):
    """Маршрут для проверки QR-кода (заглушка)"""
    order_data = db.execute_query("SELECT * FROM orders WHERE qr_code_token = %s", (token,))
    if not order_data:
        return "Недействительный QR-код"
    return f"Билет действителен. Заказ: {order_data[0]['order_number']}"


@app.route('/museum_programs/<int:exhibition_id>')
def museum_programs(exhibition_id):
    exhibition = db.get_content_by_id(exhibition_id)
    if not exhibition:
        abort(404)
    return render_template('museum_programs.html', exhibition=exhibition)


@app.route('/poster')
def poster():
    museums = db.get_content_by_category('museums') or []
    return render_template('poster.html', museums=museums)


@app.route('/poster_detail/<int:poster_id>')
def poster_detail(poster_id):
    poster_obj = db.get_content_by_id(poster_id)
    if not poster_obj:
        abort(404)
    return render_template('poster_detail.html', poster=poster_obj)


@app.route('/about_the_museum')
def about_the_museum():
    return render_template('about_the_museum.html')


@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    if not q or len(q) < 2:
        return jsonify([])
    
    results = db.search_content(q)
    formatted = []
    
    for r in (results or []):
        url = '#'
        if r['category'] == 'museums':
            url = url_for('about_us', museum_id=r['id'])
        elif r['category'] == 'virtual_exhibitions':
            url = url_for('museum_programs', exhibition_id=r['id'])
        elif r['category'] == 'poster':
            url = url_for('poster_detail', poster_id=r['id'])
            
        desc = r['short_description_card'] or ''
        # Очищаем от HTML тегов если есть
        import re
        desc = re.sub(r'<[^>]+>', '', desc)
        if len(desc) > 100:
            desc = desc[:100] + '...'
            
        formatted.append({
            'title': r['title_card'],
            'desc': desc,
            'url': url,
            'image': url_for('static', filename=r['img_card']) if r['img_card'] else ''
        })
        
    return jsonify(formatted)


# ===================================================================================
# АДМИН ПАНЕЛЬ
# ===================================================================================

# --- КОНФИГУРАЦИЯ АДМИНА ---
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'


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
                           category='museums',
                           count_museums=count_museums,
                           count_orders=count_orders,
                           recent_orders=recent_orders)


@app.route('/admin/content/<category>')
@login_required
def admin_content(category):
    titles = {
        'museums': 'Музеи',
        'virtual_exhibitions': 'Музейные программы',
        'poster': 'Афиша',
        'hero_section': 'Главный экран'
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
        title = request.form.get('title')
        short_desc = request.form.get('short_desc')
        main_text = request.form.get('main_text')

        date_event = request.form.get('date_of_the_event')
        if date_event == '':
            date_event = None

        location_event = request.form.get('location_of_the_event')
        if not location_event:
            location_event = ""

        b_txt1 = request.form.get('block_text_1')
        b_txt2 = request.form.get('block_text_2')
        b_txt3 = request.form.get('block_text_3')

        from werkzeug.datastructures import FileStorage
        def save_file(file_obj: FileStorage | None, current_path: str) -> str:
            if file_obj and file_obj.filename:
                folder_map = {
                    'museums': 'museums',
                    'virtual_exhibitions': 'virtual',
                    'poster': 'posters',
                    'hero_section': 'hero'
                }

                subfolder = folder_map.get(category, 'uploads')
                save_dir = os.path.join(static_dir, 'images', subfolder)
                os.makedirs(save_dir, exist_ok=True)

                filename = secure_filename(file_obj.filename)
                new_path = f"images/{subfolder}/{filename}"
                file_obj.save(os.path.join(save_dir, filename))
                
                if current_path and current_path != new_path:
                    old_file_path = os.path.join(static_dir, current_path)
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old image: {e}")
                            
                return new_path

            return current_path

        img_card = save_file(request.files.get('img_card_file'), request.form.get('current_img_card'))
        main_image = save_file(request.files.get('main_image_file'), request.form.get('current_main_image'))
        b_img1 = save_file(request.files.get('block_image_1_file'), request.form.get('current_block_image_1'))
        b_img2 = save_file(request.files.get('block_image_2_file'), request.form.get('current_block_image_2'))
        b_img3 = save_file(request.files.get('block_image_3_file'), request.form.get('current_block_image_3'))

        if content_id == 0:
            db.insert_content(category, title, short_desc, img_card,
                              date_event, location_event,  # Передаем новые поля
                              main_image, main_text,
                              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3)
        else:
            db.update_content(content_id, title, short_desc, img_card,
                              date_event, location_event,  # Передаем новые поля
                              main_image, main_text,
                              b_img1, b_txt1, b_img2, b_txt2, b_img3, b_txt3)

        return redirect(url_for('admin_content', category=category))

    return render_template('admin/edit_form.html', item=item, category=category)


@app.route('/admin/delete/<int:item_id>')
@login_required
def admin_delete(item_id):
    item = db.get_content_by_id(item_id)
    if item:
        img_fields = ['img_card', 'main_image', 'block_image_1', 'block_image_2', 'block_image_3']
        for field in img_fields:
            if item.get(field):
                file_path = os.path.join(static_dir, item[field])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting image {file_path}: {e}")
                        
        db.delete_content(item_id)
    return redirect(request.referrer or url_for('admin_dashboard'))


@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = db.get_all_orders()
    return render_template('admin/orders_list.html', orders=orders)


@app.route('/admin/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    new_status = request.form.get('order_status')
    if new_status:
        db.update_order_status(order_id, new_status)
        flash(f'Статус заказа #{order_id} успешно обновлен.')
    return redirect(url_for('admin_orders'))


# --- КАТЕГОРИИ БИЛЕТОВ ---

@app.route('/admin/ticket_categories')
@login_required
def admin_ticket_categories():
    categories = db.get_all_ticket_categories()
    return render_template('admin/ticket_categories_list.html', categories=categories)

@app.route('/admin/ticket_categories/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def admin_ticket_categories_edit(cat_id):
    category = None
    if cat_id > 0:
        category = db.get_ticket_category_by_id(cat_id)
        
    if request.method == 'POST':
        c_type = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description', '')
        price = request.form.get('price', 0)
        
        if cat_id == 0:
            db.insert_ticket_category(c_type, title, description, price)
            flash('Категория успешно добавлена.')
        else:
            db.update_ticket_category(cat_id, c_type, title, description, price)
            flash('Категория успешно обновлена.')
            
        return redirect(url_for('admin_ticket_categories'))
        
    return render_template('admin/ticket_categories_edit.html', category=category)

@app.route('/admin/ticket_categories/delete/<int:cat_id>')
@login_required
def admin_ticket_categories_delete(cat_id):
    db.delete_ticket_category(cat_id)
    flash('Категория билета удалена.')
    return redirect(url_for('admin_ticket_categories'))


# --- СЕАНСЫ И РАСПИСАНИЕ ---

@app.route('/admin/sessions')
@login_required
def admin_sessions():
    sessions = db.get_all_sessions_with_events()
    return render_template('admin/sessions_list.html', sessions=sessions)

@app.route('/admin/sessions/edit/<int:session_id>', methods=['GET', 'POST'])
@login_required
def admin_sessions_edit(session_id):
    session_obj = None
    if session_id > 0:
        session_obj = db.get_session_by_id(session_id)
        
    events_museums = db.get_content_by_category('museums') or []
    events_exhibitions = db.get_content_by_category('virtual_exhibitions') or []
    events_posters = db.get_content_by_category('poster') or []
    all_events = events_museums + events_exhibitions + events_posters
    
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        session_date = request.form.get('session_date')
        session_time = request.form.get('session_time')
        total_tickets = request.form.get('total_tickets', 50)
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        
        if session_id == 0:
            db.insert_session(event_id, session_date, session_time, total_tickets, is_active)
            flash('Сеанс успешно добавлен.')
        else:
            db.update_session(session_id, event_id, session_date, session_time, total_tickets, is_active)
            flash('Сеанс успешно обновлен.')
            
        return redirect(url_for('admin_sessions'))
        
    return render_template('admin/sessions_edit.html', session_obj=session_obj, all_events=all_events)

@app.route('/admin/sessions/delete/<int:session_id>')
@login_required
def admin_sessions_delete(session_id):
    db.delete_session(session_id)
    flash('Сеанс удален.')
    return redirect(url_for('admin_sessions'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(502)
def bad_gateway(e):
    return render_template('502.html'), 502

@app.errorhandler(504)
def gateway_timeout(e):
    return render_template('504.html'), 504

if __name__ == '__main__':
    app.run(debug=True)
