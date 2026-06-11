import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

# Synthetic data for training
data = {
    "text": [
        # Real Jobs
        "Software Engineer Google We are looking for a talented software engineer to join our team. Salary 120000. Contact hr@google.com.",
        "Frontend Developer Microsoft Join us to build modern web applications using React. Salary 100k-130k. email: careers@microsoft.com.",
        "Data Scientist Amazon Exciting opportunity for a data scientist. Experience with machine learning required. Contact jobs@amazon.com",
        "Backend Developer Netflix We need a strong Python backend developer. Salary competitive. Email jobs@netflix.com",
        "Full Stack Web Developer StartUp Inc Looking for a full stack dev to help build our MVP. Normal salary.",
        "Cybersecurity Analyst Bank of America We are hiring a security analyst. Please apply through our website. Salary $90,000.",
        # Fake Jobs
        "Work From Home Data Entry Easy Money No experience needed! Make $5000 a week working 2 hours a day. Contact free-money-scam@gmail.com",
        "Account Assistant Western Union Transfer. You will receive payments and forward them. Keep 10% commission. Contact westernunion-scam123@yahoo.com",
        "Secret Shopper Walmart Fake. We will send you a check for $3000, you deposit it and send $2000 back to us via wire transfer.",
        "Package Forwarding Manager Shipping Co. Receive packages at your home and reship them. Excellent pay $4000/month. No interview required.",
        "Crypto Investment Advisor. Guaranteed returns. Send money to this wallet. Contact crypto-scammer@protonmail.com",
        "Immediate Hire Cashier. Send your bank details and social security number to start immediately. Western Union accepted.",
        "Data Entry Clerk $200/hr. Send us your credit card info to pay for the starter kit. You will be rich soon. Wire transfer only."
    ],
    "label": [
        0, 0, 0, 0, 0, 0, # 0 = Real
        1, 1, 1, 1, 1, 1, 1  # 1 = Fake
    ]
}

df = pd.DataFrame(data)

# Extract features
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['label']

# Train Logistic Regression Model
model = LogisticRegression()
model.fit(X, y)

# Save the model and vectorizer
joblib.dump(model, 'model.joblib')
joblib.dump(vectorizer, 'vectorizer.joblib')

print("Model and vectorizer trained and saved successfully.")
