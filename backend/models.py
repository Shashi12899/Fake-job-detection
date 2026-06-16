from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# db is initialized in app.py and imported here

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    otp_expiration = db.Column(db.DateTime, nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<User {self.email}>"

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(150), nullable=True)
    salary = db.Column(db.String(50), nullable=True)
    prediction = db.Column(db.String(10), nullable=True)  # REAL or FAKE
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('jobs', lazy=True))

    def __repr__(self):
        return f"<Job {self.id} by {self.user_id}>"
