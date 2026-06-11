from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rank = db.Column(db.String(50), default='SECURITY ANALYST')
    created_at = db.Column(db.String(50), nullable=False)

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    operator = db.Column(db.String(120), nullable=False)
    input_data = db.Column(db.Text, nullable=False) # Store JSON string
    result = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    reasons = db.Column(db.Text, nullable=False) # Store JSON string

    def get_input_data(self):
        return json.loads(self.input_data)

    def get_reasons(self):
        return json.loads(self.reasons)

class CommunityReport(db.Model):
    __tablename__ = 'community_reports'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
