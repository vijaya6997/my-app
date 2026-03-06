from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    skills = db.Column(db.String(200))
    profile_pic = db.Column(db.String(100), default='default.jpg')
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), default='seller') # buyer, seller
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notifications = db.relationship('Notification', backref='user', lazy=True)

    applications = db.relationship('Application', backref='applicant', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='open') # open, in_progress, completed, closed
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attachment_path = db.Column(db.String(200)) # New: for job poster attachments
    submission_body = db.Column(db.Text) # New: worker's work submission
    submission_attachment = db.Column(db.String(200)) # New: worker's file submission
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy=True)
    reviews = db.relationship('Review', backref='job', lazy=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    poster = db.relationship('User', foreign_keys=[poster_id], backref='jobs_posted', lazy=True)
    worker = db.relationship('User', foreign_keys=[worker_id], backref='tasks_assigned', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected
    attachment_path = db.Column(db.String(200)) # New: for file attachments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(200)) # New: for file attachments
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(100))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'credit', 'debit'
    description = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
