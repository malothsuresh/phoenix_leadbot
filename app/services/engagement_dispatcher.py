"""
app/services/engagement_dispatcher.py
Orchestrates multi-channel outreach for a qualifying lead.
Order: WhatsApp → Email → SMS (all attempted even if one fails)
"""

import asyncio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead, LeadStatus, OutreachLog, OutreachChannel, OutreachStatus
from app.services.whatsapp_sender import send_whatsapp
from app.services.email_sender import send_email
from app.services.sms_sender import send_sms

logger = get_logger(__name__)


def _log_outreach(
    db: Session,
    lead: Lead,
    channel: OutreachChannel,
    status: OutreachStatus,
    recipient: str,
    message_id: str = "",
    error: str = "",
):
    log = OutreachLog(
        lead_id    = lead.id,
        channel    = channel,
        status     = status,
        recipient  = recipient,
        message_id = message_id,
        error      = error,
    )
    db.add(log)
    db.commit()


async def dispatch_lead(lead: Lead, db: Session):
    """
    Fire all three channels for a qualifying lead.
    Updates lead status to ENGAGED if at least one channel succeeds.
    """
    logger.info(
        f"Dispatching lead {lead.indiamart_id} | "
        f"{lead.buyer_name} | qty={lead.quantity} | score={lead.quality_score}"
    )

    results = await asyncio.gather(
        _try_whatsapp(lead, db),
        _try_email(lead, db),
        _try_sms(lead, db),
        return_exceptions=True,
    )

    any_success = any(r is True for r in results)

    lead.status = LeadStatus.ENGAGED if any_success else LeadStatus.NEW
    db.commit()

    if any_success:
        logger.info(f"Lead {lead.indiamart_id} engaged successfully via at least one channel.")
    else:
        logger.warning(f"Lead {lead.indiamart_id} — all channels failed.")


async def _try_whatsapp(lead: Lead, db: Session) -> bool:
    if not lead.buyer_mobile:
        logger.info(f"Lead {lead.indiamart_id} has no mobile — WhatsApp skipped.")
        return False
    try:
        msg_id = await send_whatsapp(lead)
        _log_outreach(db, lead, OutreachChannel.WHATSAPP, OutreachStatus.SENT, lead.buyer_mobile, message_id=msg_id)
        return True
    except Exception as e:
        logger.error(f"WhatsApp failed for {lead.indiamart_id}: {e}")
        _log_outreach(db, lead, OutreachChannel.WHATSAPP, OutreachStatus.FAILED, lead.buyer_mobile, error=str(e))
        return False


async def _try_email(lead: Lead, db: Session) -> bool:
    if not lead.buyer_email:
        logger.info(f"Lead {lead.indiamart_id} has no email — Email skipped.")
        return False
    try:
        msg_id = await send_email(lead)
        _log_outreach(db, lead, OutreachChannel.EMAIL, OutreachStatus.SENT, lead.buyer_email, message_id=msg_id)
        return True
    except Exception as e:
        logger.error(f"Email failed for {lead.indiamart_id}: {e}")
        _log_outreach(db, lead, OutreachChannel.EMAIL, OutreachStatus.FAILED, lead.buyer_email, error=str(e))
        return False


async def _try_sms(lead: Lead, db: Session) -> bool:
    if not lead.buyer_mobile:
        logger.info(f"Lead {lead.indiamart_id} has no mobile — SMS skipped.")
        return False
    try:
        msg_id = await send_sms(lead)
        _log_outreach(db, lead, OutreachChannel.SMS, OutreachStatus.SENT, lead.buyer_mobile, message_id=msg_id)
        return True
    except Exception as e:
        logger.error(f"SMS failed for {lead.indiamart_id}: {e}")
        _log_outreach(db, lead, OutreachChannel.SMS, OutreachStatus.FAILED, lead.buyer_mobile, error=str(e))
        return False
