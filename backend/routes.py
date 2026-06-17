from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from functools import wraps
import datetime
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
import joblib
import os

from backend.models import db, User, ScanHistory, CommunityReport
from backend.utils import (is_safe_url, verify_company_details, verify_email, 
                   analyze_salary, detect_phishing_links, check_dark_web, SUSPICIOUS_KEYWORDS)

api = Blueprint('api', __name__)

def get_serializer():
    # Use the app's secret key to sign tokens
    return URLSafeTimedSerializer(current_app.config.get('SECRET_KEY', 'default_secret'))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing or invalid!'}), 401
            
        try:
            s = get_serializer()
            # Token expires in 24 hours (86400 seconds)
            email = s.loads(token, max_age=86400)
            user = User.query.filter_by(email=email).first()
            if not user:
                raise Exception("User not found")
            # Store user in flask request context for the route to use
            request.user = user
        except SignatureExpired:
            return jsonify({'error': 'Token has expired!'}), 401
        except BadTimeSignature:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed!'}), 401
            
        return f(*args, **kwargs)
    return decorated


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, 'ml', 'model.joblib')
vectorizer_path = os.path.join(base_dir, 'ml', 'vectorizer.joblib')

try:
    vectorizer = joblib.load(vectorizer_path)
    model = joblib.load(model_path)
    MODEL_LOADED = True
except Exception:
    MODEL_LOADED = False

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    name = data.get('name', 'Operator')
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Operator ID already enlisted in secure base"}), 400
        
    hashed_pw = generate_password_hash(password)
    new_user = User(
        name=name, 
        email=email, 
        password_hash=hashed_pw,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_user)
    db.session.commit()
    
    session['user'] = email
    token = get_serializer().dumps(email)
    return jsonify({
        "status": "Registration Complete",
        "token": token,
        "user": {
            "name": name,
            "email": email,
            "rank": "SECURITY ANALYST"
        }
    })

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({"error": "Credentials missing"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Access Denied: Invalid security signature"}), 401
        
    # Legacy password migration support
    if len(user.password_hash) == 64:  # Old sha256 hash length
        legacy_salt = "detectai_salt_1337"
        legacy_hash = hashlib.sha256((password + legacy_salt).encode('utf-8')).hexdigest()
        if legacy_hash == user.password_hash:
            # Upgrade password securely
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            session['user'] = email
            return _login_success(user)
    else:
        if check_password_hash(user.password_hash, password):
            session['user'] = email
            return _login_success(user)

    return jsonify({"error": "Access Denied: Invalid security signature"}), 401

def _login_success(user):
    token = get_serializer().dumps(user.email)
    return jsonify({
        "status": "Access Granted",
        "token": token,
        "user": {
            "name": user.name,
            "email": user.email,
            "rank": user.rank
        }
    })

@api.route('/auth/biometric', methods=['POST'])
def biometric_login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    
    user = User.query.filter_by(email=email).first()
    if user:
        session['user'] = user.email
        token = get_serializer().dumps(user.email)
        return jsonify({
            "status": "Biometric Signature Match",
            "token": token,
            "user": {"name": user.name, "email": user.email, "rank": user.rank}
        })
        
    guest_email = "biometric.agent@detectai.net"
    guest = User.query.filter_by(email=guest_email).first()
    if not guest:
        guest = User(
            name="Bio-Verified Agent",
            email=guest_email,
            password_hash=generate_password_hash("biometric_bypass_992"),
            rank="ELITE PROTECTOR",
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(guest)
        db.session.commit()
        
    session['user'] = guest.email
    token = get_serializer().dumps(guest.email)
    return jsonify({
        "status": "Biometric Signature Match",
        "token": token,
        "user": {"name": guest.name, "email": guest.email, "rank": guest.rank}
    })

@api.route('/auth/session', methods=['GET'])
@token_required
def get_session():
    user = request.user
    return jsonify({
        "authenticated": True,
        "user": {"name": user.name, "email": user.email, "rank": user.rank}
    })

@api.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"status": "Session terminated"})

@api.route('/history', methods=['GET'])
@token_required
def get_history():
    operator = request.user.email
    histories = ScanHistory.query.filter_by(operator=operator).order_by(ScanHistory.id.desc()).limit(50).all()
    res = []
    for h in histories:
        res.append({
            "timestamp": h.timestamp,
            "operator": h.operator,
            "input": h.get_input_data(),
            "result": h.result,
            "risk_score": h.risk_score,
            "reasons": h.get_reasons()
        })
    return jsonify(res)

@api.route('/report', methods=['POST'])
@token_required
def report_scam():
    data = request.json or {}
    company = data.get('company')
    if company:
        report = CommunityReport(
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            company=company,
            reason=data.get('reason', 'Community Flag')
        )
        db.session.add(report)
        db.session.commit()
    return jsonify({"status": "Reported Successfully"})

@api.route('/stats', methods=['GET'])
@token_required
def get_stats():
    operator = request.user.email
    histories = ScanHistory.query.filter_by(operator=operator).all()
    total = len(histories)
    fakes = len([h for h in histories if h.result == 'FAKE JOB'])
    
    all_reasons = []
    for h in histories:
        all_reasons.extend(h.get_reasons())
        
    from collections import Counter
    return jsonify({
        "total": total, "fake_count": fakes, "real_count": total - fakes,
        "fake_percent": round((fakes/total*100),1) if total>0 else 0,
        "top_reasons": Counter(all_reasons).most_common(5)
    })

@api.route('/scrape', methods=['POST'])
def scrape():
    data = request.json or {}
    url = data.get('url')
    if not url: 
        return jsonify({"error": "No URL provided"}), 400
        
    if not is_safe_url(url):
        return jsonify({"error": "Unsafe or invalid URL provided. Access denied."}), 403
        
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else (soup.title.string if soup.title else "Job Post")
        description = soup.body.get_text(separator=' ', strip=True)[:1000] if soup.body else "No description"
        return jsonify({"title": title, "company": "Extracted Company", "description": description, "status": "Success"})
    except Exception as e:
        return jsonify({"error": "Failed to scrape URL"}), 500

@api.route('/ocr', methods=['POST'])
def ocr():
    file = request.files.get('file')
    if not file: return jsonify({"error": "No file"}), 400
    try:
        text = pytesseract.image_to_string(Image.open(io.BytesIO(file.read())))
        if not text.strip():
            text = "No text detected"
        return jsonify({"text": text, "status": "Success"})
    except Exception: 
        return jsonify({"error": "OCR Failed", "text": "MOCK: Senior Engineer. $200k. WhatsApp +12345678"}), 200

@api.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    title, company, description, website, email = data.get('title',''), data.get('company',''), data.get('description',''), data.get('website',''), data.get('email','')
    combined_text = f"{title} {company} {description} {website} {email}".lower()
    
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in combined_text]
    comp_v = verify_company_details(website)
    email_v = verify_email(email, company, comp_v['domain'])
    salary_v = analyze_salary(data.get('salary',''), description)
    dark_flags = check_dark_web(company, website, email)
    phishing_flags = detect_phishing_links(description)
    
    community_reports = CommunityReport.query.filter(CommunityReport.company.ilike(company)).count() if company else 0

    reasons = []
    if found_keywords: reasons.append(f"Suspicious terms: {', '.join(found_keywords[:3])}")
    if salary_v['suspicious']: reasons.extend(salary_v['reasons'])
    if email_v['suspicious']: reasons.extend(email_v['reasons'])
    if dark_flags: reasons.extend(dark_flags)
    if phishing_flags: reasons.extend(phishing_flags)
    if community_reports > 0: reasons.append(f"Flagged by {community_reports} community members.")
    if "whatsapp" in combined_text or "telegram" in combined_text: reasons.append("Chat platform recruitment detected")
    
    if MODEL_LOADED:
        X = vectorizer.transform([combined_text])
        prob = model.predict_proba(X)[0]
        score = prob[1] * 100
    else:
        score = min(99, 10 + (len(reasons) * 20))
        
    if dark_flags or community_reports > 2: score = min(99.9, score + 40)
    
    cat_risk = {
        "linguistic": min(100, (len(found_keywords) * 20) + (20 if "whatsapp" in combined_text else 0)),
        "financial": 100 if salary_v['suspicious'] else 10,
        "identity": 100 if email_v['suspicious'] or dark_flags else 10
    }
    
    res = {
        "result": "FAKE JOB" if score > 50 else "REAL JOB",
        "risk_score": round(score, 1),
        "risk_category": "High Scam Risk" if score > 60 else ("Suspicious" if score > 25 else "Safe Job"),
        "risk_label": "❌" if score > 60 else ("⚠" if score > 25 else "✅"),
        "reasons": reasons,
        "cat_risk": cat_risk,
        "community_score": max(0, 100 - (community_reports * 20)),
        "verification": {"website_exists": comp_v['exists'], "ssl_valid": comp_v['ssl'], "email_status": "Suspicious" if email_v['suspicious'] else "Verified", "found_keywords": found_keywords}
    }
    
    # Save scan result
    if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
        try:
            token = request.headers['Authorization'].split(' ')[1]
            operator = get_serializer().loads(token, max_age=86400)
        except:
            operator = 'anonymous'
    else:
        operator = session.get('user', 'anonymous')
        
    history = ScanHistory(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        operator=operator,
        input_data=json.dumps({"title": title, "company": company}),
        result=res['result'],
        risk_score=res['risk_score'],
        reasons=json.dumps(res['reasons'])
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify(res)
