"""
app/models/database.py
SQLAlchemy ORM models + Supabase/PostgreSQL engine setup.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, Enum, create_engine, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.config import settings

# ── Engine & Session ────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,          # recover from dropped connections
    echo=(settings.app_env == "development"),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Enums ────────────────────────────────────────────────────────────────────
class LeadStatus(str, enum.Enum):
    NEW        = "new"
    ENGAGED    = "engaged"
    REPLIED    = "replied"
    CONVERTED  = "converted"
    REJECTED   = "rejected"
    DUPLICATE  = "duplicate"


class OutreachChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL    = "email"
    SMS      = "sms"


class OutreachStatus(str, enum.Enum):
    PENDING  = "pending"
    SENT     = "sent"
    FAILED   = "failed"
    BOUNCED  = "bounced"


class CallDirection(str, enum.Enum):
    INBOUND  = "inbound"
    OUTBOUND = "outbound"


# ── Models ───────────────────────────────────────────────────────────────────
class Lead(Base):
    __tablename__ = "leads"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indiamart_id   = Column(String(64), unique=True, nullable=False, index=True)
    buyer_name     = Column(String(256))
    buyer_mobile   = Column(String(20))
    buyer_email    = Column(String(256))
    buyer_city     = Column(String(128))
    buyer_state    = Column(String(128))
    buyer_country  = Column(String(64), default="India")
    product        = Column(String(512))
    quantity       = Column(Integer)
    quantity_unit  = Column(String(32))
    requirement    = Column(Text)
    quality_score  = Column(Float, default=0.0)   # 0-100
    status         = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    raw_payload    = Column(Text)                  # full JSON from API
    received_at    = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_leads_received_at_status", "received_at", "status"),
    )


class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id     = Column(UUID(as_uuid=True), nullable=False, index=True)
    channel     = Column(Enum(OutreachChannel), nullable=False)
    status      = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)
    recipient   = Column(String(256))              # phone or email
    message_id  = Column(String(256))              # provider's message ID
    error       = Column(Text)
    sent_at     = Column(DateTime, default=datetime.utcnow)
    delivered_at= Column(DateTime, nullable=True)


class CallLog(Base):
    __tablename__ = "call_logs"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id         = Column(UUID(as_uuid=True), nullable=True, index=True)
    exotel_call_sid = Column(String(128), unique=True)
    direction       = Column(Enum(CallDirection), default=CallDirection.INBOUND)
    caller_number   = Column(String(20))
    virtual_number  = Column(String(20))
    duration_secs   = Column(Integer, default=0)
    status          = Column(String(32))           # answered, no-answer, busy, etc.
    recording_url   = Column(String(512), nullable=True)
    call_time       = Column(DateTime, default=datetime.utcnow, index=True)


class SystemHealth(Base):
    __tablename__ = "system_health"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    component   = Column(String(64))               # poller, whatsapp, email, etc.
    status      = Column(String(16))               # ok | error
    message     = Column(Text)
    checked_at  = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
