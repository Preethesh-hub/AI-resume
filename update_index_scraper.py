import os

path = r"c:\Users\preet\New folder (10)\app\templates\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

ui_snippet = """
                        <label class="field-label" for="jd_url">🔗 Auto-Fetch Job Description (Optional)</label>
                        <div style="display:flex; gap:10px; margin-bottom:20px;">
                            <input type="url" id="jd_url" class="textarea" style="min-height: 40px; padding:10px; margin-bottom:0;" placeholder="Paste Indeed, Greenhouse, or Company URL...">
                            <button type="button" class="btn-submit" id="btn-fetch-jd" style="margin-top:0; padding:10px 20px; white-space:nowrap; border-radius:12px; width:auto; font-size:1rem;">Fetch Text</button>
                        </div>
"""
if 'for="jd_url"' not in html:
    html = html.replace(
        '<label class="field-label" for="job_description">✍️ Paste the Job Description</label>',
        ui_snippet + '\n                        <label class="field-label" for="job_description">✍️ Paste the Job Description</label>'
    )

js_snippet = """
        document.getElementById('btn-fetch-jd').addEventListener('click', async () => {
            const url = document.getElementById('jd_url').value;
            if (!url) {
                alert('Please enter a URL first.');
                return;
            }
            const btn = document.getElementById('btn-fetch-jd');
            const originalText = btn.textContent;
            btn.textContent = 'Fetching...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/scrape-jd', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || 'Failed to fetch URL');
                }
                
                const data = await response.json();
                document.getElementById('job_description').value = data.text;
                alert('Job description fetched successfully!');
            } catch (e) {
                alert('Error fetching JD: ' + e.message + '. Please paste manually.');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
"""
if 'btn-fetch-jd' not in html[html.find('<script>'):]:
    html = html.replace('// ══════════════════════════════════════════\n        // SINGLE ANALYSIS', js_snippet + '\n        // ══════════════════════════════════════════\n        // SINGLE ANALYSIS')

with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated index.html successfully")
