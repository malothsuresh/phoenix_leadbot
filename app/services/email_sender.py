"""
app/services/email_sender.py
Sends HTML quotation emails via AWS SES using boto3.
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logger import get_logger
from app.models.database import Lead

logger = get_logger(__name__)


def _get_ses_client():
    return boto3.client(
        "ses",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def _build_html_body(lead: Lead) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body      {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
    .container{{ max-width: 600px; margin: 0 auto; padding: 24px; }}
    .header   {{ background: #1a3c6e; padding: 20px; text-align: center; border-radius: 6px 6px 0 0; }}
    .header h1{{ color: #fff; font-size: 22px; margin: 0; }}
    .body     {{ background: #f9f9f9; padding: 24px; border: 1px solid #ddd; }}
    .highlight{{ background: #e8f0fe; border-left: 4px solid #1a3c6e; padding: 12px; margin: 16px 0; }}
    .features {{ list-style: none; padding: 0; }}
    .features li{{ padding: 6px 0; }}
    .features li::before{{ content: "✅ "; }}
    .cta      {{ background: #1a3c6e; color: #fff; padding: 14px 28px; text-decoration: none;
                 border-radius: 4px; display: inline-block; margin: 16px 0; font-weight: bold; }}
    .footer   {{ font-size: 12px; color: #888; text-align: center; padding: 16px; }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>{settings.company_name}</h1>
    <p style="color:#ccc;margin:4px 0 0;">Medical Consumables Supplier</p>
  </div>
  <div class="body">
    <p>Dear <strong>{lead.buyer_name or 'Valued Buyer'}</strong>,</p>
    <p>Thank you for posting your requirement on IndiaMART. We came across your enquiry
       and would like to present our offer.</p>

    <div class="highlight">
      <strong>Your Requirement:</strong><br>
      Product : {lead.product or 'Medical Supplies'}<br>
      Quantity: {lead.quantity} {lead.quantity_unit}<br>
      Location: {lead.buyer_city}, {lead.buyer_state}
    </div>

    <p>We are a leading supplier of medical consumables with the following advantages:</p>
    <ul class="features">
      <li>ISO 13485 &amp; CE certified products</li>
      <li>Bulk quantities available — ready stock</li>
      <li>Competitive ex-factory pricing</li>
      <li>Flexible MOQ for regular buyers</li>
      <li>Fast dispatch within 48 hours</li>
      <li>Samples available on request</li>
    </ul>

    <p>Please reply to this email or contact us directly to receive a detailed quotation
       tailored to your requirement.</p>

    <a class="cta" href="mailto:{settings.company_email}">Request a Quote</a>

    <p>You can also reach us via WhatsApp: <strong>{settings.company_phone}</strong></p>
  </div>
  <div class="footer">
    {settings.company_name} | {settings.company_email} | {settings.company_phone}
    <br>{settings.company_website}
    <br><small>You received this because you posted a requirement on IndiaMART matching our products.</small>
  </div>
</div>
</body>
</html>
"""


async def send_email(lead: Lead) -> str:
    """
    Send HTML intro email via AWS SES.
    Returns SES MessageId on success, raises on failure.
    Note: boto3 is synchronous — runs fine in async context for low volume.
    """
    subject = (
        f"Re: Your Requirement for {lead.product or 'Medical Supplies'} "
        f"({lead.quantity} {lead.quantity_unit}) — {settings.company_name}"
    )

    html_body = _build_html_body(lead)
    text_body = (
        f"Dear {lead.buyer_name or 'Buyer'},\n\n"
        f"Thank you for your enquiry about {lead.product} ({lead.quantity} {lead.quantity_unit}).\n"
        f"We are {settings.company_name}, a supplier of ISO-certified medical consumables.\n\n"
        f"Please reply to discuss your requirement.\n\n"
        f"Contact: {settings.company_phone} | {settings.company_email}"
    )

    try:
        client = _get_ses_client()
        response = client.send_email(
            Source=f"{settings.ses_from_name} <{settings.ses_from_email}>",
            Destination={"ToAddresses": [lead.buyer_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            },
        )
        msg_id = response["MessageId"]
        logger.info(f"Email sent → {lead.buyer_email} | MessageId={msg_id}")
        return msg_id

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg  = e.response["Error"]["Message"]
        logger.error(f"SES ClientError [{error_code}]: {error_msg}")
        raise
    except BotoCoreError as e:
        logger.error(f"SES BotoCoreError: {e}")
        raise
