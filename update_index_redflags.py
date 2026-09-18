import os

path = r"c:\Users\preet\New folder (10)\app\templates\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

html_snippet = """
                    <!-- Red Flags -->
                    <div class="card" id="red-flags-card" style="display:none; margin-top:22px;">
                        <div class="card-label" style="color:#ef4444; border-color:#ef4444; background:rgba(239, 68, 68, 0.1);">
                            <span class="emoji">🚩</span> Job Description Red Flags
                        </div>
                        <p style="font-size:0.85rem; color:var(--text-light); margin-bottom:14px;">
                            We detected some toxic corporate buzzwords in the job description:
                        </p>
                        <ul class="tips-list" id="red-flags-list" style="color:#ef4444;"></ul>
                    </div>
"""
if 'id="red-flags-card"' not in html:
    html = html.replace('                    <!-- AI Rewrite Suggestions -->', html_snippet + '\n                    <!-- AI Rewrite Suggestions -->')

js_snippet = """
                // ── Red Flags ──
                const redFlagsCard = document.getElementById('red-flags-card');
                if (data.red_flags && data.red_flags.length) {
                    redFlagsCard.style.display = 'block';
                    document.getElementById('red-flags-list').innerHTML =
                        data.red_flags.map(f => `<li><strong>"${f.phrase}"</strong>: ${f.warning}</li>`).join('');
                } else {
                    redFlagsCard.style.display = 'none';
                }
"""
if "redFlagsCard" not in html:
    html = html.replace('// ── AI Rewrite Suggestions ──', js_snippet + '\n                // ── AI Rewrite Suggestions ──')

with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated index.html successfully")
