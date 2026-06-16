from flask import Flask, render_template, redirect, url_for, flash, request, session
import datetime, random
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os

from models import User, db
from forms import RegistrationForm, LoginForm, JobForm, OTPForm

app = Flask(__name__)
# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'replace-with-a-secure-secret-key')
# Mail settings (use environment variables)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Initialize extensions
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

# Email confirmation route
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, max_age=3600)
    except Exception:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=email).first_or_404()
    if not user.confirmed:
        user.confirmed = True
        db.session.commit()
        flash('Your account has been verified! You can now log in.', 'success')
    else:
        flash('Account already verified.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_pw, confirmed=False)
        db.session.add(user)
        db.session.commit()
        # Generate OTP
        otp_code = f"{random.randint(0, 999999):06d}"
        otp_exp = datetime.datetime.utcnow() + timedelta(minutes=5)
        user.otp = otp_code
        user.otp_expiration = otp_exp
        db.session.commit()
        # Send OTP email
        otp_msg = Message('Your OTP Code', recipients=[user.email],
                         html=f"<p>Hi {user.full_name},</p><p>Your OTP is <strong>{otp_code}</strong>. It expires in 5 minutes.</p>")
        mail.send(otp_msg)
        # Store pending user id in session for OTP verification
        session['pending_user_id'] = user.id
        flash('Registration successful! An OTP has been sent to your email.', 'success')
        return redirect(url_for('otp'))
    return render_template('register.html', title='Register', form=form)

# OTP verification route
@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if 'pending_user_id' not in session:
        flash('No pending verification.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['pending_user_id'])
    form = OTPForm()
    if form.validate_on_submit():
        if user.otp == form.otp.data and user.otp_expiration > datetime.datetime.utcnow():
            user.confirmed = True
            user.otp = None
            user.otp_expiration = None
            db.session.commit()
            flash('Your account is verified. Please log in.', 'success')
            session.pop('pending_user_id', None)
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired OTP.', 'danger')
    return render_template('otp.html', title='OTP Verification', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.confirmed:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login'))
            # Generate OTP for login
            otp_code = f"{random.randint(0, 999999):06d}"
            otp_exp = datetime.datetime.utcnow() + timedelta(minutes=5)
            user.otp = otp_code
            user.otp_expiration = otp_exp
            db.session.commit()
            # Send OTP email
            otp_msg = Message('Your Login OTP Code', recipients=[user.email],
                             html=f"<p>Hi {user.full_name},</p><p>Your login OTP is <strong>{otp_code}</strong>. It expires in 5 minutes.</p>")
            mail.send(otp_msg)
            session['login_pending_user_id'] = user.id
            flash('Login OTP sent to your email. Please verify.', 'info')
            return redirect(url_for('login_otp'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)
@app.route('/login_otp', methods=['GET', 'POST'])
def login_otp():
    if 'login_pending_user_id' not in session:
        flash('No pending login verification.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['login_pending_user_id'])
    form = OTPForm()
    if form.validate_on_submit():
        if user.otp == form.otp.data and user.otp_expiration > datetime.datetime.utcnow():
            # OTP valid, log in user
            login_user(user)
            # Clear OTP fields
            user.otp = None
            user.otp_expiration = None
            db.session.commit()
            session.pop('login_pending_user_id', None)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid or expired OTP.', 'danger')
    return render_template('otp.html', title='Login OTP Verification', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = JobForm()
    prediction = None
    if form.validate_on_submit():
        # Placeholder for ML model inference
        description = form.description.data
        # TODO: integrate model inference here
        prediction = 'REAL'  # dummy output
    return render_template('dashboard.html', title='Dashboard', form=form, prediction=prediction)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
