"""
app/services/sms_sender.py
Sends SMS via Exotel transactional SMS API.
"""

import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead

logger = get_logger(__name__)


def _format_mobile_india(number: str) -> str:
    """Return 10-digit Indian mobile number."""
    cleaned = "".join(filter(str.isdigit, number))
    if cleaned.startswith("91") and len(cleaned) == 12:
        return cleaned[2:]
    return cleaned[-10:]


def _build_sms(lead: Lead) -> str:
    return (
        f"Hi {lead.buyer_name.split()[0] if lead.buyer_name else 'there'}, "
        f"we saw your IndiaMART enquiry for {lead.quantity} {lead.quantity_unit} "
        f"of {lead.product or 'medical supplies'}. "
        f"We can supply. WhatsApp/Call: {settings.company_phone}. "
        f"– {settings.company_name}"
    )[:160]   # keep within single SMS


async def send_sms(lead: Lead) -> str:
    """
    Send SMS via Exotel SMS API.
    Returns Exotel SmsSid on success, raises on failure.
    Docs: https://developer.exotel.com/api/sms
    """
    mobile = _format_mobile_india(lead.buyer_mobile)
    message = _build_sms(lead)

    url = (
        f"https://api.exotel.com/v1/Accounts/{settings.exotel_sid}"
        f"/Sms/send.json"
    )

    payload = {
        "From"  : settings.exotel_virtual_number,
        "To"    : mobile,
        "Body"  : message,
    }

    async with httpx.AsyncClient(
        auth=(settings.exotel_api_key, settings.exotel_api_token),
        timeout=15.0,
    ) as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        data = response.json()

        sms_sid = (
            data.get("SMSMessage", {}).get("Sid", "")
            or data.get("Sid", "")
        )
        logger.info(f"SMS sent → {mobile} | SmsSid={sms_sid}")
        return sms_sid
