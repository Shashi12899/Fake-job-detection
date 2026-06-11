import os
import sys
import json

# Add parent directory to path so it can find app and backend
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from app import app, db
from backend.models import User, ScanHistory, CommunityReport

USERS_FILE = 'users.json'
HISTORY_FILE = 'scans_history.json'
REPORTS_FILE = 'community_reports.json'

def migrate_users():
    if not os.path.exists(USERS_FILE):
        print(f"No {USERS_FILE} found. Skipping users.")
        return
        
    with open(USERS_FILE, 'r') as f:
        try:
            users_data = json.load(f)
        except json.JSONDecodeError:
            print("Failed to decode users.json")
            return
            
    for email, data in users_data.items():
        # Check if already exists
        if User.query.filter_by(email=email).first():
            print(f"User {email} already exists. Skipping.")
            continue
            
        user = User(
            name=data.get('name', 'Operator'),
            email=email,
            password_hash=data.get('password', ''),
            rank=data.get('rank', 'SECURITY ANALYST'),
            created_at=data.get('created_at', '2026-01-01 00:00:00')
        )
        db.session.add(user)
    
    db.session.commit()
    print("Users migrated successfully.")

def migrate_history():
    if not os.path.exists(HISTORY_FILE):
        print(f"No {HISTORY_FILE} found. Skipping history.")
        return
        
    with open(HISTORY_FILE, 'r') as f:
        try:
            history_data = json.load(f)
        except json.JSONDecodeError:
            print("Failed to decode scans_history.json")
            return
            
    for item in history_data:
        history = ScanHistory(
            timestamp=item.get('timestamp', ''),
            operator=item.get('operator', 'anonymous'),
            input_data=json.dumps(item.get('input', {})),
            result=item.get('result', ''),
            risk_score=item.get('risk_score', 0.0),
            reasons=json.dumps(item.get('reasons', []))
        )
        db.session.add(history)
        
    db.session.commit()
    print("History migrated successfully.")

def migrate_reports():
    if not os.path.exists(REPORTS_FILE):
        print(f"No {REPORTS_FILE} found. Skipping community reports.")
        return
        
    with open(REPORTS_FILE, 'r') as f:
        try:
            reports_data = json.load(f)
        except json.JSONDecodeError:
            print("Failed to decode community_reports.json")
            return
            
    for item in reports_data:
        report = CommunityReport(
            timestamp=item.get('timestamp', ''),
            company=item.get('company', ''),
            reason=item.get('reason', '')
        )
        db.session.add(report)
        
    db.session.commit()
    print("Community reports migrated successfully.")

if __name__ == '__main__':
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        print("Migrating users...")
        migrate_users()
        
        print("Migrating history...")
        migrate_history()
        
        print("Migrating community reports...")
        migrate_reports()
        
        print("Migration complete!")
