"""
app/dashboard/streamlit_app.py
Admin dashboard for Phoenix Med Tech Lead Automation System.
Run: streamlit run app/dashboard/streamlit_app.py
"""

import os
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
DASH_USER = os.getenv("DASHBOARD_USERNAME", "admin")
DASH_PASS = os.getenv("DASHBOARD_PASSWORD", "password")

st.set_page_config(
    page_title="Phoenix Lead Bot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Simple Auth ───────────────────────────────────────────────────────────────
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Phoenix Lead Bot — Login")
        with st.form("login"):
            user = st.text_input("Username")
            pwd  = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if user == DASH_USER and pwd == DASH_PASS:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        st.stop()

check_auth()

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_stats():
    try:
        r = requests.get(f"{API_BASE}/api/stats", timeout=5)
        return r.json()
    except Exception:
        return {}

@st.cache_data(ttl=30)
def fetch_leads(page=1, size=50, status=None):
    params = {"page": page, "size": size}
    if status and status != "All":
        params["status"] = status.lower()
    try:
        r = requests.get(f"{API_BASE}/api/leads", params=params, timeout=5)
        return r.json()
    except Exception:
        return {"leads": [], "total": 0}

@st.cache_data(ttl=30)
def fetch_calls(page=1, size=50):
    try:
        r = requests.get(f"{API_BASE}/api/calls", params={"page": page, "size": size}, timeout=5)
        return r.json()
    except Exception:
        return {"calls": [], "total": 0}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=Phoenix+Med+Tech", use_column_width=True)
    st.markdown("---")
    page = st.radio("Navigate", ["📊 Dashboard", "📋 Leads", "📞 Calls", "⚙️ System"])
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ── Dashboard ─────────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Lead Automation Dashboard")
    stats = fetch_stats()
    lead_counts = stats.get("leads", {})
    call_data   = stats.get("calls", {})

    total_leads    = sum(lead_counts.values())
    engaged_leads  = lead_counts.get("engaged", 0)
    converted      = lead_counts.get("converted", 0)
    total_calls    = call_data.get("total", 0)
    conversion_pct = round(converted / total_leads * 100, 1) if total_leads else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Leads",   total_leads)
    col2.metric("Engaged",       engaged_leads)
    col3.metric("Converted",     converted)
    col4.metric("Conversion %",  f"{conversion_pct}%")
    col5.metric("Calls Tracked", total_calls)

    st.markdown("---")

    # Lead status breakdown
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Lead Status Breakdown")
        if lead_counts:
            df_status = pd.DataFrame(
                list(lead_counts.items()), columns=["Status", "Count"]
            ).set_index("Status")
            st.bar_chart(df_status)
        else:
            st.info("No lead data yet.")

    # Outreach channel performance
    with col_b:
        st.subheader("Outreach Performance")
        outreach = stats.get("outreach", [])
        if outreach:
            df_out = pd.DataFrame(outreach)
            pivot  = df_out.pivot_table(
                index="channel", columns="status", values="count", fill_value=0
            )
            st.dataframe(pivot, use_container_width=True)
        else:
            st.info("No outreach data yet.")

# ── Leads Table ───────────────────────────────────────────────────────────────
elif page == "📋 Leads":
    st.title("📋 Lead Management")

    col1, col2 = st.columns([1, 3])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "New", "Engaged", "Replied", "Converted", "Rejected", "Duplicate"],
        )
    with col2:
        st.write("")

    data = fetch_leads(status=status_filter)
    leads = data.get("leads", [])

    st.caption(f"Showing {len(leads)} of {data.get('total', 0)} leads")

    if leads:
        df = pd.DataFrame(leads)
        df["received_at"] = pd.to_datetime(df["received_at"]).dt.strftime("%d %b %Y %H:%M")
        df = df.rename(columns={
            "buyer_name"   : "Name",
            "buyer_mobile" : "Mobile",
            "buyer_email"  : "Email",
            "buyer_city"   : "City",
            "product"      : "Product",
            "quantity"     : "Qty",
            "quality_score": "Score",
            "status"       : "Status",
            "received_at"  : "Received At",
        })
        cols = ["Name", "Mobile", "City", "Product", "Qty", "Score", "Status", "Received At"]
        st.dataframe(df[cols], use_container_width=True, height=500)
    else:
        st.info("No leads found.")

# ── Calls ─────────────────────────────────────────────────────────────────────
elif page == "📞 Calls":
    st.title("📞 Call Logs")
    data  = fetch_calls()
    calls = data.get("calls", [])
    st.caption(f"Total calls tracked: {data.get('total', 0)}")

    if calls:
        df = pd.DataFrame(calls)
        df["call_time"] = pd.to_datetime(df["call_time"]).dt.strftime("%d %b %Y %H:%M")
        df["duration"]  = df["duration_secs"].apply(
            lambda s: f"{s//60}m {s%60}s" if s else "—"
        )
        cols = ["caller", "direction", "status", "duration", "call_time"]
        st.dataframe(df[cols], use_container_width=True, height=500)
    else:
        st.info("No calls logged yet.")

# ── System ────────────────────────────────────────────────────────────────────
elif page == "⚙️ System":
    st.title("⚙️ System Status")
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        health = r.json()
        if health.get("status") == "ok":
            st.success("✅ API server is running")
        else:
            st.error("❌ API server returned non-ok status")
        st.json(health)
    except Exception as e:
        st.error(f"❌ Cannot reach API server: {e}")

    st.markdown("---")
    st.subheader("Configuration")
    st.info("Sensitive credentials are hidden. Check your .env file.")
    cfg = {
        "Poll Interval"  : f"{os.getenv('POLL_INTERVAL_SECONDS', 60)}s",
        "Min Quantity"   : f"{os.getenv('LEAD_MIN_QUANTITY', 300)} boxes",
        "Environment"    : os.getenv("APP_ENV", "production"),
        "AWS Region"     : os.getenv("AWS_REGION", "—"),
    }
    st.json(cfg)
