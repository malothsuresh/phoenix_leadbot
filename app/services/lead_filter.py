"""
app/services/lead_filter.py
Lead quality scoring (0–100) and qualification gate.

Score breakdown:
  Quantity      : 0-40 pts
  Has email     : 10 pts
  Has mobile    : 15 pts
  Requirement   : 0-20 pts (detail length)
  Keywords      : 0-15 pts (urgency / medical keywords)
"""

import re
from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead

logger = get_logger(__name__)

# Keywords that suggest serious purchase intent
HIGH_INTENT_KEYWORDS = [
    "urgent", "immediately", "asap", "bulk", "regular",
    "monthly", "contract", "hospital", "clinic", "medical",
    "nitrile", "surgical", "disposable", "sterile", "iso",
    "ce certified", "fda", "export", "wholesale",
]

LOW_INTENT_KEYWORDS = [
    "price only", "just checking", "sample", "catalogue",
    "brochure", "inquiry only", "for knowledge",
]


def score_lead(mapped: dict) -> float:
    """Return a quality score 0–100 for a mapped lead dict."""
    score = 0.0
    quantity = mapped.get("quantity", 0)
    requirement = (mapped.get("requirement") or "").lower()

    # ── Quantity (0–40 pts) ───────────────────────────────────────────────
    if quantity >= 10_000:
        score += 40
    elif quantity >= 5_000:
        score += 32
    elif quantity >= 2_000:
        score += 25
    elif quantity >= 1_000:
        score += 18
    elif quantity >= 500:
        score += 12
    elif quantity >= 300:
        score += 8
    else:
        score += 0   # below threshold

    # ── Contact completeness ──────────────────────────────────────────────
    if mapped.get("buyer_email"):
        score += 10
    if mapped.get("buyer_mobile"):
        score += 15

    # ── Requirement detail (0–20 pts) ─────────────────────────────────────
    req_len = len(requirement)
    if req_len > 200:
        score += 20
    elif req_len > 100:
        score += 14
    elif req_len > 50:
        score += 8
    elif req_len > 20:
        score += 4

    # ── Keyword signals (0–15 pts) ────────────────────────────────────────
    high_hits = sum(1 for kw in HIGH_INTENT_KEYWORDS if kw in requirement)
    low_hits  = sum(1 for kw in LOW_INTENT_KEYWORDS  if kw in requirement)
    score += min(high_hits * 3, 15)
    score -= min(low_hits  * 5, 15)

    return max(0.0, min(100.0, round(score, 1)))


def is_qualifying(lead: Lead) -> bool:
    """
    Gate: Does this lead deserve outreach?
    Hard rule: quantity >= LEAD_MIN_QUANTITY
    Soft rule: score >= 10 (catches obvious junk even if qty is met)
    """
    if lead.quantity < settings.lead_min_quantity:
        logger.debug(
            f"Lead {lead.indiamart_id} below min quantity "
            f"({lead.quantity} < {settings.lead_min_quantity})"
        )
        return False

    if lead.quality_score < 10:
        logger.debug(
            f"Lead {lead.indiamart_id} quality score too low ({lead.quality_score})"
        )
        return False

    return True
