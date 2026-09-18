import os

OLD_CSS = """
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

NEW_CSS = """
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
        .dark-mode input, .dark-mode select, .dark-mode textarea { background: #2a2a2a; color: #fff; border-color: #444; }
        .dark-mode th, .dark-mode td { border-color: #444; }
"""

def fix_css(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    
    if OLD_CSS in html:
        html = html.replace(OLD_CSS, NEW_CSS)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Fixed CSS in {path}")
    else:
        print(f"OLD_CSS not found in {path}")

base_dir = r"c:\Users\preet\New folder (10)\app\templates"
fix_css(os.path.join(base_dir, "dashboard.html"))
fix_css(os.path.join(base_dir, "login.html"))
