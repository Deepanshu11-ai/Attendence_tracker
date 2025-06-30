# attendance-flask-app/app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    attendances = db.relationship('Attendance', backref='subject', lazy=True)
    topics = db.relationship('Topic', backref='subject', lazy=True)

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

@app.route('/')
def index():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/add-subject', methods=['POST'])
def add_subject():
    name = request.form['subject_name']
    new_subject = Subject(name=name)
    db.session.add(new_subject)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('subject.html', subject=subject)

@app.route('/subject/<int:subject_id>/mark', methods=['POST'])
def mark_attendance(subject_id):
    status = request.form['status']
    new_attendance = Attendance(subject_id=subject_id, status=status)
    db.session.add(new_attendance)
    db.session.commit()
    return redirect(url_for('subject_detail', subject_id=subject_id))

@app.route('/subject/<int:subject_id>/add-topic', methods=['POST'])
def add_topic(subject_id):
    topic_name = request.form['topic_name']
    topic_date = request.form['topic_date']
    new_topic = Topic(subject_id=subject_id, topic_name=topic_name, date=topic_date)
    db.session.add(new_topic)
    db.session.commit()
    return redirect(url_for('subject_detail', subject_id=subject_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)