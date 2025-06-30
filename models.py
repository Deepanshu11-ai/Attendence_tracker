from app import db
from datetime import date

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
