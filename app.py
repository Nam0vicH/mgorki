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


class Order(db.Model):
    """Модель для заказов"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='paid')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Order {self.customer_name}>'


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
def order():
    return render_template('order.html')

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
