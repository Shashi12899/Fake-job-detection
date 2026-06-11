import re
import socket
import ssl
from urllib.parse import urlparse
import ipaddress

SCAM_BLACKLIST = {
    "domains": ["jobs-amazon.cc", "google-recruitment.top", "work-from-home.biz", "earn-fast.net"],
    "emails": ["hr.verify@gmail.com", "official.jobs@outlook.com"],
    "companies": ["Global Wealth Systems", "Fast Cash Inc", "Crypto Mining Jobs Ltd"]
}

SUSPICIOUS_KEYWORDS = [
    "western union", "wire transfer", "deposit", "credit card", "starter kit", 
    "no experience needed", "guaranteed returns", "forwarding", "commission",
    "pay registration fee", "instant joining", "no interview", "work from home earn",
    "whatsapp", "telegram", "immediate hiring", "bank details", "application fee",
    "security deposit", "processing fee", "buy equipment", "earn daily", "dm for details",
    "chat with us", "gpay", "paytm", "binance", "crypto"
]

def is_safe_url(url):
    """
    Checks if a URL is safe to fetch (prevents SSRF).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Resolve IP
        ip_addr = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_addr)
        
        # Block private, loopback, multicast, etc.
        if ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_reserved or ip.is_link_local:
            return False
            
        return True
    except Exception:
        return False

def verify_company_details(website):
    if not website: return {"exists": False, "ssl": False, "domain": ""}
    domain = website.replace('https://', '').replace('http://', '').split('/')[0]
    try:
        socket.gethostbyname(domain)
        exists = True
    except: exists = False
    has_ssl = False
    if exists:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    has_ssl = True
        except: has_ssl = False
    return {"exists": exists, "ssl": has_ssl, "domain": domain}

def verify_email(email, company_name, website_domain):
    if not email: return {"suspicious": True, "reasons": ["No email provided"]}
    email = email.lower()
    local_part, domain = email.split('@') if '@' in email else ('', '')
    disposable = ['mailinator.com', 'tempmail.com', 'yopmail.com']
    public = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    reasons = []
    if domain in disposable: reasons.append("Disposable email domain")
    if domain in public: reasons.append("Public recruiter email domain")
    if website_domain and website_domain not in domain and domain not in public:
        reasons.append(f"Domain mismatch: @{domain} vs {website_domain}")
    return {"suspicious": len(reasons) > 0, "reasons": reasons, "domain": domain}

def analyze_salary(salary_text, description):
    reasons = []
    salary_text = salary_text.lower()
    lpa_match = re.search(r'(\d+)\s*lpa', salary_text)
    if lpa_match and int(lpa_match.group(1)) > 40:
        if "fresher" in description.lower() or "no experience" in description.lower():
            reasons.append(f"Unrealistic salary ({lpa_match.group(1)} LPA) for entry-level")
    if any(t in salary_text for t in ["daily pay", "weekly pay"]):
        reasons.append("Suspicious pay frequency (Daily/Weekly)")
    return {"suspicious": len(reasons) > 0, "reasons": reasons}

def detect_phishing_links(text):
    reasons = []
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'buff.ly', 'is.gd']
    for link in links:
        if any(s in link for s in shorteners):
            reasons.append(f"Suspicious shortened link detected: {link}")
    return reasons

def check_dark_web(company, website, email):
    flags = []
    domain = website.replace('https://', '').replace('http://', '').split('/')[0]
    if domain in SCAM_BLACKLIST['domains']: flags.append(f"Blacklisted domain: {domain}")
    if email in SCAM_BLACKLIST['emails']: flags.append(f"Blacklisted recruiter: {email}")
    if company in SCAM_BLACKLIST['companies']: flags.append(f"Flagged entity: {company}")
    return flags
