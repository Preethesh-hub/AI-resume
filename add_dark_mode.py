import os
import re

CSS = """
        /* Dark Mode Variables & Overrides */
        body.dark-mode {
            background: #121212;
            color: #f0f0f0;
        }
        .dark-mode .topbar { background: rgba(30, 30, 30, 0.85); }
        .dark-mode .container, .dark-mode .card, .dark-mode .glass-panel { background: #1e1e1e; color: #f0f0f0; border-color: #333; }
        .dark-mode input, .dark-mode select, .dark-mode textarea { background: #2a2a2a; color: #fff; border-color: #444; }
        .dark-mode th, .dark-mode td { border-color: #444; }
        .dark-mode .pill { background: #2a2a2a; color: #ddd; }
"""

JS = """
    <script>
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            document.querySelector('.theme-toggle').textContent = isDark ? '☀️' : '🌙';
        }
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
            const toggle = document.querySelector('.theme-toggle');
            if (toggle) toggle.textContent = '☀️';
        }
    </script>
"""

BTN = """<button class="theme-toggle" onclick="toggleTheme()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; padding: 0 10px;">🌙</button>"""

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add CSS
    if "body.dark-mode" not in html:
        html = html.replace("</style>", CSS + "</style>")

    # 2. Add BTN
    if "theme-toggle" not in html:
        # Find the <div class="topbar-right"> or similar
        # If dashboard, it's <div class="nav-links">
        if "dashboard" in path:
            html = html.replace('<div class="nav-links">', '<div class="nav-links">\n                ' + BTN)
        elif "login" in path:
            # Login has no topbar in the same way, or maybe it does?
            # Let's just insert it at the top right absolutely positioned
            topbar = """<div style="position: absolute; top: 20px; right: 20px; z-index: 1000;">""" + BTN + """</div>"""
            html = html.replace('<body>', '<body>\n    ' + topbar)

    # 3. Add JS
    if "toggleTheme()" not in html:
        html = html.replace("</body>", JS + "\n</body>")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Processed {path}")

base_dir = r"c:\Users\preet\New folder (10)\app\templates"
process_file(os.path.join(base_dir, "dashboard.html"))
process_file(os.path.join(base_dir, "login.html"))
