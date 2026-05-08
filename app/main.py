@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Phoenix Lead Bot Dashboard</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, Helvetica, sans-serif;
                background: #0b1120;
                color: #f8fafc;
            }

            .layout {
                display: flex;
                min-height: 100vh;
            }

            .sidebar {
                width: 260px;
                background: #111827;
                padding: 24px;
                border-right: 1px solid #1f2937;
                position: fixed;
                top: 0;
                bottom: 0;
                left: 0;
            }

            .brand {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 36px;
            }

            .brand-logo {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background: linear-gradient(135deg, #38bdf8, #22c55e);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
            }

            .brand-text h2 {
                margin: 0;
                font-size: 18px;
            }

            .brand-text p {
                margin: 3px 0 0;
                font-size: 12px;
                color: #94a3b8;
            }

            .nav button {
                width: 100%;
                display: block;
                margin-bottom: 12px;
                padding: 13px 14px;
                border: 1px solid #334155;
                border-radius: 10px;
                background: #1e293b;
                color: #e5e7eb;
                text-align: left;
                cursor: pointer;
                font-weight: bold;
            }

            .nav button:hover,
            .nav button.active {
                background: #2563eb;
                border-color: #60a5fa;
            }

            .side-footer {
                position: absolute;
                bottom: 24px;
                left: 24px;
                right: 24px;
                padding: 14px;
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
                font-size: 12px;
                color: #94a3b8;
            }

            .main {
                margin-left: 260px;
                padding: 32px;
                width: calc(100% - 260px);
            }

            .topbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 28px;
            }

            .topbar h1 {
                margin: 0;
                font-size: 34px;
            }

            .topbar p {
                margin: 8px 0 0;
                color: #94a3b8;
            }

            .actions {
                display: flex;
                gap: 10px;
            }

            .btn {
                padding: 12px 16px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
            }

            .btn-primary {
                background: #38bdf8;
                color: #020617;
            }

            .btn-dark {
                background: #1e293b;
                color: #e5e7eb;
                border: 1px solid #334155;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 18px;
                margin-bottom: 28px;
            }

            .card {
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            }

            .card h3 {
                margin: 0 0 12px;
                color: #cbd5e1;
                font-size: 14px;
            }

            .number {
                font-size: 34px;
                font-weight: bold;
                color: #38bdf8;
            }

            .muted {
                color: #94a3b8;
                font-size: 13px;
            }

            .section {
                display: none;
            }

            .section.active {
                display: block;
            }

            .section-title {
                margin: 30px 0 16px;
                font-size: 24px;
            }

            .two-col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 18px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: #111827;
                border-radius: 14px;
                overflow: hidden;
                border: 1px solid #1f2937;
            }

            th, td {
                padding: 14px;
                border-bottom: 1px solid #1f2937;
                text-align: left;
                font-size: 14px;
            }

            th {
                background: #1e293b;
                color: #e2e8f0;
            }

            td {
                color: #cbd5e1;
            }

            .status {
                padding: 5px 9px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: bold;
                background: #1d4ed8;
                color: white;
            }

            .notice {
                background: #082f49;
                border: 1px solid #0ea5e9;
                color: #bae6fd;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 16px;
            }

            .error {
                background: #450a0a;
                border: 1px solid #ef4444;
                color: #fecaca;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 16px;
                display: none;
            }

            .api-list a {
                color: #38bdf8;
                display: block;
                margin-bottom: 10px;
                text-decoration: none;
            }

            .api-list a:hover {
                text-decoration: underline;
            }

            @media (max-width: 1000px) {
                .sidebar {
                    position: relative;
                    width: 100%;
                    height: auto;
                }

                .layout {
                    display: block;
                }

                .main {
                    margin-left: 0;
                    width: 100%;
                }

                .grid {
                    grid-template-columns: 1fr 1fr;
                }

                .two-col {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 600px) {
                .grid {
                    grid-template-columns: 1fr;
                }

                .topbar {
                    display: block;
                }

                .actions {
                    margin-top: 18px;
                }
            }
        </style>
    </head>

    <body>
        <div class="layout">
            <aside class="sidebar">
                <div class="brand">
                    <div class="brand-logo">📊</div>
                    <div class="brand-text">
                        <h2>Phoenix Lead Bot</h2>
                        <p>IndiaMART Automation</p>
                    </div>
                </div>

                <div class="nav">
                    <button class="active" onclick="showSection('dashboard', this)">📊 Dashboard</button>
                    <button onclick="showSection('leads', this)">📋 Leads</button>
                    <button onclick="showSection('calls', this)">📞 Calls</button>
                    <button onclick="showSection('system', this)">⚙️ System</button>
                </div>

                <div class="side-footer">
                    <strong>Vercel API Mode</strong><br>
                    Poller disabled for serverless deployment.<br><br>
                    Last refresh: <span id="lastRefresh">Never</span>
                </div>
            </aside>

            <main class="main">
                <div class="topbar">
                    <div>
                        <h1>Lead Automation Dashboard</h1>
                        <p>Monitor leads, calls, outreach status, and system health.</p>
                    </div>

                    <div class="actions">
                        <button class="btn btn-primary" onclick="loadData()">Refresh Data</button>
                        <button class="btn btn-dark" onclick="window.open('/docs', '_blank')">API Docs</button>
                    </div>
                </div>

                <div id="errorBox" class="error"></div>

                <section id="dashboard" class="section active">
                    <div class="grid">
                        <div class="card">
                            <h3>Total Leads</h3>
                            <div class="number" id="totalLeads">0</div>
                            <div class="muted">All captured leads</div>
                        </div>

                        <div class="card">
                            <h3>New Leads</h3>
                            <div class="number" id="newLeads">0</div>
                            <div class="muted">Waiting for action</div>
                        </div>

                        <div class="card">
                            <h3>Engaged</h3>
                            <div class="number" id="engagedLeads">0</div>
                            <div class="muted">Contact started</div>
                        </div>

                        <div class="card">
                            <h3>Converted</h3>
                            <div class="number" id="convertedLeads">0</div>
                            <div class="muted">Won opportunities</div>
                        </div>

                        <div class="card">
                            <h3>Calls Tracked</h3>
                            <div class="number" id="totalCalls">0</div>
                            <div class="muted">Exotel call logs</div>
                        </div>
                    </div>

                    <div class="two-col">
                        <div class="card">
                            <h2 class="section-title">Lead Status Breakdown</h2>
                            <div id="leadBreakdown" class="notice">Loading lead status...</div>
                        </div>

                        <div class="card">
                            <h2 class="section-title">Outreach Performance</h2>
                            <div id="outreachBreakdown" class="notice">Loading outreach data...</div>
                        </div>
                    </div>
                </section>

                <section id="leads" class="section">
                    <h2 class="section-title">Lead Management</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Buyer</th>
                                <th>Mobile</th>
                                <th>Email</th>
                                <th>City</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Score</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="leadsTable">
                            <tr><td colspan="8">Loading...</td></tr>
                        </tbody>
                    </table>
                </section>

                <section id="calls" class="section">
                    <h2 class="section-title">Call Logs</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Caller</th>
                                <th>Direction</th>
                                <th>Status</th>
                                <th>Duration</th>
                                <th>Recording</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody id="callsTable">
                            <tr><td colspan="6">Loading...</td></tr>
                        </tbody>
                    </table>
                </section>

                <section id="system" class="section">
                    <h2 class="section-title">System Status</h2>

                    <div class="grid">
                        <div class="card">
                            <h3>API Status</h3>
                            <div class="number" id="apiStatus">-</div>
                        </div>

                        <div class="card">
                            <h3>Environment</h3>
                            <div class="number" id="appEnv">-</div>
                        </div>

                        <div class="card">
                            <h3>Scheduler</h3>
                            <div class="number" id="schedulerStatus">-</div>
                        </div>

                        <div class="card">
                            <h3>Poller Enabled</h3>
                            <div class="number" id="pollerStatus">-</div>
                        </div>

                        <div class="card">
                            <h3>Database</h3>
                            <div class="number">Ready</div>
                        </div>
                    </div>

                    <div class="card">
                        <h2 class="section-title">API Links</h2>
                        <div class="api-list">
                            <a href="/health" target="_blank">/health</a>
                            <a href="/docs" target="_blank">/docs</a>
                            <a href="/api/leads" target="_blank">/api/leads</a>
                            <a href="/api/stats" target="_blank">/api/stats</a>
                            <a href="/api/calls" target="_blank">/api/calls</a>
                            <a href="/webhook/call" target="_blank">/webhook/call</a>
                        </div>
                    </div>
                </section>
            </main>
        </div>

        <script>
            function showSection(sectionId, button) {
                document.querySelectorAll('.section').forEach(section => {
                    section.classList.remove('active');
                });

                document.querySelectorAll('.nav button').forEach(btn => {
                    btn.classList.remove('active');
                });

                document.getElementById(sectionId).classList.add('active');
                button.classList.add('active');
            }

            function showError(message) {
                const box = document.getElementById('errorBox');
                box.innerText = message;
                box.style.display = 'block';
            }

            function clearError() {
                const box = document.getElementById('errorBox');
                box.innerText = '';
                box.style.display = 'none';
            }

            function cleanStatus(status) {
                if (!status) return '-';
                return String(status).replace('LeadStatus.', '').replace('OutreachStatus.', '');
            }

            async function loadData() {
                clearError();

                try {
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();

                    const leadsRes = await fetch('/api/leads?page=1&size=100');
                    const leadsData = await leadsRes.json();

                    const callsRes = await fetch('/api/calls?page=1&size=100');
                    const callsData = await callsRes.json();

                    const healthRes = await fetch('/health');
                    const health = await healthRes.json();

                    const leads = leadsData.leads || [];
                    const calls = callsData.calls || [];

                    document.getElementById('totalLeads').innerText = leadsData.total || 0;
                    document.getElementById('totalCalls').innerText = callsData.total || 0;

                    let newCount = 0;
                    let engagedCount = 0;
                    let convertedCount = 0;

                    leads.forEach(lead => {
                        const status = cleanStatus(lead.status).toUpperCase();

                        if (status === 'NEW') newCount++;
                        if (status === 'ENGAGED') engagedCount++;
                        if (status === 'CONVERTED') convertedCount++;
                    });

                    document.getElementById('newLeads').innerText = newCount;
                    document.getElementById('engagedLeads').innerText = engagedCount;
                    document.getElementById('convertedLeads').innerText = convertedCount;

                    document.getElementById('apiStatus').innerText = health.status || '-';
                    document.getElementById('appEnv').innerText = health.env || '-';
                    document.getElementById('schedulerStatus').innerText = health.scheduler ? 'On' : 'Off';
                    document.getElementById('pollerStatus').innerText = health.poller_enabled ? 'On' : 'Off';

                    renderLeadBreakdown(stats.leads || {});
                    renderOutreachBreakdown(stats.outreach || []);
                    renderLeadsTable(leads);
                    renderCallsTable(calls);

                    document.getElementById('lastRefresh').innerText = new Date().toLocaleTimeString();
                } catch (error) {
                    showError('Dashboard failed to load data: ' + error.message);
                }
            }

            function renderLeadBreakdown(leadsStats) {
                const box = document.getElementById('leadBreakdown');
                const entries = Object.entries(leadsStats);

                if (entries.length === 0) {
                    box.innerHTML = 'No lead status data yet.';
                    return;
                }

                box.innerHTML = entries.map(([status, count]) => {
                    return `<div><strong>${cleanStatus(status)}</strong>: ${count}</div>`;
                }).join('');
            }

            function renderOutreachBreakdown(outreach) {
                const box = document.getElementById('outreachBreakdown');

                if (!outreach || outreach.length === 0) {
                    box.innerHTML = 'No outreach data yet.';
                    return;
                }

                box.innerHTML = outreach.map(item => {
                    return `<div><strong>${item.channel}</strong> ${cleanStatus(item.status)}: ${item.count}</div>`;
                }).join('');
            }

            function renderLeadsTable(leads) {
                const table = document.getElementById('leadsTable');
                table.innerHTML = '';

                if (!leads || leads.length === 0) {
                    table.innerHTML = '<tr><td colspan="8">No leads found.</td></tr>';
                    return;
                }

                leads.forEach(lead => {
                    table.innerHTML += `
                        <tr>
                            <td>${lead.buyer_name || '-'}</td>
                            <td>${lead.buyer_mobile || '-'}</td>
                            <td>${lead.buyer_email || '-'}</td>
                            <td>${lead.buyer_city || '-'}</td>
                            <td>${lead.product || '-'}</td>
                            <td>${lead.quantity || '-'}</td>
                            <td>${lead.quality_score || '-'}</td>
                            <td><span class="status">${cleanStatus(lead.status)}</span></td>
                        </tr>
                    `;
                });
            }

            function renderCallsTable(calls) {
                const table = document.getElementById('callsTable');
                table.innerHTML = '';

                if (!calls || calls.length === 0) {
                    table.innerHTML = '<tr><td colspan="6">No call logs found.</td></tr>';
                    return;
                }

                calls.forEach(call => {
                    const recording = call.recording_url
                        ? `<a href="${call.recording_url}" target="_blank" style="color:#38bdf8;">Open</a>`
                        : '-';

                    table.innerHTML += `
                        <tr>
                            <td>${call.caller || '-'}</td>
                            <td>${call.direction || '-'}</td>
                            <td>${call.status || '-'}</td>
                            <td>${call.duration_secs || 0}s</td>
                            <td>${recording}</td>
                            <td>${call.call_time || '-'}</td>
                        </tr>
                    `;
                });
            }

            loadData();
        </script>
    </body>
    </html>
    """