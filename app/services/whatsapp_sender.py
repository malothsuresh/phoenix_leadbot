"""
app/services/whatsapp_sender.py
Sends WhatsApp messages via 360dialog Cloud API.
Uses a template message for the first contact (required by Meta policy).
"""

import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead

logger = get_logger(__name__)

DIALOG360_API_URL = "https://waba.360dialog.io/v1/messages"


def _format_mobile(number: str) -> str:
    """
    Ensure number is E.164 format without '+'.
    IndiaMART numbers are typically 10-digit Indian numbers.
    """
    cleaned = "".join(filter(str.isdigit, number))
    if len(cleaned) == 10:
        return f"91{cleaned}"          # prepend India country code
    return cleaned


def _build_intro_message(lead: Lead) -> str:
    """Plain-text fallback message (used if template not approved yet)."""
    return (
        f"Hello {lead.buyer_name or 'there'},\n\n"
        f"Thank you for your enquiry about *{lead.product or 'medical supplies'}* "
        f"({lead.quantity} {lead.quantity_unit}) on IndiaMART.\n\n"
        f"We are *{settings.company_name}*, a trusted supplier of high-quality "
        f"medical consumables (Nitrile Gloves, Surgical Masks, PPE Kits).\n\n"
        f"✅ Bulk quantities available\n"
        f"✅ Competitive pricing\n"
        f"✅ Fast shipping\n"
        f"✅ ISO & CE certified products\n\n"
        f"Please reply here or call us at {settings.company_phone} to discuss your requirement.\n\n"
        f"Best regards,\n{settings.company_name}\n{settings.company_website}"
    )


async def send_whatsapp(lead: Lead) -> str:
    """
    Send WhatsApp intro message via 360dialog.
    Returns the message ID on success, raises on failure.
    """
    to_number = _format_mobile(lead.buyer_mobile)

    headers = {
        "D360-API-KEY": settings.dialog360_api_key,
        "Content-Type": "application/json",
    }

    # ── Attempt 1: Template message (required for new contacts) ──────────
    # Replace 'phoenix_intro' with your actual approved template name.
    # Template params: {{1}} = buyer_name, {{2}} = product, {{3}} = quantity
    template_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "phoenix_intro",           # ← your approved template name
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": lead.buyer_name or "there"},
                        {"type": "text", "text": lead.product or "medical supplies"},
                        {"type": "text", "text": str(lead.quantity)},
                    ],
                }
            ],
        },
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(DIALOG360_API_URL, json=template_payload, headers=headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            msg_id = data.get("messages", [{}])[0].get("id", "")
            logger.info(f"WhatsApp template sent → {to_number} | msg_id={msg_id}")
            return msg_id

        # ── Fallback: free-form text (only works within 24h session window) ──
        logger.warning(
            f"WhatsApp template failed ({resp.status_code}) — trying free-form. "
            f"Response: {resp.text[:200]}"
        )

        text_payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": _build_intro_message(lead)},
        }

        resp2 = await client.post(DIALOG360_API_URL, json=text_payload, headers=headers)
        resp2.raise_for_status()
        data2 = resp2.json()
        msg_id = data2.get("messages", [{}])[0].get("id", "")
        logger.info(f"WhatsApp free-form sent → {to_number} | msg_id={msg_id}")
        return msg_id
