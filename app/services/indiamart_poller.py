"""
app/services/indiamart_poller.py
Polls IndiaMART Lead Manager API every N seconds, deduplicates,
scores, and dispatches qualifying leads into the engagement pipeline.
"""

import json
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead, LeadStatus, SessionLocal
from app.services.lead_filter import score_lead, is_qualifying
from app.services.engagement_dispatcher import dispatch_lead

logger = get_logger(__name__)

# IndiaMART Lead Manager API endpoint
INDIAMART_API_URL = "https://mapi.indiamart.com/wservce/crm/crmListing/v2/"


async def fetch_leads_from_api() -> list[dict]:
    """
    Fetch latest leads from IndiaMART Lead Manager API.
    Returns list of raw lead dicts.
    """
    params = {
        "glusr_usr_key": settings.indiamart_api_key,
        "start_time": (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y %H:%M:%S"),
        "end_time": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(INDIAMART_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # IndiaMART returns {"STATUS": 1, "RESPONSE_DATA": [...]}
            if data.get("STATUS") != 1:
                logger.warning(f"IndiaMART API non-success status: {data.get('STATUS')} | {data.get('MESSAGE')}")
                return []

            leads = data.get("RESPONSE_DATA", [])
            logger.info(f"IndiaMART API returned {len(leads)} leads")
            return leads

    except httpx.HTTPStatusError as e:
        logger.error(f"IndiaMART API HTTP error: {e.response.status_code} – {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"IndiaMART API fetch failed: {e}")
        return []


def parse_quantity(qty_str: str) -> int:
    """Extract integer quantity from strings like '500 Boxes', '1000', '2K'."""
    if not qty_str:
        return 0
    cleaned = str(qty_str).lower().replace(",", "").strip()
    multiplier = 1
    if cleaned.endswith("k"):
        multiplier = 1000
        cleaned = cleaned[:-1]
    try:
        return int(float(cleaned.split()[0]) * multiplier)
    except (ValueError, IndexError):
        return 0


def map_lead(raw: dict) -> dict:
    """
    Map IndiaMART API response fields to our internal lead schema.
    Field names based on IndiaMART Lead Manager API v2 docs.
    """
    return {
        "indiamart_id"  : str(raw.get("UNIQUE_QUERY_ID", "")),
        "buyer_name"    : raw.get("SENDER_NAME", "").strip(),
        "buyer_mobile"  : raw.get("SENDER_MOBILE", "").strip(),
        "buyer_email"   : raw.get("SENDER_EMAIL", "").strip(),
        "buyer_city"    : raw.get("SENDER_CITY", "").strip(),
        "buyer_state"   : raw.get("SENDER_STATE", "").strip(),
        "buyer_country" : raw.get("SENDER_COUNTRY_ISO", "IN"),
        "product"       : raw.get("SUBJECT", "").strip(),
        "quantity"      : parse_quantity(raw.get("QUERY_PRODUCT_QUANTITY", "0")),
        "quantity_unit" : raw.get("QUERY_PRODUCT_UNIT", "Boxes"),
        "requirement"   : raw.get("QUERY_MESSAGE", "").strip(),
        "raw_payload"   : json.dumps(raw),
    }


def save_lead(db: Session, mapped: dict) -> Lead | None:
    """
    Persist a lead to the database.
    Returns the Lead object, or None if it already existed (duplicate).
    """
    existing = db.query(Lead).filter_by(indiamart_id=mapped["indiamart_id"]).first()
    if existing:
        logger.debug(f"Duplicate lead skipped: {mapped['indiamart_id']}")
        return None

    lead = Lead(**mapped)
    lead.quality_score = score_lead(mapped)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    logger.info(
        f"New lead saved | ID:{lead.indiamart_id} | "
        f"{lead.buyer_name} | Qty:{lead.quantity} | Score:{lead.quality_score:.1f}"
    )
    return lead


async def poll_and_process():
    """
    Main poll cycle — called by the APScheduler job every N seconds.
    Fetch → Parse → Deduplicate → Score → Filter → Dispatch
    """
    logger.info("── Poll cycle started ──")
    raw_leads = await fetch_leads_from_api()

    if not raw_leads:
        logger.info("No new leads this cycle.")
        return

    db: Session = SessionLocal()
    dispatched = 0
    skipped    = 0

    try:
        for raw in raw_leads:
            mapped = map_lead(raw)

            if not mapped["indiamart_id"]:
                logger.warning("Lead missing UNIQUE_QUERY_ID — skipped.")
                continue

            lead = save_lead(db, mapped)
            if lead is None:
                skipped += 1
                continue

            if is_qualifying(lead):
                await dispatch_lead(lead, db)
                dispatched += 1
            else:
                logger.info(
                    f"Lead {lead.indiamart_id} did not qualify "
                    f"(qty={lead.quantity}, score={lead.quality_score:.1f}) — no outreach."
                )
                lead.status = LeadStatus.REJECTED
                db.commit()

    except Exception as e:
        logger.error(f"Error in poll cycle: {e}", exc_info=True)
    finally:
        db.close()

    logger.info(
        f"── Poll cycle complete | {len(raw_leads)} fetched | "
        f"{dispatched} dispatched | {skipped} duplicates ──"
    )
