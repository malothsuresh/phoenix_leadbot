"""
app/main.py
FastAPI application entry point.
Starts the APScheduler polling loop locally and exposes:
  GET  /                 — root status
  GET  /health           — liveness probe
  POST /webhook/call     — Exotel call event webhook
  GET  /api/leads        — paginated lead list
  GET  /api/stats        — summary statistics
  GET  /api/calls        — call logs
"""

import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import (
    init_db, get_db, Lead, LeadStatus,
    OutreachLog, CallLog, SystemHealth
)
from app.services.indiamart_poller import poll_and_process
from app.services.call_tracker import handle_call_event

logger = get_logger(__name__)

# ── Scheduler ────────────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler(timezone="Asia/Kuala_Lumpur")

# For Vercel/serverless, set ENABLE_POLLER=false
ENABLE_POLLER = os.getenv("ENABLE_POLLER", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Phoenix Lead Bot starting up…")
    init_db()
    logger.info("✅ Database tables verified.")

    if ENABLE_POLLER:
        scheduler.add_job(
            poll_and_process,
            trigger="interval",
            seconds=settings.poll_interval_seconds,
            id="indiamart_poller",
            replace_existing=True,
            max_instances=1,
        )
        scheduler.start()
        logger.info(f"✅ Poller scheduled every {settings.poll_interval_seconds}s.")
    else:
        logger.info("IndiaMART poller disabled for serverless deployment.")

    yield

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("🛑 Scheduler shut down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Phoenix Med Tech – Lead Automation System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
def root():
    return {
        "status": "ok",
        "message": "Phoenix Lead Bot API is running",
        "docs": "/docs",
        "health": "/health",
    }


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "env": settings.app_env,
        "scheduler": scheduler.running,
        "poller_enabled": ENABLE_POLLER,
    }


# ── Exotel Webhook ────────────────────────────────────────────────────────────
@app.post("/webhook/call", tags=["Webhooks"])
async def call_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Exotel posts call events here.
    Configure this URL in your Exotel app settings:
    https://your-server.com/webhook/call
    """
    payload = await request.form()
    data = dict(payload)
    logger.info(f"Exotel webhook received: {data}")
    await handle_call_event(data, db)
    return JSONResponse({"status": "ok"})


# ── REST API ─────────────────────────────────────────────────────────────────
@app.get("/api/leads", tags=["Leads"])
def get_leads(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Lead).order_by(desc(Lead.received_at))

    if status:
        try:
            query = query.filter(Lead.status == LeadStatus(status))
        except ValueError:
            raise HTTPException(400, f"Invalid status '{status}'")

    total = query.count()
    leads = query.offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "leads": [
            {
                "id": str(l.id),
                "indiamart_id": l.indiamart_id,
                "buyer_name": l.buyer_name,
                "buyer_mobile": l.buyer_mobile,
                "buyer_email": l.buyer_email,
                "buyer_city": l.buyer_city,
                "product": l.product,
                "quantity": l.quantity,
                "quality_score": l.quality_score,
                "status": l.status,
                "received_at": l.received_at.isoformat() if l.received_at else None,
            }
            for l in leads
        ],
    }


@app.get("/api/stats", tags=["Leads"])
def get_stats(db: Session = Depends(get_db)):
    status_counts = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )

    outreach_counts = (
        db.query(OutreachLog.channel, OutreachLog.status, func.count(OutreachLog.id))
        .group_by(OutreachLog.channel, OutreachLog.status)
        .all()
    )

    call_stats = db.query(
        func.count(CallLog.id),
        func.sum(CallLog.duration_secs),
    ).first()

    return {
        "leads": {str(s): c for s, c in status_counts},
        "outreach": [
            {"channel": str(ch), "status": str(st), "count": c}
            for ch, st, c in outreach_counts
        ],
        "calls": {
            "total": call_stats[0] or 0,
            "total_duration_s": int(call_stats[1] or 0),
        },
    }


@app.get("/api/calls", tags=["Calls"])
def get_calls(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(CallLog).count()
    calls = (
        db.query(CallLog)
        .order_by(desc(CallLog.call_time))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "calls": [
            {
                "id": str(c.id),
                "caller": c.caller_number,
                "direction": c.direction,
                "status": c.status,
                "duration_secs": c.duration_secs,
                "recording_url": c.recording_url,
                "call_time": c.call_time.isoformat() if c.call_time else None,
            }
            for c in calls
        ],
    }