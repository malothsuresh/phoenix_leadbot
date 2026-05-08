"""
app/services/call_tracker.py
Handles Exotel inbound call webhooks.
Exotel hits your /webhook/call endpoint on every call event.
"""

from sqlalchemy.orm import Session
from app.core.logger import get_logger
from app.models.database import CallLog, CallDirection, Lead, SessionLocal

logger = get_logger(__name__)


async def handle_call_event(payload: dict, db: Session):
    """
    Process an Exotel call webhook payload.
    Exotel POST fields: CallSid, From, To, Direction, Status,
                        RecordingUrl, Duration, StartTime
    """
    call_sid     = payload.get("CallSid", "")
    caller       = payload.get("From", "")
    virtual_num  = payload.get("To", "")
    direction_raw= payload.get("Direction", "inbound").lower()
    status       = payload.get("Status", "")
    duration     = int(payload.get("Duration", 0) or 0)
    recording    = payload.get("RecordingUrl", "")

    direction = (
        CallDirection.INBOUND
        if "inbound" in direction_raw
        else CallDirection.OUTBOUND
    )

    # Try to match caller to an existing lead
    lead_id = None
    if caller:
        mobile_digits = "".join(filter(str.isdigit, caller))[-10:]
        lead = (
            db.query(Lead)
            .filter(Lead.buyer_mobile.like(f"%{mobile_digits}%"))
            .order_by(Lead.received_at.desc())
            .first()
        )
        if lead:
            lead_id = lead.id
            logger.info(f"Call from {caller} matched to lead {lead.indiamart_id}")

    # Upsert call log (update if same CallSid already exists)
    existing = db.query(CallLog).filter_by(exotel_call_sid=call_sid).first()
    if existing:
        existing.status        = status
        existing.duration_secs = duration
        existing.recording_url = recording
        db.commit()
        logger.info(f"Call log updated | CallSid={call_sid} | status={status}")
    else:
        log = CallLog(
            lead_id         = lead_id,
            exotel_call_sid = call_sid,
            direction       = direction,
            caller_number   = caller,
            virtual_number  = virtual_num,
            duration_secs   = duration,
            status          = status,
            recording_url   = recording,
        )
        db.add(log)
        db.commit()
        logger.info(
            f"Call logged | CallSid={call_sid} | {caller} → {virtual_num} | "
            f"status={status} | duration={duration}s"
        )
