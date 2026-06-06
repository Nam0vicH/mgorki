# 🏛️ mgorki - Музейная платформа электронного билетирования

**Современная веб-приложение для управления билетами музеев, виртуальных выставок и афиш событий.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Nam0vicH/mgorki/blob/main/LICENSE)
![Language Composition](https://img.shields.io/badge/HTML-56.5%25-informational?style=flat-square&color=e34c26)
![CSS](https://img.shields.io/badge/CSS-27.4%25-informational?style=flat-square&color=563d7c)
![Python](https://img.shields.io/badge/Python-14.3%25-informational?style=flat-square&color=3776ab)
![JavaScript](https://img.shields.io/badge/JavaScript-1.8%25-informational?style=flat-square&color=f7df1e)

---

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Основные возможности](#основные-возможности)
- [Технологический стек](#технологический-стек)
- [Архитектура приложения](#архитектура-приложения)
- [Установка и настройка](#установка-и-настройка)
- [Структура проекта](#структура-проекта)
- [API Маршруты](#api-маршруты)
- [База данных](#база-данных)
- [Администраторская панель](#администраторская-панель)
- [Безопасность](#безопасность)
- [Лицензия](#лицензия)
- [Автор](#автор)

---

## 📝 Описание проекта

**mgorki** — это полнофункциональная платформа для управления билетами музеев. Приложение предоставляет пользователям удобный интерфейс для:

- 👁️ Просмотра информации о музеях и выставках
- 🎫 Бронирования и покупки билетов онлайн
- 💳 Оплаты через различные способы оплаты
- 🎟️ Получения цифровых билетов с QR-кодами

А также комплексную администраторскую панель для:

- 📊 Управления контентом (музеи, выставки, афиша)
- 📅 Управления расписанием сеансов
- 💰 Управления категориями и ценами билетов
- 📈 Отслеживания заказов и платежей

---

## ✨ Основные возможности

### Для посетителей (Public)

- ✅ **Главная страница** — Каталог музеев, виртуальных выставок и событий
- ✅ **О музеях** — Подробная информация о каждом музее
- ✅ **Заказ билетов** — Интуитивный интерфейс для выбора и бронирования билетов
- ✅ **Расписание сеансов** — Автоматическое управление расписанием на 7 дней вперед
- ✅ **Оплата билетов** — Поддержка различных способов платежа
- ✅ **QR-коды** — Генерация и верификация цифровых билетов
- ✅ **Подписка на новости** — Система подписки пользователей
- ✅ **Информация о программах** — Детальное описание музейных программ

### Для администраторов (Admin Panel)

- ✅ **Управление контентом** — Добавление, редактирование, удаление музеев, выставок, афиш
- ✅ **Загрузка изображений** — Поддержка загрузки картинок для всех типов контента
- ✅ **Управление билетами** — Создание категорий билетов и установка цен
- ✅ **Расписание сеансов** — Просмотр и управление расписанием на неделю
- ✅ **История заказов** — Полный журнал всех выполненных заказов
- ✅ **Статистика** — Дашборд с основными метриками
- ✅ **Защита паролем** — Безопасный вход в администраторскую панель

---

## 🛠️ Технологический стек

### Backend

- **Python 3.x** — Язык программирования
- **Flask** — Микрофреймворк для веб-приложений
- **MySQL** — Система управления базами данных
- **mysql-connector-python** — Драйвер для подключения к MySQL

### Frontend

- **HTML5** — Структура веб-страниц (56.5%)
- **CSS3** — Стилизация интерфейса (27.4%)
- **JavaScript** — Интерактивность (1.8%)
- **Jinja2** — Шаблонизатор для Python

### Дополнительные библиотеки

- **Werkzeug** — Утилиты для работы с HTTP
- **MarkupSafe** — Защита от XSS атак
- **Click** — Интерфейс командной строки
- **Colorama** — Цветной вывод в консоль

---

## 🏗️ Архитектура приложения

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (HTML/CSS/JS)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Flask Application                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │             Routing & View Controllers                 │ │
│  │  (app.py - 491 lines)                                  │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Public Routes (/, /about-us, /order, etc.)          │ │
│  │  • Payment Routes (/payment, /process-payment)         │ │
│  │  • Admin Routes (/admin/*, protected)                  │ │
│  │  • Testing Routes (/test-db, /show-tables, etc.)       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────���──────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               Database Layer (database.py)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Connection Management                               │ │
│  │  • Query Execution                                     │ │
│  │  • ORM-like Functions                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   MySQL Database                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Tables:                                               │ │
│  │  • data_content (музеи, выставки, афиша)               │ │
│  │  • ticket_categories (категории билетов)               │ │
│  │  • session_schedule (расписание сеансов)               │ │
│  │  • ticket_bookings (бронирования)                      │ │
│  │  • orders (заказы и платежи)                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Установка и настройка

### Предварительные требования

- Python 3.7+
- MySQL 5.7+ или MySQL 8.0+
- pip (менеджер пакетов Python)
- Git

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Nam0vicH/mgorki.git
cd mgorki
```

### Шаг 2: Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка базы данных

#### Создание базы данных MySQL

```sql
CREATE DATABASE db_museum CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_museum;

-- Таблица контента (музеи, выставки, афиша)
CREATE TABLE data_content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    title_card VARCHAR(255) NOT NULL,
    short_description_card TEXT,
    img_card VARCHAR(255),
    date_of_the_event DATE,
    location_of_the_event VARCHAR(255),
    main_image VARCHAR(255),
    main_text TEXT,
    block_image_1 VARCHAR(255),
    block_text_1 TEXT,
    block_image_2 VARCHAR(255),
    block_text_2 TEXT,
    block_image_3 VARCHAR(255),
    block_text_3 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Таблица категорий билетов
CREATE TABLE ticket_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    pushkin_card_allowed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Таблица расписания сеансов
CREATE TABLE session_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_date DATE NOT NULL,
    session_time TIME NOT NULL,
    day_of_week VARCHAR(20),
    total_tickets INT DEFAULT 50,
    available_tickets INT DEFAULT 50,
    sold_tickets INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_session (session_date, session_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Таблица бронирований билетов
CREATE TABLE ticket_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    ticket_category_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_phone VARCHAR(20),
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    booking_status VARCHAR(50) DEFAULT 'pending',
    booking_code VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES session_schedule(id),
    FOREIGN KEY (ticket_category_id) REFERENCES ticket_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Таблица заказов
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    country_code VARCHAR(5) DEFAULT '+7',
    booking_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_status VARCHAR(50) DEFAULT 'new',
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    qr_code_token VARCHAR(255) UNIQUE,
    qr_code_url VARCHAR(255),
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES ticket_bookings(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Обновление конфигурации базы данных

Отредактируйте файл `database.py`:

```python
DB_CONFIG = {
    'host': 'localhost',        # Адрес сервера MySQL
    'user': 'root',             # Имя пользователя MySQL
    'password': 'ваш_пароль',   # Пароль MySQL
    'database': 'db_museum',    # Имя базы данных
    'port': 3306                # Порт MySQL
}
```

### Шаг 5: Настройка параметров приложения

Отредактируйте `app.py` и установите безопасный ключ сессии:

```python
app.config['SECRET_KEY'] = 'ваш-безопасный-ключ-здесь'
```

### Шаг 6: Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: **http://localhost:5000**

---

## 📂 Структура проекта

```
mgorki/
├── app.py                      # Основное Flask приложение (491 строк)
├── database.py                 # Слой работы с БД (243 строки)
├── requirements.txt            # Зависимости Python
├── LICENSE                     # MIT License
├── .gitignore                  # Исключения для Git
├── README.md                   # Этот файл
│
├── static/                     # Статические файлы
│   └── images/
│       ├── museums/            # Изображения музеев
│       ├── virtual/            # Изображения выставок
│       ├── posters/            # Изображения афиш
│       └── uploads/            # Загруженные пользователем файлы
│
└── templates/                  # HTML шаблоны (Jinja2)
    ├── homepage.html           # Главная страница
    ├── about_us.html           # Информация о музеях
    ├── order.html              # Страница заказа билетов
    ├── payment.html            # Страница оплаты
    ├── ticket.html             # Страница билета с QR-кодом
    ├── museum_programs.html    # Программы музеев
    ├── poster.html             # Афиша событий
    ├── about_the_museum.html   # Общая информация о музее
    │
    └── admin/                  # Админ-панель
        ├── login.html          # Форма входа
        ├── content_list.html   # Список контента
        ├── edit_form.html      # Форма редактирования
        └── orders_list.html    # Список заказов
```

---

## 🛣️ API Маршруты

### Открытые маршруты (Public)

| Маршрут                 | Метод | Описание                                       |
|-------------------------|-------|------------------------------------------------|
| `/`                     | GET   | Главная страница с каталогом музеев и выставок |
| `/about-us`             | GET   | Информация о музеях                            |
| `/about-us/<id>`        | GET   | Информация о конкретном музее                  |
| `/order`                | GET   | Страница заказа билетов                        |
| `/order/<id>`           | GET   | Заказ билетов для конкретного музея            |
| `/create-order`         | POST  | Создание нового заказа                         |
| `/payment/<id>`         | GET   | Страница оплаты заказа                         |
| `/process-payment/<id>` | POST  | Обработка оплаты                               |
| `/ticket/<id>`          | GET   | Просмотр билета и QR-��ода                      |
| `/qr/<token>`           | GET   | Верификация QR-кода                            |
| `/museum_programs/<id>` | GET   | Программы музея                                |
| `/poster`               | GET   | Афиша событий                                  |
| `/about_the_museum`     | GET   | Общая информация о музее                       |

### Администраторские маршруты (Protected)

| Маршрут                       | Метод     | Описание                     |
|-------------------------------|-----------|------------------------------|
| `/admin/login`                | GET, POST | Вход в админ-панель          |
| `/admin/logout`               | GET       | Выход из админ-панели        |
| `/admin`                      | GET       | Дашборд                      |
| `/admin/content/<category>`   | GET       | Список контента по категории |
| `/admin/edit/<category>/<id>` | GET, POST | Редактирование контента      |
| `/admin/delete/<id>`          | GET       | Удаление контента            |
| `/admin/orders`               | GET       | Список всех заказов          |

### Тестовые маршруты (Test)

| Маршрут            | Метод | Описание                    |
|--------------------|-------|-----------------------------|
| `/test-db`         | GET   | Проверка подключения к БД   |
| `/show-tables`     | GET   | Список таблиц в БД          |
| `/show-sessions`   | GET   | Просмотр расписания сеансов |
| `/show-categories` | GET   | Просмотр категорий билетов  |
| `/show-columns`    | GET   | Структура таблицы контента  |
| `/show-content`    | GET   | Весь контент из БД          |

---

## 💾 База данных

### Описание таблиц

#### 1. **data_content** — Основной контент

| Поле                   | Тип          | Описание                                        |
|------------------------|--------------|-------------------------------------------------|
| id                     | INT          | Уникальный идентификатор                        |
| category               | VARCHAR(50)  | Категория: museums, virtual_exhibitions, poster |
| title_card             | VARCHAR(255) | Название на карточке                            |
| short_description_card | TEXT         | Краткое описание                                |
| img_card               | VARCHAR(255) | Путь к изображению карточки                     |
| date_of_the_event      | DATE         | Дата события (для афиш)                         |
| location_of_the_event  | VARCHAR(255) | Место события                                   |
| main_image             | VARCHAR(255) | Главное изображение                             |
| main_text              | TEXT         | Основной текст                                  |
| block_image_1,2,3      | VARCHAR(255) | Изображения в блоках                            |
| block_text_1,2,3       | TEXT         | Текст в блоках                                  |

#### 2. **ticket_categories** — Категории билетов

| Поле                 | Тип           | Описание                                      |
|----------------------|---------------|-----------------------------------------------|
| id                   | INT           | Уникальный идентификатор                      |
| title                | VARCHAR(100)  | Название категории (Взрослый, Детский и т.д.) |
| description          | TEXT          | Описание                                      |
| price                | DECIMAL(10,2) | Цена билета                                   |
| pushkin_card_allowed | BOOLEAN       | Поддержка Пушкинской карты                    |

#### 3. **session_schedule** — Расписание сеансов

| Поле              | Тип         | Описание                    |
|-------------------|-------------|-----------------------------|
| id                | INT         | Уникальный идентификатор    |
| session_date      | DATE        | Дата сеанса                 |
| session_time      | TIME        | Время сеанса                |
| day_of_week       | VARCHAR(20) | День недели (ПН, ВТ и т.д.) |
| total_tickets     | INT         | Всего билетов               |
| available_tickets | INT         | Доступных билетов           |
| sold_tickets      | INT         | Проданных билетов           |
| is_active         | BOOLEAN     | Активен ли сеанс            |

#### 4. **ticket_bookings** — Бронирования

| Поле               | Тип           | Описание                              |
|--------------------|---------------|---------------------------------------|
| id                 | INT           | Уникальный идентификатор              |
| session_id         | INT           | Ссылка на сеанс                       |
| ticket_category_id | INT           | Ссылка на категорию билета            |
| user_email         | VARCHAR(255)  | Email пользователя                    |
| user_phone         | VARCHAR(20)   | Телефон пользователя                  |
| quantity           | INT           | Количество билетов                    |
| total_price        | DECIMAL(10,2) | Общая стоимость                       |
| payment_method     | VARCHAR(50)   | Способ оплаты                         |
| booking_status     | VARCHAR(50)   | Статус: pending, confirmed, cancelled |
| booking_code       | VARCHAR(50)   | Уникальный код бронирования           |

#### 5. **orders** — Заказы

| Поле           | Тип           | Описание                                      |
|----------------|---------------|-----------------------------------------------|
| id             | INT           | Уникальный идентификатор                      |
| full_name      | VARCHAR(255)  | ФИО заказчика                                 |
| email          | VARCHAR(255)  | Email заказчика                               |
| phone          | VARCHAR(20)   | Телефон заказчика                             |
| country_code   | VARCHAR(5)    | Код страны (по умолчанию +7)                  |
| booking_id     | INT           | Ссылка на бронирование                        |
| order_number   | VARCHAR(50)   | Уникальный номер заказа                       |
| order_status   | VARCHAR(50)   | Статус: new, processing, completed, cancelled |
| payment_status | VARCHAR(50)   | Статус платежа: unpaid, paid, refunded        |
| qr_code_token  | VARCHAR(255)  | Токен для QR-кода                             |
| qr_code_url    | VARCHAR(255)  | URL QR-кода                                   |
| total_amount   | DECIMAL(10,2) | Итоговая сумма                                |
| created_at     | TIMESTAMP     | Время создания                                |
| updated_at     | TIMESTAMP     | Время последнего обновления                   |

---

## 🔐 Администраторская панель

### Вход в админ-панель

Доступ по адресу: **http://localhost:5000/admin/login**

**Учетные данные по умолчанию:**

- Логин: `admin`
- Пароль: `admin`

⚠️ **ВАЖНО:** Измените учетные данные в файле `app.py` перед развертыванием в production!

### Функции админ-панели

1. **Управление контентом**
    - Добавление/редактирование/удаление музеев
    - Добавление/редактирование/удаление виртуальных выставок
    - Добавление/редактирование/удаление афиш событий
    - Загрузка изображений для каждого элемента

2. **История заказов**
    - Просмотр всех выполненных заказов
    - Информация о клиентах и сумме заказа
    - Статусы платежей

3. **Дашборд**
    - Количество музеев в системе
    - Количество заказов
    - Последние заказы

---

## 🔒 Безопасность

### Реализованные меры защиты

1. **Аутентификация**
    - Защита админ-панели требованием входа
    - Использование сессий Flask
    - Проверка прав доступа на каждом защищенном маршруте

2. **Защита от атак**
    - Использование `MarkupSafe` для защиты от XSS
    - Использование `Werkzeug.secure_filename` при загрузке файлов
    - Параметризованные SQL-запросы для защиты от SQL-injection

3. **Безопасность сессий**
    - Секретный ключ для подписания сессий
    - Автоматическая очистка сессии при выходе

### Рекомендации для production

1. **Измените учетные данные администратора**
   ```python
   # app.py
   ADMIN_USER = 'your_secure_username'
   ADMIN_PASS = 'your_secure_password'
   ```

2. **Используйте переменные окружения**
   ```python
   import os
   ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'default')
   ```

3. **Активируйте HTTPS**
    - Используйте SSL/TLS сертификаты
    - Настройте редирект с HTTP на HTTPS

4. **Регулярно обновляйте зависимости**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

5. **Создайте резервные копии БД**
   ```bash
   mysqldump -u root -p db_museum > backup.sql
   ```

---

## 📊 Основные функции по кодам

### app.py (491 строк)

**Ключевые функции:**

- `homepage()` — Главная страница с каталогом
- `about_us()` — Информация о музеях
- `order()` — Страница выбора и бронирования билетов
- `create_order()` — Обработка создания заказа
- `payment()` / `process_payment()` — Обработка платежей
- `ticket()` / `verify_qr()` — Генерация и верификация QR-кодов
- `login()` / `logout()` — Аутентификация админа
- `admin_dashboard()` — Дашборд администратора
- `admin_edit()` — Редактирование контента
- `admin_delete()` — Удаление контента

### database.py (243 строки)

**Ключевые функции:**

- `get_connection()` — Подключение к MySQL
- `execute_query()` — Выполнение SQL запросов
- `get_content_by_category()` — Получение контента по категории
- `get_active_sessions()` — Получение активных сеансов
- `generate_weekly_schedule()` — Автогенерация расписания на неделю
- `create_order()` / `create_booking()` — Создание заказов
- `insert_content()` / `update_content()` / `delete_content()` — CRUD операции

---

## 🚀 Развертывание

### Развертывание на Heroku

1. Установите Heroku CLI
2. Создайте `Procfile`:
   ```
   web: gunicorn app:app
   ```

3. Установите gunicorn:
   ```bash
   pip install gunicorn
   pip freeze > requirements.txt
   ```

4. Разверните:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

### Развертывание на собственном сервере

1. Устан��вите Python и MySQL на сервер
2. Клонируйте репозиторий
3. Настройте окружение
4. Используйте обратный прокси (nginx) и WSGI сервер (Gunicorn/uWSGI)

---

## 🐛 Тестирование

### Проверка подключения к БД

```
http://localhost:5000/test-db
```

### Просмотр таблиц

```
http://localhost:5000/show-tables
```

### Просмотр расписания

```
http://localhost:5000/show-sessions
```

### Просмотр категорий билетов

```
http://localhost:5000/show-categories
```

---

## 📝 Примеры использования API

### Создание заказа (POST /create-order)

```javascript
const formData = new FormData();
formData.append('full_name', 'Иван Петров');
formData.append('email', 'ivan@example.com');
formData.append('phone', '9991234567');
formData.append('session_date', '2024-05-15');
formData.append('session_time', '14:00:00');
formData.append('tickets_data', JSON.stringify({1: 2, 2: 1})); // категория: кол-во
formData.append('accept_terms', 'on');

fetch('/create-order', {
    method: 'POST',
    body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

### Получение активных сеансов

```python
from database import get_active_sessions
from datetime import datetime, timedelta

today = datetime.now().date()
week_later = today + timedelta(days=7)
sessions = get_active_sessions(today, week_later)
```

---

## 📋 Состав языков

| Язык       | Доля  |
|------------|-------|
| HTML       | 56.5% |
| CSS        | 27.4% |
| Python     | 14.3% |
| JavaScript | 1.8%  |

---

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT — см. файл [LICENSE](LICENSE) для подробностей.

---

## 👤 Автор

**Nam0vicH**

- GitHub: [@Nam0vicH](https://github.com/Nam0vicH)
- Repository: [Nam0vicH/mgorki](https://github.com/Nam0vicH/mgorki)

---

## 🤝 Вклад в проект

Внесение вклада в проект приветствуется! Пожалуйста:

1. Создайте fork репозитория
2. Создайте ветку для своей функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте свои изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте раздел [Issues](https://github.com/Nam0vicH/mgorki/issues)
2. Создайте новый issue с описанием проблемы
3. Приложите логи ошибок и информацию о вашей системе

---

## 🔄 История обновлений

- **v1.0.0** (18 декабря 2025) — Первый релиз
    - Основной функционал бронирования билетов
    - Админ-панель управления контентом
    - Система QR-кодов для билетов
    - Автогенерация расписания

---

**Спасибо за использование mgorki! 🏛️**
