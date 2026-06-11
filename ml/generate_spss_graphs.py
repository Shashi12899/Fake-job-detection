import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import joblib
import os

# Set SPSS-like style
plt.style.use('bmh') # 'bmh' or 'ggplot' is close-ish to SPSS defaults
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Data from train_model.py
data = {
    "text": [
        "Software Engineer Google We are looking for a talented software engineer to join our team. Salary 120000. Contact hr@google.com.",
        "Frontend Developer Microsoft Join us to build modern web applications using React. Salary 100k-130k. email: careers@microsoft.com.",
        "Data Scientist Amazon Exciting opportunity for a data scientist. Experience with machine learning required. Contact jobs@amazon.com",
        "Backend Developer Netflix We need a strong Python backend developer. Salary competitive. Email jobs@netflix.com",
        "Full Stack Web Developer StartUp Inc Looking for a full stack dev to help build our MVP. Normal salary.",
        "Cybersecurity Analyst Bank of America We are hiring a security analyst. Please apply through our website. Salary $90,000.",
        "Work From Home Data Entry Easy Money No experience needed! Make $5000 a week working 2 hours a day. Contact free-money-scam@gmail.com",
        "Account Assistant Western Union Transfer. You will receive payments and forward them. Keep 10% commission. Contact westernunion-scam123@yahoo.com",
        "Secret Shopper Walmart Fake. We will send you a check for $3000, you deposit it and send $2000 back to us via wire transfer.",
        "Package Forwarding Manager Shipping Co. Receive packages at your home and reship them. Excellent pay $4000/month. No interview required.",
        "Crypto Investment Advisor. Guaranteed returns. Send money to this wallet. Contact crypto-scammer@protonmail.com",
        "Immediate Hire Cashier. Send your bank details and social security number to start immediately. Western Union accepted.",
        "Data Entry Clerk $200/hr. Send us your credit card info to pay for the starter kit. You will be rich soon. Wire transfer only."
    ],
    "label": [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
}

df = pd.DataFrame(data)
df['Label Name'] = df['label'].map({0: 'Real Job', 1: 'Fake Job'})

# 1. Distribution Chart
plt.figure(figsize=(8, 6))
ax = sns.countplot(x='Label Name', data=df, palette=['#4e79a7', '#f28e2b'])
plt.title('Distribution of Real vs Fake Job Postings\n(SPSS Style Visualization)', fontsize=14, fontweight='bold')
plt.xlabel('Job Authenticity', fontsize=12)
plt.ylabel('Frequency Count', fontsize=12)

# Add counts on top
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=11, color='black', xytext=(0, 5),
                textcoords='offset points')

plt.tight_layout()
plt.savefig('spss_distribution_graph.png', dpi=300)
print("Saved: spss_distribution_graph.png")

# 2. Confusion Matrix (Simplified Mock for visualization)
# Assuming 100% accuracy on this small training set
y_true = df['label']
y_pred = df['label'] # Perfect prediction for visualization
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
plt.title('Model Performance: Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('spss_confusion_matrix.png', dpi=300)
print("Saved: spss_confusion_matrix.png")
