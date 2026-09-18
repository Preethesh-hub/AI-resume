import os
import re

BTN = """<button class="theme-toggle" onclick="toggleTheme()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; padding: 0 10px;">🌙</button>"""

def fix_dashboard(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Check if BTN is already present
    if BTN in html:
        print("Dashboard already has BTN")
        return
        
    target = '<div style="display: flex; gap: 16px; align-items: center;">'
    if target in html:
        html = html.replace(target, target + '\n            ' + BTN)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("Fixed dashboard.html")
    else:
        print("Could not find target in dashboard.html")

def fix_login(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Remove the ugly absolute positioned button
    ugly = '<div style="position: absolute; top: 20px; right: 20px; z-index: 1000;">' + BTN + '</div>'
    if ugly in html:
        html = html.replace(ugly, '')
        
    if BTN not in html:
        target = '<div style="display: flex; gap: 16px; align-items: center;">'
        if target in html:
            html = html.replace(target, target + '\n            ' + BTN)
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed login.html")

base_dir = r"c:\Users\preet\New folder (10)\app\templates"
fix_dashboard(os.path.join(base_dir, "dashboard.html"))
fix_login(os.path.join(base_dir, "login.html"))
