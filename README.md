# DetectAI: Fake Job Detector 🛡️

A powerful, full-stack web application designed to detect fraudulent job postings using a combination of Rule-Based Heuristics, Natural Language Processing (NLP), and Machine Learning. 

With a premium "Cyberpunk/Glassmorphism" UI, this application provides an interactive experience for security analysts to scan URLs, images (OCR), and raw text for scams.

## 🚀 Features

- **Machine Learning Inference**: Uses `scikit-learn` and TF-IDF vectorization to probabilistically score the legitimacy of a job description.
- **Deep Forensic Verification**:
  - Validates Domain Registration & SSL Certificates.
  - Checks for disposable email addresses and public recruiter domains.
  - Scans for Phishing/Shortened links.
  - Extracts and analyzes unrealistic salary figures (LPA/Daily Pay).
- **OCR Integration**: Extracts text from job post screenshots using `pytesseract`.
- **Automated Web Scraping**: Scrapes job titles and descriptions directly from a given URL using `BeautifulSoup4`.
- **Advanced UI/UX**: Fully responsive Dashboard, Risk Heatmap, animated Terminal Forensics log, and dynamic charts (`Chart.js`).
- **Secure Backend Architecture**:
  - Powered by Flask, utilizing `Flask-SQLAlchemy` (SQLite/PostgreSQL ready).
  - Secure Password Hashing via `bcrypt`.
  - Built-in SSRF (Server-Side Request Forgery) protection for the web scraper.

## 📁 Repository Structure

```
fake-job-detector/
├── app.py                  # Main Flask Entry Point (Gunicorn Ready)
├── backend/                # API and Core Logic
│   ├── routes.py           # API Endpoints (Auth, Scan, History)
│   ├── models.py           # SQLAlchemy Database Models
│   └── utils.py            # Security & Heuristic Check Functions
├── ml/                     # Machine Learning Models & Training Scripts
│   ├── model.joblib        # Pre-trained Logistic Regression Model
│   ├── vectorizer.joblib   # TF-IDF Vectorizer
│   └── train_model.py      # Script to retrain the ML model
├── frontend/               # Vanilla JS/CSS/HTML Frontend
├── scripts/                # Database Utilities (Migrations)
└── requirements.txt        # Python Dependencies
```

## 🛠️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/fake-job-detector.git
   cd fake-job-detector
   ```
2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application:**
   ```bash
   python app.py
   ```
5. Visit `http://localhost:5000` in your browser.

## ☁️ Deployment (Render / Heroku)

This application is fully prepared for Cloud Deployment and supports dynamic PostgreSQL databases natively.

### Render Setup:
1. Push this repository to GitHub.
2. Go to **Render.com** > New Web Service > Connect your repository.
3. Set the Build Command: `pip install -r requirements.txt`
4. Set the Start Command: `gunicorn app:app`
5. *(Optional but Recommended)*: Create a Render PostgreSQL database and copy the "Internal Database URL". Add an Environment Variable `DATABASE_URL` with that value to ensure your data persists!

---
*Built with Flask, Vanilla JS, and scikit-learn.*
