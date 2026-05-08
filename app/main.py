@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Phoenix Lead Bot Dashboard</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
        }
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 240px;
            background: #111827;
            padding: 24px;
            border-right: 1px solid #334155;
        }
        .main {
            margin-left: 260px;
            padding: 32px;
        }
        h1 {
            font-size: 34px;
            margin-bottom: 6px;
        }
        .muted {
            color: #94a3b8;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-top: 28px;
            margin-bottom: 28px;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px;
        }
        .number {
            font-size: 34px;
            color: #38bdf8;
            font-weight: bold;
        }
        .btn {
            padding: 12px 16px;
            background: #38bdf8;
            color: #020617;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 8px;
        }
        .nav button {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            background: #1e293b;
            color: white;
            border: 1px solid #334155;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
        }
        .nav button:hover {
            background: #2563eb;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 18px;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #334155;
            text-align: left;
        }
        th {
            background: #334155;
        }
        a {
            color: #38bdf8;
        }
        .section {
            display: none;
        }
        .section.active {
            display: block;
        }
        .error {
            display: none;
            background: #7f1d1d;
            color: #fecaca;
            padding: 14px;
            border-radius: 10px;
            margin-top: 16px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Phoenix Lead Bot</h2>
        <p class="muted">Vercel Dashboard</p>

        <div class="nav">
            <button onclick="showSection('dashboard')">Dashboard</button>
            <button onclick="showSection('leads')">Leads</button>
            <button onclick="showSection('calls')">Calls</button>
            <button onclick="showSection('system')">System</button>
        </div>

        <p class="muted">Poller disabled on Vercel.</p>
        <p class="muted">Last refresh: <span id="lastRefresh">Never</span></p>
    </div>

    <div class="main">
        <h1>Lead Automation Dashboard</h1>
        <p class="muted">Phoenix Med Tech lead automation API dashboard.</p>

        <button class="btn" onclick="loadData()">Refresh Data</button>
        <button class="btn" onclick="window.open('/docs', '_blank')">API Docs</button>

        <div id="errorBox" class="error"></div>

        <div id="dashboard" class="section active">
            <div class="grid">
                <div class="card">
                    <h3>Total Leads</h3>
                    <div class="number" id="totalLeads">0</div>
                </div>
                <div class="card">
                    <h3>New Leads</h3>
                    <div class="number" id="newLeads">0</div>
                </div>
                <div class="card">
                    <h3>Calls Tracked</h3>
                    <div class="number" id="totalCalls">0</div>
                </div>
                <div class="card">
                    <h3>System</h3>
                    <div class="number" id="apiStatus">-</div>
                </div>
            </div>
        </div>

        <div id="leads" class="section">
            <h2>Lead Management</h2>
            <table>
                <thead>
                    <tr>
                        <th>Buyer</th>
                        <th>Mobile</th>
                        <th>Email</th>
                        <th>City</th>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="leadsTable">
                    <tr><td colspan="7">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="calls" class="section">
            <h2>Call Logs</h2>
            <table>
                <thead>
                    <tr>
                        <th>Caller</th>
                        <th>Direction</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="callsTable">
                    <tr><td colspan="5">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="system" class="section">
            <h2>System Status</h2>
            <div class="grid">
                <div class="card">
                    <h3>Environment</h3>
                    <div class="number" id="appEnv">-</div>
                </div>
                <div class="card">
                    <h3>Scheduler</h3>
                    <div class="number" id="schedulerStatus">-</div>
                </div>
                <div class="card">
                    <h3>Poller</h3>
                    <div class="number" id="pollerStatus">-</div>
                </div>
                <div class="card">
                    <h3>Docs</h3>
                    <p><a href="/docs" target="_blank">Open API Docs</a></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showSection(id) {
            var sections = document.querySelectorAll('.section');
            for (var i = 0; i < sections.length; i++) {
                sections[i].classList.remove('active');
            }
            document.getElementById(id).classList.add('active');
        }

        function showError(message) {
            var box = document.getElementById('errorBox');
            box.innerText = message;
            box.style.display = 'block';
        }

        function cleanStatus(status) {
            if (!status) return '-';
            return String(status).replace('LeadStatus.', '').replace('OutreachStatus.', '');
        }

        async function loadData() {
            try {
                document.getElementById('errorBox').style.display = 'none';

                var statsRes = await fetch('/api/stats');
                var stats = await statsRes.json();

                var leadsRes = await fetch('/api/leads?page=1&size=100');
                var leadsData = await leadsRes.json();

                var callsRes = await fetch('/api/calls?page=1&size=100');
                var callsData = await callsRes.json();

                var healthRes = await fetch('/health');
                var health = await healthRes.json();

                var leads = leadsData.leads || [];
                var calls = callsData.calls || [];

                document.getElementById('totalLeads').innerText = leadsData.total || 0;
                document.getElementById('totalCalls').innerText = callsData.total || 0;
                document.getElementById('apiStatus').innerText = health.status || '-';
                document.getElementById('appEnv').innerText = health.env || '-';
                document.getElementById('schedulerStatus').innerText = health.scheduler ? 'On' : 'Off';
                document.getElementById('pollerStatus').innerText = health.poller_enabled ? 'On' : 'Off';

                var newCount = 0;
                for (var i = 0; i < leads.length; i++) {
                    if (cleanStatus(leads[i].status).toUpperCase() === 'NEW') {
                        newCount++;
                    }
                }
                document.getElementById('newLeads').innerText = newCount;

                var leadsTable = document.getElementById('leadsTable');
                leadsTable.innerHTML = '';

                if (leads.length === 0) {
                    leadsTable.innerHTML = '<tr><td colspan="7">No leads found.</td></tr>';
                } else {
                    for (var j = 0; j < leads.length; j++) {
                        var lead = leads[j];
                        leadsTable.innerHTML += '<tr>' +
                            '<td>' + (lead.buyer_name || '-') + '</td>' +
                            '<td>' + (lead.buyer_mobile || '-') + '</td>' +
                            '<td>' + (lead.buyer_email || '-') + '</td>' +
                            '<td>' + (lead.buyer_city || '-') + '</td>' +
                            '<td>' + (lead.product || '-') + '</td>' +
                            '<td>' + (lead.quantity || '-') + '</td>' +
                            '<td>' + cleanStatus(lead.status) + '</td>' +
                            '</tr>';
                    }
                }

                var callsTable = document.getElementById('callsTable');
                callsTable.innerHTML = '';

                if (calls.length === 0) {
                    callsTable.innerHTML = '<tr><td colspan="5">No call logs found.</td></tr>';
                } else {
                    for (var k = 0; k < calls.length; k++) {
                        var call = calls[k];
                        callsTable.innerHTML += '<tr>' +
                            '<td>' + (call.caller || '-') + '</td>' +
                            '<td>' + (call.direction || '-') + '</td>' +
                            '<td>' + (call.status || '-') + '</td>' +
                            '<td>' + (call.duration_secs || 0) + 's</td>' +
                            '<td>' + (call.call_time || '-') + '</td>' +
                            '</tr>';
                    }
                }

                document.getElementById('lastRefresh').innerText = new Date().toLocaleTimeString();
            } catch (error) {
                showError('Dashboard failed to load data: ' + error.message);
            }
        }

        loadData();
    </script>
</body>
</html>
    """