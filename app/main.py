@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phoenix Lead Bot Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                margin: 0;
                padding: 30px;
            }
            h1 {
                font-size: 36px;
                margin-bottom: 10px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-top: 30px;
            }
            .card {
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            }
            .number {
                font-size: 34px;
                font-weight: bold;
                color: #38bdf8;
            }
            table {
                width: 100%;
                margin-top: 30px;
                border-collapse: collapse;
                background: #1e293b;
                border-radius: 12px;
                overflow: hidden;
            }
            th, td {
                padding: 14px;
                border-bottom: 1px solid #334155;
                text-align: left;
            }
            th {
                background: #334155;
            }
            .btn {
                margin-top: 20px;
                padding: 12px 18px;
                background: #38bdf8;
                color: #020617;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>📊 Phoenix Lead Automation Dashboard</h1>
        <p>Live Vercel dashboard for API testing.</p>

        <button class="btn" onclick="loadData()">Refresh Data</button>

        <div class="grid">
            <div class="card">
                <h3>Total Leads</h3>
                <div class="number" id="totalLeads">0</div>
            </div>
            <div class="card">
                <h3>Calls Tracked</h3>
                <div class="number" id="totalCalls">0</div>
            </div>
            <div class="card">
                <h3>Total Call Duration</h3>
                <div class="number" id="callDuration">0s</div>
            </div>
            <div class="card">
                <h3>System</h3>
                <div class="number">Online</div>
            </div>
        </div>

        <h2>Leads</h2>
        <table>
            <thead>
                <tr>
                    <th>Buyer</th>
                    <th>Mobile</th>
                    <th>City</th>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="leadsTable">
                <tr><td colspan="6">Loading...</td></tr>
            </tbody>
        </table>

        <script>
            async function loadData() {
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();

                const leadsRes = await fetch('/api/leads?page=1&size=50');
                const leadsData = await leadsRes.json();

                document.getElementById('totalLeads').innerText = leadsData.total || 0;
                document.getElementById('totalCalls').innerText = stats.calls.total || 0;
                document.getElementById('callDuration').innerText = (stats.calls.total_duration_s || 0) + 's';

                const table = document.getElementById('leadsTable');
                table.innerHTML = '';

                if (!leadsData.leads || leadsData.leads.length === 0) {
                    table.innerHTML = '<tr><td colspan="6">No leads found.</td></tr>';
                    return;
                }

                leadsData.leads.forEach(lead => {
                    table.innerHTML += `
                        <tr>
                            <td>${lead.buyer_name || '-'}</td>
                            <td>${lead.buyer_mobile || '-'}</td>
                            <td>${lead.buyer_city || '-'}</td>
                            <td>${lead.product || '-'}</td>
                            <td>${lead.quantity || '-'}</td>
                            <td>${lead.status || '-'}</td>
                        </tr>
                    `;
                });
            }

            loadData();
        </script>
    </body>
    </html>
    """