import os

path = r"c:\Users\preet\New folder (10)\app\templates\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

target = "if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);"
replacement = """if (response.status === 401) {
                    alert('Your session has expired or you are not logged in. Redirecting to login...');
                    window.location.href = '/login';
                    return;
                }
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);"""

if target in html:
    html = html.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed 401 redirect in index.html")
else:
    print("Target not found")
