import os

path = r"c:\Users\preet\New folder (10)\app\templates\dashboard.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Add Chart.js to head
if "chart.js" not in html:
    html = html.replace("</head>", '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>')

# Add charts container before the table card
charts_html = """
        <!-- Stats Overview -->
        <div class="stats-overview" style="display: flex; gap: 20px; margin-bottom: 24px;">
            <div class="card stat-card" style="flex: 1; text-align: center;">
                <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: 1px;">Total Resumes Analyzed</div>
                <div id="stat-total" style="font-size: 3rem; font-weight: 800; color: var(--text-dark); margin-top: 10px;">-</div>
            </div>
            <div class="card stat-card" style="flex: 1; text-align: center;">
                <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: 1px;">Avg Match Score</div>
                <div id="stat-avg" style="font-size: 3rem; font-weight: 800; color: var(--text-dark); margin-top: 10px;">-</div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div class="card" style="padding: 20px;">
                <h3 style="font-size: 1rem; color: var(--text-dark); margin-bottom: 16px;">Match Score Trend (Last 10)</h3>
                <canvas id="scoreChart" height="220"></canvas>
            </div>
            <div class="card" style="padding: 20px;">
                <h3 style="font-size: 1rem; color: var(--text-dark); margin-bottom: 16px;">Most Frequently Missing Skills</h3>
                <canvas id="skillsChart" height="220"></canvas>
            </div>
        </div>

        <h2 style="font-size: 1.4rem; color: var(--text-dark); font-weight: 800; margin-bottom: 16px;">All Candidates</h2>
"""

if 'class="stats-overview"' not in html:
    html = html.replace('<div class="card">\n            <table>', charts_html + '        <div class="card">\n            <table>')

# Add JS logic to fetch stats and render charts
js_code = """
        async function loadStats() {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) return;
                
                const response = await fetch('/api/dashboard/stats', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                
                if (!response.ok) return;
                const data = await response.json();
                
                document.getElementById('stat-total').textContent = data.total_analyzed;
                document.getElementById('stat-avg').textContent = data.avg_match_score;
                
                // Score Trend Chart
                const ctxScore = document.getElementById('scoreChart').getContext('2d');
                new Chart(ctxScore, {
                    type: 'line',
                    data: {
                        labels: data.score_history.map(d => d.date),
                        datasets: [{
                            label: 'Match Score',
                            data: data.score_history.map(d => d.score),
                            borderColor: '#a78bfa',
                            backgroundColor: 'rgba(167, 139, 250, 0.2)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: { y: { min: 0, max: 100 } }
                    }
                });

                // Missing Skills Chart
                const ctxSkills = document.getElementById('skillsChart').getContext('2d');
                new Chart(ctxSkills, {
                    type: 'bar',
                    data: {
                        labels: data.top_missing_skills.map(s => s.skill),
                        datasets: [{
                            label: 'Times Missing',
                            data: data.top_missing_skills.map(s => s.count),
                            backgroundColor: '#ff6b6b',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                    }
                });
                
            } catch (err) {
                console.error("Error loading stats", err);
            }
        }
"""

if 'loadStats()' not in html:
    html = html.replace("window.onload = loadCandidates;", "window.onload = function() { loadCandidates(); loadStats(); };")
    html = html.replace("async function loadCandidates() {", js_code + "\n        async function loadCandidates() {")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated dashboard.html successfully.")
