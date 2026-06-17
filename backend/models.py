from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

# db is initialized in app.py and imported here

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rank = db.Column(db.String(50), default="SECURITY ANALYST")
    created_at = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    operator = db.Column(db.String(120), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    reasons = db.Column(db.Text, nullable=False)

    def get_input_data(self):
        try:
            return json.loads(self.input_data)
        except:
            return {}

    def get_reasons(self):
        try:
            return json.loads(self.reasons)
        except:
            return []

class CommunityReport(db.Model):
    __tablename__ = 'community_reports'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.Text, nullable=False)
