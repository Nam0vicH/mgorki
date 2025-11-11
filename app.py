from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Получаем абсолютный путь к текущей директории
template_dir = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__,
            template_folder=os.path.join(template_dir, 'templates'),
            static_folder=static_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_museum'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)


# ===================================================================================
# МОДЕЛИ БАЗЫ ДАННЫХ
# ===================================================================================

class DataContent(db.Model):
    """Модель для контента (карточки музеев, выставок, афиши)"""
    __tablename__ = 'data_content'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    img_card = db.Column('img_card', db.String(255))
    title_card = db.Column('title_card', db.String(255))
    short_description_card = db.Column('short_description_card', db.Text)
    main_image = db.Column('main-image', db.String(255))
    main_text = db.Column('main-text', db.Text)
    block_image_1 = db.Column('block-image_1', db.String(255))
    block_text_1 = db.Column('block-text_1', db.Text)
    block_image_2 = db.Column('block-image_2', db.String(255))
    block_text_2 = db.Column('block-text_2', db.Text)
    block_image_3 = db.Column('block-image_3', db.String(255))
    block_text_4 = db.Column('block-text_4', db.Text)

    def __repr__(self):
        return f'<DataContent {self.title_card}>'


class Event(db.Model):
    """Модель для мероприятий (конкретные сеансы)"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    content_card_id = db.Column(db.Integer, db.ForeignKey('data_content.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    event_datetime = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=20)

    def __repr__(self):
        return f'<Event {self.title}>'


class TicketPrice(db.Model):
    """Модель для цен на билеты"""
    __tablename__ = 'ticket_prices'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    category_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<TicketPrice {self.category_name}: {self.price}>'


class TicketCategory(db.Model):
    """Модель для категорий билетов"""
    __tablename__ = 'ticket_categories'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Enum('museum', 'poster', name='category_enum'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer)
    pushkin_card_allowed = db.Column(db.Boolean, default=False)
    age_restriction = db.Column(db.String(100))
    student_discount = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(50))

    def __repr__(self):
        return f'<TicketCategory {self.title}: {self.price}>'


class SessionSchedule(db.Model):
    """Модель для расписания сеансов"""
    __tablename__ = 'session_schedule'

    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.Enum('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС', name='day_of_week_enum'), nullable=False)
    total_tickets = db.Column(db.Integer, default=50)
    available_tickets = db.Column(db.Integer, default=50)
    reserved_tickets = db.Column(db.Integer, default=0)
    sold_tickets = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    session_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<SessionSchedule {self.session_date} {self.session_time}>'


class Order(db.Model):
    """Модель для заказов"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    country_code = db.Column(db.String(5), default='+7')
    subscribe_news = db.Column(db.Boolean, default=False)
    accept_terms = db.Column(db.Boolean, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('ticket_bookings.id'))
    order_number = db.Column(db.String(50), nullable=False, unique=True)
    order_status = db.Column(db.Enum('new', 'awaiting_payment', 'paid', 'completed', 'cancelled', name='order_status_enum'), default='new')
    qr_code_token = db.Column(db.String(100), unique=True)
    qr_code_url = db.Column(db.String(255))
    ticket_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.String(100))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.Enum('unpaid', 'paid', 'refunded', name='payment_status_enum'), default='unpaid')
    payment_method = db.Column(db.Enum('bank_card', 'pushkin_card', 'cash', name='payment_method_enum'))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    paid_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Order {self.order_number}>'


class TicketBooking(db.Model):
    """Модель для бронирования билетов"""
    __tablename__ = 'ticket_bookings'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session_schedule.id'))
    ticket_category_id = db.Column(db.Integer, db.ForeignKey('ticket_categories.id'))
    user_email = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<TicketBooking {self.id}>'


class Ticket(db.Model):
    """Модель для уникальных билетов (для QR-кодов)"""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('ticket_prices.id'), nullable=False)
    ticket_guid = db.Column(db.String(36), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False, default='valid')

    def __repr__(self):
        return f'<Ticket {self.ticket_guid}>'


# ===================================================================================
# МАРШРУТЫ
# ===================================================================================

@app.route('/')
def homepage():
    """Главная страница с карточками из БД"""
    # Получаем карточки музеев
    museums = DataContent.query.filter_by(category='museums').all()

    # Получаем карточки виртуальных выставок
    virtual_exhibitions = DataContent.query.filter_by(category='virtual_exhibitions').all()

    # Получаем карточки афиши
    posters = DataContent.query.filter_by(category='poster').all()

    return render_template('homepage.html',
                         museums=museums,
                         virtual_exhibitions=virtual_exhibitions,
                         events=posters)

@app.route('/about-us')
@app.route('/about-us/<int:museum_id>')
def about_us(museum_id=None):
    # Если ID не указан, берем первый музей из категории 'museums'
    if museum_id is None:
        museum = DataContent.query.filter_by(category='museums').first()
    else:
        museum = DataContent.query.get_or_404(museum_id)

    return render_template('about_us.html', museum=museum)

@app.route('/order')
@app.route('/order/<int:museum_id>')
def order(museum_id=None):
    """Страница заказа билетов"""
    from datetime import datetime, timedelta

    # Если ID не указан, берем первый музей
    if museum_id is None:
        museum = DataContent.query.filter_by(category='museums').first()
    else:
        museum = DataContent.query.get_or_404(museum_id)

    # Получаем активные сеансы на ближайшие 7 дней
    today = datetime.now().date()
    week_later = today + timedelta(days=7)

    sessions = SessionSchedule.query.filter(
        SessionSchedule.is_active == True,
        SessionSchedule.session_date >= today,
        SessionSchedule.session_date <= week_later
    ).order_by(SessionSchedule.session_date, SessionSchedule.session_time).all()

    # Получаем категории билетов
    ticket_categories = TicketCategory.query.all()

    return render_template('order.html',
                         museum=museum,
                         sessions=sessions,
                         ticket_categories=ticket_categories,
                         today=today)


@app.route('/create-order', methods=['POST'])
def create_order():
    """Создание заказа"""
    from datetime import datetime
    import json
    import secrets

    try:
        # Получаем данные из формы
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        country_code = request.form.get('country_code', '+7')
        subscribe_news = request.form.get('subscribe_news') == 'on'
        accept_terms = request.form.get('accept_terms') == 'on'

        session_date = request.form.get('session_date')
        session_time = request.form.get('session_time')
        tickets_data = json.loads(request.form.get('tickets_data', '{}'))

        # Проверка обязательных полей
        if not all([full_name, email, phone, session_date, session_time, accept_terms]):
            return jsonify({'success': False, 'error': 'Заполните все обязательные поля'})

        if not tickets_data or sum(tickets_data.values()) == 0:
            return jsonify({'success': False, 'error': 'Выберите хотя бы один билет'})

        # Находим сеанс
        session = SessionSchedule.query.filter_by(
            session_date=session_date,
            session_time=session_time
        ).first()

        if not session:
            return jsonify({'success': False, 'error': 'Сеанс не найден'})

        # Проверяем доступность билетов
        total_tickets = sum(int(qty) for qty in tickets_data.values())
        if session.available_tickets < total_tickets:
            return jsonify({'success': False, 'error': 'Недостаточно доступных билетов'})

        # Рассчитываем общую сумму
        total_amount = 0
        for category_id, quantity in tickets_data.items():
            category = TicketCategory.query.get(int(category_id))
            if category:
                total_amount += float(category.price) * int(quantity)

        # Создаем бронирование билета
        booking = TicketBooking(
            session_id=session.id,
            user_email=email
        )
        db.session.add(booking)
        db.session.flush()  # Получаем ID бронирования

        # Генерируем номер заказа и QR-токен
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        qr_token = secrets.token_urlsafe(32)

        # Создаем заказ
        new_order = Order(
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,
            subscribe_news=subscribe_news,
            accept_terms=accept_terms,
            booking_id=booking.id,
            order_number=order_number,
            order_status='new',
            qr_code_token=qr_token,
            qr_code_url=f"/qr/{qr_token}",
            total_amount=total_amount,
            payment_status='unpaid'
        )

        db.session.add(new_order)

        # Обновляем количество доступных билетов
        session.available_tickets -= total_tickets
        session.reserved_tickets += total_tickets

        db.session.commit()

        return jsonify({
            'success': True,
            'order_id': new_order.id,
            'order_number': order_number,
            'total_amount': float(total_amount)
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/virtual-exhibition')
def virtual_exhibition():
    return render_template('virtual-exhi.html')

@app.route('/poster')
def poster():
    return render_template('Poster.html')


# ===================================================================================
# ВСПОМОГАТЕЛЬНЫЕ МАРШРУТЫ ДЛЯ ТЕСТИРОВАНИЯ
# ===================================================================================

@app.route('/test-db')
def test_db():
    """Тестирование подключения к БД"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return "✅ Подключение к базе данных db_museum успешно!"
    except Exception as e:
        return f"❌ Ошибка подключения: {str(e)}"


@app.route('/show-tables')
def show_tables():
    """Показать все таблицы в БД"""
    try:
        result = db.session.execute(db.text('SHOW TABLES'))
        tables = [row[0] for row in result]
        return f"<h2>Таблицы в db_museum:</h2><ul>{''.join([f'<li>{t}</li>' for t in tables])}</ul>"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


@app.route('/show-sessions')
def show_sessions():
    """Тестовый маршрут для проверки сеансов"""
    sessions = SessionSchedule.query.all()
    result = '<h1>Данные из таблицы session_schedule:</h1>'
    for session in sessions:
        result += f'<p><strong>ID:</strong> {session.id}, <strong>Date:</strong> {session.session_date}, <strong>Time:</strong> {session.session_time}, <strong>Available:</strong> {session.available_tickets}/{session.total_tickets}</p>'
    return result


@app.route('/show-categories')
def show_categories():
    """Тестовый маршрут для проверки категорий билетов"""
    categories = TicketCategory.query.all()
    result = '<h1>Данные из таблицы ticket_categories:</h1>'
    for cat in categories:
        result += f'<p><strong>ID:</strong> {cat.id}, <strong>Title:</strong> {cat.title}, <strong>Price:</strong> {cat.price} ₽, <strong>Pushkin:</strong> {cat.pushkin_card_allowed}</p>'
    return result


@app.route('/show-columns')
def show_columns():
    """Показать структуру таблицы data_content"""
    try:
        result = db.session.execute(db.text('DESCRIBE data_content'))
        columns = [(row[0], row[1], row[2], row[3]) for row in result]
        html = "<h2>Структура таблицы data_content:</h2><table border='1' style='border-collapse: collapse;'>"
        html += "<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th></tr>"
        for col in columns:
            html += f"<tr><td>{col[0]}</td><td>{col[1]}</td><td>{col[2]}</td><td>{col[3]}</td></tr>"
        html += "</table>"
        return html
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


@app.route('/show-content')
def show_content():
    """Показать весь контент из data_content"""
    try:
        museums = DataContent.query.filter_by(category='museums').all()
        exhibitions = DataContent.query.filter_by(category='virtual_exhibitions').all()
        posters = DataContent.query.filter_by(category='poster').all()

        html = "<h1>Контент из БД</h1>"

        html += "<h2>Музеи:</h2><ul>"
        for m in museums:
            html += f"<li><strong>{m.title_card}</strong> - {m.short_description_card}<br>Изображение: {m.img_card}</li>"
        html += "</ul>"

        html += "<h2>Виртуальные выставки:</h2><ul>"
        for e in exhibitions:
            html += f"<li><strong>{e.title_card}</strong> - {e.img_card}</li>"
        html += "</ul>"

        html += "<h2>Афиша:</h2><ul>"
        for p in posters:
            html += f"<li><strong>{p.title_card}</strong> - {p.img_card}</li>"
        html += "</ul>"

        return html
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
