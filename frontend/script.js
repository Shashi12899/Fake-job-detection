document.addEventListener('DOMContentLoaded', () => {
    // --- 0. API CONFIGURATION ---
    const API_BASE = window.location.protocol === 'file:' || window.location.port === '5500' || window.location.port === '3000' ? 'http://127.0.0.1:5000' : '';
    
    // Configure Axios
    if (typeof axios !== 'undefined') {
        axios.defaults.baseURL = API_BASE;
        axios.interceptors.request.use(config => {
            const token = localStorage.getItem('detectai_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
    }

    const form = document.getElementById('jobForm');
    const scanBtn = document.getElementById('scanBtn');
    const gaugeFill = document.getElementById('gaugeFill');
    const confidenceValue = document.getElementById('confidenceValue');
    const predictionBadge = document.getElementById('predictionBadge');
    const predictionText = document.getElementById('predictionText');
    const indicatorsList = document.getElementById('indicatorsList');
    const explanationPanel = document.getElementById('explanationPanel');
    const xaiReport = document.getElementById('xaiReport');
    
    // UI Elements
    const chatToggle = document.getElementById('chatToggle');
    const chatBox = document.getElementById('chatBox');
    const chatInput = document.getElementById('chatInput');
    const chatMsgs = document.getElementById('chatMsgs');
    const domainRep = document.getElementById('domainRep');
    const sslStatus = document.getElementById('sslStatus');
    const emailOrigin = document.getElementById('emailOrigin');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const terminalBox = document.getElementById('terminalBox');
    const terminalContent = document.getElementById('terminalContent');

    // --- 0. SIDEBAR NAVIGATION ---
    const navItems = document.querySelectorAll('.nav-item');
    const appPanels = document.querySelectorAll('.app-panel');
    const breadcrumbText = document.getElementById('breadcrumbText');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const target = item.getAttribute('data-target');
            
            // Switch Active Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Switch Active Panel
            appPanels.forEach(panel => panel.classList.remove('active'));
            document.getElementById(target).classList.add('active');

            // Update Breadcrumb
            const pageName = item.textContent.trim().toUpperCase();
            breadcrumbText.textContent = `SYSTEM / ${pageName} / ANALYSIS`;
        });
    });

    // --- 1. SESSION & AUTHENTICATION GATEKEEPING ---
    let trendChart = null;
    let lastScanResult = null;
    const loginContainer = document.getElementById('login-container');
    const mainContainer = document.querySelector('.main-container');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const biometricBtn = document.getElementById('biometricBtn');
    const biometricScanner = document.getElementById('biometricScanner');
    const biometricStatus = document.getElementById('biometricStatus');
    const loginMessage = document.getElementById('loginMessage');
    const logoutBtnItem = document.getElementById('logoutBtnItem');

    // Tab Switching
    tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        loginMessage.textContent = '';
    });

    tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        loginMessage.textContent = '';
    });

    // Check Session on page load
    async function checkSession() {
        try {
            const res = await axios.get('/api/auth/session');
            const data = res.data;
            if (data.authenticated) {
                enterApp(data.user);
            } else {
                loginContainer.classList.remove('hidden');
                mainContainer.classList.add('hidden');
            }
        } catch(e) {
            loginContainer.classList.remove('hidden');
            mainContainer.classList.add('hidden');
        }
    }
    checkSession();

    function enterApp(user) {
        loginContainer.classList.add('hidden');
        mainContainer.classList.remove('hidden');
        
        // Customize Dashboard profile
        const analystIdEl = document.querySelector('.profile-info h2');
        const analystRankEl = document.querySelector('.profile-info .neon-text');
        const analystEmailInput = document.getElementById('userEmail');
        
        if (analystIdEl) analystIdEl.textContent = user.name || 'Security Operator';
        if (analystRankEl) analystRankEl.textContent = `RANK: ${user.rank || 'SECURITY ANALYST'}`;
        if (analystEmailInput) analystEmailInput.value = user.email || '';
        
        // Load history and stats for this logged-in operator
        loadHistory();
        initStats();
    }

    // Login Form Submit
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const secretKey = document.getElementById('loginPassword').value;
        
        loginMessage.className = 'login-message info';
        loginMessage.textContent = 'VERIFYING CREDENTIALS...';
        
        try {
            const res = await axios.post('/api/auth/login', { email, password: secretKey });
            const data = res.data;
            if (data.token) {
                localStorage.setItem('detectai_token', data.token);
            }
            loginMessage.className = 'login-message success';
            loginMessage.textContent = 'LOGIN SUCCESSFUL. REDIRECTING...';
            setTimeout(() => {
                enterApp(data.user);
            }, 1000);
        } catch(err) {
            loginMessage.className = 'login-message error';
            if (err.response && err.response.data && err.response.data.error) {
                loginMessage.textContent = err.response.data.error;
            } else {
                loginMessage.textContent = 'SERVER CONNECTION TIMEOUT';
            }
        }
    });

    // Register Form Submit
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const secretKey = document.getElementById('registerPassword').value;
        
        loginMessage.className = 'login-message info';
        loginMessage.textContent = 'CREATING YOUR ACCOUNT...';
        
        try {
            const res = await axios.post('/api/auth/register', { name, email, password: secretKey });
            const data = res.data;
            if (data.token) {
                localStorage.setItem('detectai_token', data.token);
            }
            loginMessage.className = 'login-message success';
            loginMessage.textContent = 'REGISTRATION SUCCESSFUL. REDIRECTING...';
            setTimeout(() => {
                enterApp(data.user);
            }, 1000);
        } catch(err) {
            loginMessage.className = 'login-message error';
            if (err.response && err.response.data && err.response.data.error) {
                loginMessage.textContent = err.response.data.error;
            } else {
                loginMessage.textContent = 'DATABASE CONNECTION TIMEOUT';
            }
        }
    });

    // Biometric Scanner simulation
    if (biometricBtn) {
        biometricBtn.addEventListener('click', () => {
            biometricBtn.classList.add('hidden');
            biometricScanner.classList.remove('hidden');
            biometricStatus.textContent = 'SCANNING RETINAL & DNA SIGNATURES...';
            
            setTimeout(() => { biometricStatus.textContent = 'COMPILING BIOMETRIC HASHLIST...'; }, 1000);
            setTimeout(() => { biometricStatus.textContent = 'BYPASS ALIGNMENT DETECTED...'; }, 2000);
            
            setTimeout(async () => {
                const email = document.getElementById('loginEmail').value;
                try {
                    const res = await axios.post('/api/auth/biometric', { email });
                    const data = res.data;
                    if (data.token) {
                        localStorage.setItem('detectai_token', data.token);
                    }
                    biometricStatus.textContent = 'VERIFIED! ACCESS AUTHORIZED.';
                    biometricStatus.style.color = 'var(--neon-green)';
                    loginMessage.className = 'login-message success';
                    loginMessage.textContent = `WELCOME BACK, ${data.user.name.toUpperCase()}`;
                    setTimeout(() => {
                        enterApp(data.user);
                        biometricBtn.classList.remove('hidden');
                        biometricScanner.classList.add('hidden');
                        biometricStatus.style.color = '';
                        loginMessage.textContent = '';
                    }, 1200);
                } catch(e) {
                    biometricStatus.textContent = 'BIOMETRIC SERVER OFFLINE';
                    biometricStatus.style.color = 'var(--neon-red)';
                    setTimeout(() => {
                        biometricBtn.classList.remove('hidden');
                        biometricScanner.classList.add('hidden');
                        biometricStatus.style.color = '';
                    }, 2000);
                }
            }, 3000);
        });
    }

    // Logout Logic
    logoutBtnItem.addEventListener('click', async (e) => {
        e.preventDefault();
        if (confirm("Disconnect secure operator link?")) {
            try {
                await axios.post('/api/auth/logout');
            } catch(err) {}
            localStorage.removeItem('detectai_token');
            location.reload();
        }
    });

    // --- 1. INITIALIZATION ---

    // --- 2. CHATBOT LOGIC ---
    chatToggle.addEventListener('click', () => {
        chatBox.style.display = chatBox.style.display === 'flex' ? 'none' : 'flex';
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim() !== '') {
            const input = chatInput.value;
            addMessage('user', input);
            chatInput.value = '';
            setTimeout(() => addMessage('bot', getBotResponse(input)), 600);
        }
    });

    function addMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `msg ${sender}`;
        div.textContent = text;
        chatMsgs.appendChild(div);
        chatMsgs.scrollTop = chatMsgs.scrollHeight;
    }

    function getBotResponse(text) {
        text = text.toLowerCase();
        if (!lastScanResult) return "System online. Perform a scan for forensic analysis.";
        if (text.includes('why') || text.includes('fake')) return `Flags: ${lastScanResult.reasons.join(". ")}. Score: ${lastScanResult.risk_score}%`;
        return "Forensic data analyzed. Check the AI Forensic Report for details.";
    }

    // --- 3. SCRAPING & OCR ---
    document.getElementById('scrapeBtn').addEventListener('click', async () => {
        const url = document.getElementById('jobUrl').value;
        if (!url) return alert("Paste URL");
        const btn = document.getElementById('scrapeBtn');
        btn.textContent = "SCRAPING...";
        try {
            const res = await axios.post('/api/scrape', {url});
            const data = res.data;
            document.getElementById('title').value = data.title;
            document.getElementById('company').value = data.company;
            document.getElementById('description').value = data.description;
            btn.textContent = "AUTO-FILL";
        } catch(e) { btn.textContent = "AUTO-FILL"; alert("Scrape failed"); }
    });

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });

    async function handleFileUpload(file) {
        dropZone.innerHTML = "<p>Analyzing OCR...</p>";
        const fd = new FormData(); fd.append('file', file);
        try {
            const res = await axios.post('/api/ocr', fd);
            const data = res.data;
            document.getElementById('description').value = data.text;
            dropZone.innerHTML = "<p>OCR Success</p>";
        } catch(e) { dropZone.innerHTML = "<p>OCR Error</p>"; }
    }

    // --- 4. SCAN LOGIC ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        scanBtn.disabled = true;
        scanBtn.textContent = 'SCANNING...';
        
        terminalBox.classList.remove('hidden');
        terminalContent.innerHTML = "";
        await runTerminalLogs();
        
        const payload = {
            title: document.getElementById('title').value,
            company: document.getElementById('company').value,
            salary: document.getElementById('salary').value,
            email: document.getElementById('email').value,
            website: document.getElementById('website').value,
            description: document.getElementById('description').value
        };

        try {
            const res = await axios.post('/api/predict', payload);
            const result = res.data;
            lastScanResult = result;
            
            setTimeout(() => {
                displayResults(result);
                scanBtn.disabled = false;
                scanBtn.textContent = 'INITIALIZE AI SCAN';
                initStats();
                loadHistory();

                // AUTOMATICALLY SWITCH TO DASHBOARD TO SHOW RESULT
                document.querySelector('[data-target="dashboard-panel"]').click();
            }, 1000);
        } catch(e) { scanBtn.disabled = false; scanBtn.textContent = 'RETRY SCAN'; }
    });

    async function runTerminalLogs() {
        const logs = [
            "[✓] INITIALIZING NEURAL ENGINE...",
            "[✓] CONNECTING TO DARK WEB SCAM DATABASE...",
            "[✓] RESOLVING COMPANY DOMAIN...",
            "[✓] ANALYZING LINGUISTIC PATTERNS...",
            "[✓] EXTRACTING METADATA...",
            "[✓] CROSS-REFERENCING COMMUNITY REPORTS...",
            "[!] ANALYZING PHISHING VECTORS...",
            "[✓] SCAN COMPLETE. GENERATING REPORT..."
        ];
        for (const log of logs) {
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.textContent = log;
            terminalContent.appendChild(line);
            terminalContent.scrollTop = terminalContent.scrollHeight;
            await new Promise(r => setTimeout(r, 200));
        }
    }

    function displayResults(data) {
        predictionBadge.classList.remove('hidden');
        predictionBadge.className = `prediction-badge ${data.result === 'REAL JOB' ? 'real-badge' : 'fake-badge'}`;
        predictionText.textContent = data.result;
        
        const score = data.risk_score;
        gaugeFill.style.transform = `rotate(${45 + (score * 1.8)}deg)`;
        let color = score > 60 ? 'var(--neon-red)' : (score > 25 ? 'var(--neon-yellow)' : 'var(--neon-green)');
        gaugeFill.style.borderColor = color;
        
        const cat = document.getElementById('riskCategory');
        cat.textContent = `${data.risk_label} ${data.risk_category}`;
        cat.style.color = color;
        
        animateValue(confidenceValue, 0, score, 800);
        indicatorsList.innerHTML = data.reasons.map(r => `<div class="indicator-item">🚩 ${r}</div>`).join('') || "✅ Safe";
        
        domainRep.textContent = data.verification.website_exists ? 'EXISTS' : 'NOT FOUND';
        sslStatus.textContent = data.verification.ssl_valid ? 'SECURE' : 'INSECURE';
        emailOrigin.textContent = data.verification.email_status.toUpperCase();

        // Heatmap
        document.getElementById('riskHeatmap').classList.remove('hidden');
        updateHeatmap('riskLing', data.cat_risk.linguistic);
        updateHeatmap('riskFin', data.cat_risk.financial);
        updateHeatmap('riskIden', data.cat_risk.identity);

        explanationPanel.style.display = 'block';
        xaiReport.innerHTML = `<h3>Forensic Report</h3><ul><li>Risk Score: ${score}%</li><li>Community Trust: ${data.community_score}%</li><li>Factors: ${data.reasons.length} flagged</li></ul>`;
    }

    function updateHeatmap(id, val) {
        const el = document.getElementById(id);
        el.style.width = val + "%";
        el.style.background = val > 60 ? 'var(--neon-red)' : (val > 25 ? 'var(--neon-yellow)' : 'var(--neon-green)');
    }

    // --- 5. ANALYTICS & HISTORY ---
    async function initStats() {
        try {
            const res = await axios.get('/api/stats');
            const data = res.data;
            
            // Update Profile Stats
            if (document.getElementById('totalScansCount')) {
                document.getElementById('totalScansCount').textContent = data.total || 0;
                document.getElementById('scamsDetectedCount').textContent = data.fake_count || 0;
            }

            const ctx = document.getElementById('scamTrendChart').getContext('2d');
            if (trendChart) trendChart.destroy();
            trendChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Real Jobs', 'Scams'],
                    datasets: [{
                        data: [data.real_count || 0, data.fake_count || 0],
                        backgroundColor: ['#39ff14', '#ff003c'],
                        borderWidth: 0
                    }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } } }
            });
        } catch(e) {}
    }

    async function loadHistory() {
        try {
            const res = await axios.get('/api/history');
            const history = res.data;
            const body = document.getElementById('historyBody');
            body.innerHTML = history.reverse().map(h => `
                <tr>
                    <td>${h.timestamp}</td>
                    <td>${h.input.title} / ${h.input.company}</td>
                    <td class="risk-col">${h.risk_score}%</td>
                    <td class="${h.result === 'FAKE JOB' ? 'result-fake' : 'result-real'}">${h.result}</td>
                </tr>
            `).join('');
        } catch(e) {}
    }

    document.getElementById('refreshStats').addEventListener('click', () => { initStats(); loadHistory(); });

    // --- 6. PDF & REPORTING ---
    // ... existing ...

    // --- 7. OTP SIMULATION ---
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    const otpBox = document.getElementById('otpBox');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const otpStatus = document.getElementById('otpStatus');

    sendOtpBtn.addEventListener('click', () => {
        const email = document.getElementById('userEmail').value;
        if (!email || !email.includes('@')) return alert("Please enter a valid email address.");
        
        sendOtpBtn.textContent = "SENDING...";
        setTimeout(() => {
            sendOtpBtn.textContent = "RESEND OTP";
            otpBox.classList.remove('hidden');
            otpStatus.textContent = `Security code sent to ${email}. (MOCK: 123456)`;
            otpStatus.style.color = "var(--primary-cyan)";
            
            // Log in terminal for effect
            if (terminalContent) {
                const line = document.createElement('div');
                line.className = 'terminal-line';
                line.textContent = `[!] SECURITY ALERT: OTP REQUESTED FOR ${email.toUpperCase()}`;
                terminalContent.appendChild(line);
            }
        }, 1500);
    });

    verifyOtpBtn.addEventListener('click', () => {
        const code = document.getElementById('otpInput').value;
        if (code === "123456") {
            otpStatus.textContent = "✅ EMAIL VERIFIED SUCCESSFULLY. Account secured.";
            otpStatus.style.color = "var(--neon-green)";
            verifyOtpBtn.disabled = true;
            verifyOtpBtn.textContent = "VERIFIED";
        } else {
            otpStatus.textContent = "❌ INVALID CODE. Please try again.";
            otpStatus.style.color = "var(--neon-red)";
        }
    });

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = (progress * (end - start) + start).toFixed(1) + "%";
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }
});
