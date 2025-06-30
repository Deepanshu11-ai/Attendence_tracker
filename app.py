from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret123'  # use env variable in production

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------- Models --------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    subjects = db.relationship('Subject', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attendances = db.relationship('Attendance', backref='subject', lazy=True, cascade="all, delete-orphan")
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade="all, delete-orphan")

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topic_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)

# -------------------- Auth --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------- Routes --------------------
@app.route('/')
@login_required
def index():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', subjects=subjects)

@app.route('/add-subject', methods=['POST'])
@login_required
def add_subject():
    name = request.form['subject_name'].strip()
    if name:
        new_subject = Subject(name=name, user_id=current_user.id)
        db.session.add(new_subject)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/subject/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        return "Unauthorized", 403
    total = len(subject.attendances)
    present = len([a for a in subject.attendances if a.status.lower() == 'present'])
    percent = round((present / total * 100), 2) if total > 0 else 0
    return render_template('subject.html', subject=subject, total=total, present=present, percent=percent)

@app.route('/subject/<int:subject_id>/mark', methods=['POST'])
@login_required
def mark_attendance(subject_id):
    status = request.form['status']
    today = date.today()
    existing = Attendance.query.filter_by(subject_id=subject_id, date=today).first()
    if not existing:
        new_attendance = Attendance(subject_id=subject_id, status=status)
        db.session.add(new_attendance)
        db.session.commit()
    return redirect(url_for('subject_detail', subject_id=subject_id))

@app.route('/subject/<int:subject_id>/add-topic', methods=['POST'])
@login_required
def add_topic(subject_id):
    topic_name = request.form['topic_name']
    topic_date_str = request.form['topic_date']
    try:
        topic_date = datetime.strptime(topic_date_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format", 400
    new_topic = Topic(subject_id=subject_id, topic_name=topic_name, date=topic_date)
    db.session.add(new_topic)
    db.session.commit()
    return redirect(url_for('subject_detail', subject_id=subject_id))

@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete-attendance/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    if attendance.subject.user_id != current_user.id:
        return "Unauthorized", 403
    subject_id = attendance.subject_id
    db.session.delete(attendance)
    db.session.commit()
    return redirect(url_for('subject_detail', subject_id=subject_id))

# -------------------- Main --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
