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

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/virtual-exhibition')
def virtual_exhibition():
    return render_template('virtual-exhi.html')

@app.route('/poster')
def poster():
    return render_template('Poster.html')

if __name__ == '__main__':
    app.run(debug=True)
