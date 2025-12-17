from datetime import datetime
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# === Конфігурація додатку ===
app = Flask(__name__)
app.secret_key = 'labhealth2025-secret-key-1234567890'

# SQLite + SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    appointments = db.relationship(
        'Appointment', backref='user', lazy=True, cascade="all, delete-orphan")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(200), nullable=False)
    doctor = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(100), default="Очікує підтвердження")
    result_text = db.Column(db.Text, nullable=True)
    result_date = db.Column(db.String(50), nullable=True)
    result_ready = db.Column(db.Boolean, default=False)
    pdf_link = db.Column(db.String(300), nullable=True)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.String(50), default=datetime.now().strftime("%d.%m.%Y %H:%M"))


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(200))
    photo = db.Column(db.String(300))
    experience = db.Column(db.String(50))
    education = db.Column(db.String(200))
    bio = db.Column(db.Text)


# Створюємо таблиці
with app.app_context():
    db.create_all()

    # Додаємо лікарів у БД, якщо їх ще немає
    doctors_list = [
        {'slug': 'olena-koval', 'name': 'Олена Коваль', 'position': 'Головний лікар, к.м.н.',
         'photo': 'https://isida.ua/media/cache/e9/59/e9591ec40d1b9ece185c66fb524e8785.jpg',
         'experience': '12 років', 'education': 'НМУ ім. О.О. Богомольця',
         'bio': 'Спеціалізується на клінічній біохімії та імунології. Автор 12 наукових публікацій.'},
        {'slug': 'andriy-melnyk', 'name': 'Андрій Мельник', 'position': 'Лікар-лаборант вищої категорії',
         'photo': 'https://mister-blister.com/wp-content/uploads/2023/11/shutterstock_2281024823.jpg',
         'experience': '11 років', 'education': 'Львівський національний медичний університет',
         'bio': 'Експерт з гематологічних та коагуляційних досліджень.'},
        {'slug': 'mariya-martynyuk', 'name': 'Марія Мартинюк', 'position': 'Старша медична сестра',
         'photo': 'https://isida.ua/media/cache/a5/e4/a5e45e1d24391698fe8f9da17a6831d2.jpg',
         'experience': '10 років', 'education': 'Київський медичний коледж',
         'bio': 'Відповідає за якість забору біоматеріалу та комфорт пацієнтів.'},
        {'slug': 'serhiy-petrenko', 'name': 'Сергій Петренко', 'position': 'Завідувач ПЛР-лабораторії',
         'photo': 'https://innovacia.com.ua/wp-content/uploads/2021/08/Omelchenko-Andrey-Yuryevich.jpg',
         'experience': '11 років', 'education': 'КПІ, біомедична інженерія',
         'bio': 'Експерт з молекулярної діагностики та ПЛР-тестування.'},
        {'slug': 'nataliya-shevchenko', 'name': 'Наталія Шевченко', 'position': 'Лікар-гематолог',
         'photo': 'https://hochu.ua/static/content/thumbs/780x468/0/98/ppsp5r---c2500x1500x0sx0s--ec58ae1a08ea10f37a3d758526e50980.jpg',
         'experience': '7 років', 'education': 'НМУ ім. О.О. Богомольця',
         'bio': 'Спеціалізується на діагностиці анемій та лейкозів.'},
        {'slug': 'dmytro-lytvyn', 'name': 'Дмитро Литвин', 'position': 'Біохімік, к.б.н.',
         'photo': 'https://drmarts.com.ua/wp-content/uploads/2022/10/Martsynkevych-Oleksandr-Viktorovych.jpg',
         'experience': '10 років', 'education': 'Київський національний університет',
         'bio': 'Розробник нових методик біохімічного аналізу.'},
        {'slug': 'tetyana-myronenko', 'name': 'Тетяна Мироненко', 'position': 'Лікар-окуліст',
         'photo': 'https://rplus.com.ua/content/doctors/item_659_sm.jpg',
         'experience': '7 років', 'education': 'НМУ ім. О.О. Богомольця',
         'bio': 'Спеціалізується на офтальмологічній діагностиці.'},
        {'slug': 'myron-telenyuk', 'name': 'Мирон Теленюк', 'position': 'Лікар-хірург',
         'photo': 'https://daily-med.com.ua/wp-content/uploads/2021/09/hirurg.jpg',
         'experience': '9 років', 'education': 'НМУ ім. О.О. Богомольця',
         'bio': 'Провідний спеціаліст з малоінвазивної хірургії.'}
    ]

    for d in doctors_list:
        if not Doctor.query.filter_by(slug=d['slug']).first():
            doc = Doctor(**d)
            db.session.add(doc)
    db.session.commit()


# =============== СТОРІНКИ ЛІКАРІВ ===============
@app.route('/doctor/<doctor_slug>')
def doctor_page(doctor_slug):
    doctor = Doctor.query.filter_by(slug=doctor_slug).first()
    if not doctor:
        return "Лікар не знайдений", 404
    return render_template('doctor.html', doctor=doctor)


# Створюємо таблиці
with app.app_context():
    db.create_all()


# =================== СТАТИЧНІ СТОРІНКИ ===================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success_message = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message_text = request.form.get('message', '').strip()

        if name and email and message_text:
            msg = ContactMessage(
                name=name,
                email=email,
                message=message_text
            )
            db.session.add(msg)
            db.session.commit()

            success_message = f"Дякуємо, {name}! Ваше повідомлення надіслано."

    return render_template('contact.html', success_message=success_message)


# ================= AUTH =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Всі поля обов\'язкові', 'danger')
            return redirect('/register')

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Такий email вже є!', 'danger')
            return redirect('/register')

        user = User(name=name, email=email,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        flash('Реєстрація успішна! Тепер увійдіть', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['user_id'] = user.id
            flash(f'Вітаємо, {user.name}!', 'success')
            return redirect('/')
        else:
            flash('Невірний email або пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Ви вийшли', 'info')
    return redirect('/')


# ================= PROFILE =================
@app.route('/profile')
def profile():
    if 'user_email' not in session:
        flash('Спочатку увійдіть', 'warning')
        return redirect('/login')

    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        flash('Користувача не знайдено', 'danger')
        session.clear()
        return redirect('/login')

    appointments = Appointment.query.filter_by(
        user_id=user.id).order_by(Appointment.id.desc()).all()
    messages = ContactMessage.query.filter_by(
        email=session['user_email']).order_by(ContactMessage.id.desc()).all()

    return render_template('profile.html', user=user, appointments=appointments, messages=messages)


# ================= APPOINTMENT =================
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user_email' not in session:
        flash('Увійдіть в кабінет, щоб записатися', 'warning')
        return redirect('/login')

    services_list = [
        "Загальний аналіз крові", "Біохімічні аналізи",
        "Гормональні аналізи", "Аналізи на інфекції",
        "ПЛР-тестування", "Аналізи для вагітних"
    ]
    doctors = [
        "Др. Мельник", "Др. Мартинюк", "Др. Шевченко",
        "Др. Коваль", "Др. Литвин", "Др. Петренко",
        "Др. Теленюк", "Др. Мироненко"
    ]

    selected_service = request.args.get("service", "")

    if request.method == 'POST':
        service = request.form.get('service')
        doctor = request.form.get('doctor')
        date = request.form.get('date')
        time = request.form.get('time')

        user = User.query.filter_by(email=session['user_email']).first()
        if not user:
            flash('Користувача не знайдено', 'danger')
            return redirect('/login')

        apt = Appointment(
            user_id=user.id,
            service=service,
            doctor=doctor,
            date=date,
            time=time,
            status='Очікує підтвердження',
            result_ready=False
        )
        db.session.add(apt)
        db.session.commit()

        flash(
            f'Дякуємо, {user.name}! Ви записані на «{service}» до {doctor} — {date} о {time}', 'success')
        return redirect('/profile')

    return render_template(
        'appointment.html',
        services=services_list,
        doctors=doctors,
        selected_service=selected_service
    )


# ================= Cancel appointment =================
@app.route('/cancel_appointment/<int:index>')
def cancel_appointment(index):
    if 'user_email' not in session:
        flash('Увійдіть в кабінет', 'warning')
        return redirect('/login')

    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        flash('Користувача не знайдено', 'danger')
        return redirect('/login')

    all_apts = Appointment.query.filter_by(
        user_id=user.id).order_by(Appointment.id.desc()).all()
    if 0 <= index < len(all_apts):
        apt = all_apts[index]
        db.session.delete(apt)
        db.session.commit()
        flash(f'Запис на «{apt.service}» скасовано', 'info')
    else:
        flash('Запис не знайдено', 'danger')

    return redirect('/profile')


# ================= РЕЗУЛЬТАТИ АНАЛІЗІВ =================
@app.route('/_generate_results')
def generate_results():
    if 'user_email' not in session:
        return "no"

    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        return "no"

    apt = Appointment.query.filter_by(
        user_id=user.id).order_by(Appointment.id.desc()).first()
    if not apt:
        return "no appointments"

    apt.status = 'Готово'
    apt.result_ready = True
    apt.result_date = datetime.now().strftime("%d.%m.%Y")
    apt.pdf_link = f"/static/results/{user.email.split('@')[0]}_{random.randint(1000,9999)}.pdf"
    apt.result_text = apt.result_text or "Усі показники в нормі\n(згенеровано автоматично)"
    db.session.commit()

    flash('Новий результат аналізів готовий!', 'success')
    return redirect('/profile')


@app.route('/view_result/<int:index>')
def view_result(index):
    if 'user_email' not in session:
        flash('Спочатку увійдіть', 'warning')
        return redirect('/login')

    user = User.query.filter_by(email=session['user_email']).first()
    if not user:
        flash('Користувача не знайдено', 'danger')
        return redirect('/login')

    appts = Appointment.query.filter_by(
        user_id=user.id).order_by(Appointment.id.desc()).all()
    try:
        apt = appts[index]
    except IndexError:
        flash('Результат не знайдено', 'danger')
        return redirect('/profile')

    if apt.status != 'Готово':
        flash('Результат ще не готовий', 'warning')
        return redirect('/profile')

    result_text_html = (
        apt.result_text or "Результат відсутній").replace("\n", "<br>")

    return f'''
    <div style="max-width:900px;margin:100px auto;padding:60px;background:#1a1a1a;border-radius:32px;text-align:center;color:#eee;">
        <h1 style="color:#00eaff;font-size:3em;margin-bottom:30px;">Результат аналізу</h1>
        <div style="background:white;color:black;padding:50px;border-radius:20px;">
            <h2>LabHealth — Результати</h2>
            <p><strong>Пацієнт:</strong> {user.name}</p>
            <p><strong>Аналіз:</strong> {apt.service}</p>
            <p><strong>Дата здачі:</strong> {apt.date} о {apt.time}</p>
            <p><strong>Дата результату:</strong> {apt.result_date or '—'}</p>
            <hr style="margin:30px 0;">
            <div style="text-align:left;font-size:1.3em;line-height:1.8;">
                {result_text_html}
            </div>
        </div>
        <a href="/profile" style="margin-top:40px;display:inline-block;padding:18px 60px;background:#00ffaa;color:#121212;border-radius:60px;text-decoration:none;font-size:1.4em;">
            ← Назад до кабінету
        </a>
    </div>
    '''

# ================= ADMIN PANEL =================


@app.route('/admin')
def admin_panel():
    if session.get('is_admin') != True:
        if request.args.get('password') == '2301':
            session['is_admin'] = True
        else:
            return '''
            <div style="max-width:500px;margin:150px auto;padding:60px;background:#1a1a1a;border-radius:32px;text-align:center;color:#eee;">
                <h2 style="color:#00eaff;font-size:2.5em;">Адмін-панель</h2>
                <form>
                    <input type="password" name="password" placeholder="Пароль" style="width:100%;padding:18px;margin:20px 0;border-radius:16px;background:#2c2c2c;color:#eee;border:none;font-size:1.2em;"><br>
                    <button type="submit" style="padding:18px 60px;background:#00ffaa;color:#121212;border:none;border-radius:60px;font-size:1.4em;font-weight:700;">Увійти</button>
                </form>
            </div>
            '''

    all_appointments = []
    appts = Appointment.query.order_by(Appointment.id.desc()).all()
    for apt in appts:
        u = User.query.get(apt.user_id)
        all_appointments.append({
            'email': u.email,
            'name': u.name,
            'apt_id': apt.id,
            'apt': apt
        })

    messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
    return render_template('admin.html', appointments=all_appointments, messages=messages)


@app.route('/admin/reply/<int:msg_id>', methods=['POST'])
def admin_reply(msg_id):
    if session.get('is_admin') != True:
        return redirect('/admin')

    msg = ContactMessage.query.get(msg_id)
    if not msg:
        flash("Повідомлення не знайдено", "danger")
        return redirect('/admin')

    reply_text = request.form.get('reply', '').strip()
    if reply_text:
        msg.reply = reply_text
        db.session.commit()
        flash("Відповідь надіслано!", "success")
    else:
        flash("Поле відповіді пусте", "danger")

    return redirect('/admin')


@app.route('/admin/confirm/<int:apt_id>', methods=['POST'])
def admin_confirm(apt_id):
    if session.get('is_admin') != True:
        return redirect('/admin')

    apt = Appointment.query.get(apt_id)
    if not apt:
        flash('Запис не знайдено', 'danger')
        return redirect('/admin')

    result_text = request.form.get('result_text', '').strip()
    if result_text:
        apt.status = 'Готово'
        apt.result_text = result_text
        apt.result_date = datetime.now().strftime("%d.%m.%Y")
        apt.result_ready = True
        db.session.commit()
        flash(
            f'Результат для користувача (id={apt.user_id}) успішно збережено!', 'success')
    else:
        flash('Результат не може бути порожнім', 'danger')

    return redirect('/admin')


# ================= Запуск сервера =================
if __name__ == '__main__':
    app.run(debug=True)
