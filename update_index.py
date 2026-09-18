import os
path = r"c:\Users\preet\New folder (10)\app\templates\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Dark mode css
dark_css = """
        /* ═══════════════════════════════════════════
           DARK MODE TOKENS
        ═══════════════════════════════════════════ */
        body.dark-mode {
            --bg-page: #121212;
            --bg-card: #1e1e1e;
            --bg-upload: #2d2d2d;
            --bg-upload-hover: #3d3d3d;
            --text-dark: #f0f0f0;
            --text-body: #d1d1d1;
            --text-light: #a0a0a0;
            --border: #333333;
            --border-light: #444444;
            --shadow-card: 0 4px 20px rgba(0,0,0,0.4);
            --lavender-light: #3b2f5b;
            --mint-light: #1c3d31;
            --peach-light: #4d2b15;
            --sky-light: #163d53;
            --coral-light: #521c1c;
            --teal-light: #16403a;
        }
        .dark-mode .topbar { background: rgba(30, 30, 30, 0.85); }
        .dark-mode .textarea, .dark-mode .jd-entry-input, .dark-mode .jd-entry { background: #252525; color: #f0f0f0; }
        .theme-toggle { background:none; border:none; cursor:pointer; font-size:1.2rem; }
"""
html = html.replace("        /* ═══════════════════════════════════════════\n           RESET & BASE", dark_css + "\n        /* ═══════════════════════════════════════════\n           RESET & BASE")

# 2. Topbar toggle button
nav_html = """
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark Mode">🌙</button>
            <a href="/dashboard" style="text-decoration: none; font-size: 0.9rem; font-weight: 700; color: var(--text-dark); transition: color 0.2s;" onmouseover="this.style.color='var(--lavender)'" onmouseout="this.style.color='var(--text-dark)'">Recruiter Dashboard</a>"""
html = html.replace("""<a href="/dashboard" style="text-decoration: none; font-size: 0.9rem; font-weight: 700; color: var(--text-dark); transition: color 0.2s;" onmouseover="this.style.color='var(--lavender)'" onmouseout="this.style.color='var(--text-dark)'">Recruiter Dashboard</a>""", nav_html)

# 3. Tab for LinkedIn
tabs_html = """<button class="mode-tab" id="tab-compare" onclick="switchMode('compare')">📋 Compare Jobs</button>
            <button class="mode-tab" id="tab-linkedin" onclick="switchMode('linkedin')">🌐 LinkedIn Optimizer</button>"""
html = html.replace("""<button class="mode-tab" id="tab-compare" onclick="switchMode('compare')">📋 Compare Jobs</button>""", tabs_html)

# 4. LinkedIn Mode div
linkedin_div = """
        <!-- ════════════════════════════════════════════════
             LINKEDIN MODE
        ════════════════════════════════════════════════ -->
        <div id="linkedin-mode" style="display:none;">
            <div class="layout single-col">
                <div class="card">
                    <div class="card-label sky"><span class="emoji">🌐</span> LinkedIn Profile Optimizer</div>
                    <form id="linkedin-form">
                        <label class="field-label">Target Role</label>
                        <input type="text" class="jd-entry-input" id="li-role" name="target_role" placeholder="e.g. Senior Software Engineer" required>
                        <label class="field-label" style="margin-top:16px;">Paste Your LinkedIn Text (About, Experience, etc.)</label>
                        <textarea class="textarea" id="li-text" name="profile_text" placeholder="Copy and paste your LinkedIn profile text here..." required></textarea>
                        
                        <button type="submit" class="btn-submit" id="li-submit-btn">
                            <span class="btn-inner">✨ Optimize Profile</span>
                        </button>
                        <div class="loading-area" id="li-loader">
                            <div class="loading-dots"><span></span><span></span><span></span></div>
                            <div class="loading-msg">Analyzing your profile...</div>
                        </div>
                    </form>
                    
                    <div id="li-results" style="display:none; margin-top:24px;">
                        <h3 style="margin-bottom:12px; font-weight:800; color:var(--text-dark);">Suggested Headline</h3>
                        <div class="card" style="background:var(--sky-light); border-color:var(--sky); margin-bottom:20px; padding:16px;">
                            <p id="li-headline" style="font-weight:700; color:var(--text-dark);"></p>
                        </div>
                        <h3 style="margin-bottom:12px; font-weight:800; color:var(--text-dark);">Suggested About Section</h3>
                        <div class="card" style="background:var(--mint-light); border-color:var(--mint); margin-bottom:20px; padding:16px;">
                            <p id="li-about" style="white-space:pre-wrap; color:var(--text-body);"></p>
                        </div>
                        <h3 style="margin-bottom:12px; font-weight:800; color:var(--text-dark);">Actionable Tips</h3>
                        <ul class="tips-list" id="li-tips"></ul>
                    </div>
                </div>
            </div>
        </div>
"""
html = html.replace("""<div class="footer">Made with ❤️ to help you land your dream job.</div>""", linkedin_div + '\n        <div class="footer">Made with ❤️ to help you land your dream job.</div>')

# 5. Interview questions in Single Mode
iq_div = """
                    <!-- Interview Questions -->
                    <div class="card" id="interview-card" style="display:none; margin-top:22px;">
                        <div class="card-label peach"><span class="emoji">🎤</span> Interview Predictor</div>
                        <p style="font-size:0.85rem; color:var(--text-light); margin-bottom:14px;">
                            Be prepared for these questions based on your experience gaps:
                        </p>
                        <ul class="rewrite-list" id="interview-list"></ul>
                    </div>
"""
html = html.replace("""<!-- AI Summary -->""", iq_div + "\n                    <!-- AI Summary -->")

# 6. Action Buttons
buttons_div = """
                    <!-- Action Buttons -->
                    <div style="display:flex; gap:16px; margin-top:22px;" id="action-buttons">
                        <button class="btn-add-jd" type="button" onclick="generateCoverLetter()" id="btn-cover-letter" style="margin-top:0; border-color:var(--lavender); color:var(--lavender);">✉️ Generate Cover Letter</button>
                        <button class="btn-add-jd" type="button" onclick="exportResume()" id="btn-export-pdf" style="margin-top:0; border-color:var(--teal); color:var(--teal);">📄 Export to PDF</button>
                    </div>
                    
                    <!-- Cover letter display -->
                    <div class="card" id="cover-letter-card" style="display:none; margin-top:22px;">
                        <div class="card-label lavender">Generated Cover Letter</div>
                        <textarea class="textarea" id="cover-letter-text" style="min-height:300px;"></textarea>
                    </div>
"""
html = html.replace("""<!-- AI Summary -->""", buttons_div + "\n                    <!-- AI Summary -->")

# 7. JavaScript additions
js_additions = """
        // ══════════════════════════════════════════
        // THEME TOGGLE
        // ══════════════════════════════════════════
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            document.querySelector('.theme-toggle').textContent = isDark ? '☀️' : '🌙';
        }
        
        // Load theme on startup
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
            document.querySelector('.theme-toggle').textContent = '☀️';
        }

        // Add switchMode logic for linkedin
        const originalSwitchMode = switchMode;
        switchMode = function(mode) {
            originalSwitchMode(mode);
            document.getElementById('linkedin-mode').style.display = mode === 'linkedin' ? 'block' : 'none';
            document.getElementById('tab-linkedin').classList.toggle('active', mode === 'linkedin');
        }
        
        // ══════════════════════════════════════════
        // NEW FEATURES
        // ══════════════════════════════════════════
        async function generateCoverLetter() {
            const btn = document.getElementById('btn-cover-letter');
            btn.textContent = 'Generating...';
            btn.disabled = true;
            try {
                const formData = new FormData(document.getElementById('analyze-form'));
                const token = localStorage.getItem('access_token');
                const headers = {};
                if (token) headers['Authorization'] = 'Bearer ' + token;
                
                const res = await fetch('/api/generate-cover-letter', { method: 'POST', body: formData, headers: headers });
                const data = await res.json();
                if (res.ok) {
                    document.getElementById('cover-letter-card').style.display = 'block';
                    document.getElementById('cover-letter-text').value = data.cover_letter;
                } else {
                    alert(data.detail);
                }
            } catch(e) {
                alert('Error generating cover letter');
            }
            btn.textContent = '✉️ Generate Cover Letter';
            btn.disabled = false;
        }

        function exportResume() {
            const text = prompt("Paste the text you want to export to PDF (or your updated resume text):");
            if (!text) return;
            
            const token = localStorage.getItem('access_token');
            fetch('/api/export-resume', {
                method: 'POST',
                headers: {
                    'Authorization': token ? 'Bearer ' + token : '',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({'resume_content': text})
            }).then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'resume.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
            });
        }

        document.getElementById('linkedin-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const role = document.getElementById('li-role').value;
            const text = document.getElementById('li-text').value;
            
            const loader = document.getElementById('li-loader');
            const btn = document.getElementById('li-submit-btn');
            btn.style.display = 'none';
            loader.classList.add('active');
            
            try {
                const token = localStorage.getItem('access_token');
                const headers = { 'Content-Type': 'application/json' };
                if (token) headers['Authorization'] = 'Bearer ' + token;
                
                const res = await fetch('/api/linkedin-optimize', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ profile_text: text, target_role: role })
                });
                const data = await res.json();
                if (res.ok) {
                    document.getElementById('li-headline').textContent = data.headline_suggestion;
                    document.getElementById('li-about').textContent = data.summary_suggestion;
                    document.getElementById('li-tips').innerHTML = data.tips.map(t => `<li>${t}</li>`).join('');
                    document.getElementById('li-results').style.display = 'block';
                } else {
                    alert(data.detail);
                }
            } catch(e) {
                alert('Error');
            }
            loader.classList.remove('active');
            btn.style.display = 'block';
        });
"""
html = html.replace("""<script>""", """<script>\n""" + js_additions)

iq_js = """
                // ── AI Interview Questions ──
                const interviewCard = document.getElementById('interview-card');
                if (data.interview_questions && data.interview_questions.length) {
                    interviewCard.style.display = 'block';
                    document.getElementById('interview-list').innerHTML =
                        data.interview_questions.map(q => `<li>• ${q}</li>`).join('');
                } else {
                    interviewCard.style.display = 'none';
                }
"""
html = html.replace("""                // ── AI Rewrite Suggestions ──""", iq_js + """\n                // ── AI Rewrite Suggestions ──""")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated index.html successfully.")
