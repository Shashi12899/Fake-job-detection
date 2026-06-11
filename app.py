import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.models import db
from backend.routes import api

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Use a strong secure key from environment, or a fallback for dev
app.secret_key = os.environ.get('SECRET_KEY', 'detectai_secret_secure_key_1337_fallback')

# Configure Database
base_dir = os.path.abspath(os.path.dirname(__file__))
db_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(base_dir, 'detectai.db'))
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db.init_app(app)

# Register API Blueprint
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
