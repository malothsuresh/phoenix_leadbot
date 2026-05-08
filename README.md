# Phoenix Med Tech — Automated Lead Capture & Engagement System

## Architecture Overview

```
IndiaMART API
     │  (poll every 60s)
     ▼
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
│                                                     │
│  APScheduler ──► Poller ──► Filter ──► Dispatcher  │
│                                  │                   │
│                            ┌─────┼──────┐           │
│                            ▼     ▼      ▼           │
│                         WA    Email   SMS            │
│                       360dlg  AWSSES  Exotel         │
│                                                     │
│  POST /webhook/call ──► Call Tracker                │
│                                                     │
│  All data ──────────────────────────────► PostgreSQL│
└─────────────────────────────────────────────────────┘
     │
     ▼
Streamlit Dashboard (port 8501)
```

---

## Quick Start (Local Development)

### 1. Clone / copy project
```bash
cd phoenix_leadbot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Open .env and fill in all your API keys
nano .env
```

### 5. Start the API server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start the dashboard (separate terminal)
```bash
streamlit run app/dashboard/streamlit_app.py
```

Visit: http://localhost:8501

---

## Production Deployment (AWS EC2 / DigitalOcean)

### Server Requirements
- Ubuntu 22.04 LTS
- 1 CPU, 1GB RAM minimum (2GB recommended)
- Docker + Docker Compose installed

### Steps

**1. Install Docker on Ubuntu**
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

**2. Upload project to server**
```bash
scp -r phoenix_leadbot/ ubuntu@YOUR_SERVER_IP:~/
```

**3. Set up environment**
```bash
cd ~/phoenix_leadbot
cp .env.example .env
nano .env    # fill in all keys
```

**4. Launch**
```bash
docker compose up -d --build
```

**5. Verify**
```bash
docker compose ps
curl http://localhost:8000/health
```

**6. View logs**
```bash
docker compose logs -f leadbot
```

---

## Exotel Webhook Configuration

In your Exotel dashboard:
1. Go to **Apps → My Apps**
2. Edit your virtual number app
3. Set **Passthru URL** (for all inbound calls) to:
   ```
   https://your-server.com/webhook/call
   ```
4. Method: **POST**

---

## IndiaMART API Setup

1. Login to IndiaMART seller panel
2. Go to **Settings → API Access**
3. Enable **Lead Manager API**
4. Copy your API key to `.env` → `INDIAMART_API_KEY`
5. Set `INDIAMART_MOBILE` to your registered seller mobile

**API Documentation:** https://seller.indiamart.com/lmsapi/

---

## 360dialog WhatsApp Template

Before going live, you must get a WhatsApp message template approved by Meta.

Suggested template name: `phoenix_intro`

Template body:
```
Hello {{1}},

Thank you for your enquiry about {{2}} ({{3}} boxes) on IndiaMART.

We are Phoenix Med Tech, a certified supplier of medical consumables.

✅ Bulk stock available
✅ CE & ISO certified
✅ Fast dispatch

Please reply here or call us to discuss pricing.

– Phoenix Med Tech Team
```

Submit via your 360dialog dashboard → **Templates → New Template**

While awaiting approval, the system will fall back to free-form messages (works within 24h session window).

---

## AWS SES Setup

1. Verify your sender domain in AWS SES
2. If your account is in **sandbox**, verify recipient emails too
3. Request **production access** to send to any address
4. Ensure your IAM user has `ses:SendEmail` permission

---

## File Structure

```
phoenix_leadbot/
├── app/
│   ├── core/
│   │   ├── config.py          # All settings from .env
│   │   └── logger.py          # Structured logging
│   ├── models/
│   │   └── database.py        # SQLAlchemy models + DB init
│   ├── services/
│   │   ├── indiamart_poller.py    # API polling + parsing
│   │   ├── lead_filter.py         # Scoring + qualification
│   │   ├── engagement_dispatcher.py # Orchestration
│   │   ├── whatsapp_sender.py     # 360dialog
│   │   ├── email_sender.py        # AWS SES
│   │   ├── sms_sender.py          # Exotel SMS
│   │   └── call_tracker.py        # Exotel webhook handler
│   ├── dashboard/
│   │   └── streamlit_app.py   # Admin UI
│   └── main.py                # FastAPI app + scheduler
├── deployment/
│   └── nginx.conf             # Reverse proxy config
├── .env.example               # Config template
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Lead Quality Scoring

| Factor | Points |
|--------|--------|
| Quantity ≥ 10,000 | 40 |
| Quantity ≥ 5,000 | 32 |
| Quantity ≥ 2,000 | 25 |
| Quantity ≥ 1,000 | 18 |
| Quantity ≥ 500 | 12 |
| Quantity ≥ 300 | 8 |
| Has email | 10 |
| Has mobile | 15 |
| Detailed requirement (>200 chars) | 20 |
| High-intent keywords (urgent, bulk, hospital…) | +3 each (max 15) |
| Low-intent keywords (price only, sample…) | −5 each |

Minimum to qualify: **Quantity ≥ 300 AND Score ≥ 10**

---

## Monitoring

- **Health endpoint:** `GET /health`
- **Logs:** `docker compose logs -f leadbot`
- **Dashboard:** `http://your-server:8501`

Set up a free uptime monitor (e.g. UptimeRobot) pinging `/health` every 5 minutes.

---

## Support

For questions about this system, refer to the source code comments or the project assignment document.
