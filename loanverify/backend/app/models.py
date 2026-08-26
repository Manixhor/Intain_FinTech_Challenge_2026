"""SQLAlchemy models for the loan verification system."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, Boolean,
    ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from .database import Base
import enum


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class ExceptionStatus(str, enum.Enum):
    PENDING = "pending"
    EXPLAINED = "explained"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.ANALYST)
    created_at = Column(DateTime, default=datetime.utcnow)

    uploads = relationship("LoanUpload", back_populates="uploader")
    resolutions = relationship("ValidationException", back_populates="resolver")


class LoanUpload(Base):
    __tablename__ = "loan_uploads"

    id = Column(String, primary_key=True, default=gen_uuid)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    record_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    status = Column(String(50), default="processing")  # processing, completed, failed
    uploaded_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    uploader = relationship("User", back_populates="uploads")
    records = relationship("LoanRecord", back_populates="upload", cascade="all, delete-orphan")
    exceptions = relationship("ValidationException", back_populates="upload", cascade="all, delete-orphan")


class LoanRecord(Base):
    __tablename__ = "loan_records"

    id = Column(String, primary_key=True, default=gen_uuid)
    upload_id = Column(String, ForeignKey("loan_uploads.id"), nullable=False)
    row_index = Column(Integer, nullable=False)

    # Normalized loan fields
    loan_id = Column(String(100))
    borrower_name = Column(String(255))
    loan_amount = Column(Float)
    interest_rate = Column(Float)
    loan_term_months = Column(Integer)
    origination_date = Column(String(50))
    monthly_payment = Column(Float)
    remaining_balance = Column(Float)
    status = Column(String(50))  # current, late, defaulted, paid_off
    credit_score = Column(Integer)
    ltv_ratio = Column(Float)
    property_type = Column(String(100))
    state = Column(String(5))

    # Raw and normalized data
    raw_data = Column(JSON)  # Original row data
    normalized = Column(Boolean, default=False)

    # Hash chain
    record_hash = Column(String(64))
    prev_hash = Column(String(64))
    chain_index = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    upload = relationship("LoanUpload", back_populates="records")
    exceptions = relationship("ValidationException", back_populates="record")


class ValidationException(Base):
    __tablename__ = "validation_exceptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    upload_id = Column(String, ForeignKey("loan_uploads.id"), nullable=False)
    record_id = Column(String, ForeignKey("loan_records.id"), nullable=True)
    row_index = Column(Integer)

    field_name = Column(String(100))
    rule_name = Column(String(200))
    severity = Column(String(20))  # critical, warning, info
    message = Column(Text)
    expected_value = Column(String(500))
    actual_value = Column(String(500))
    status = Column(String(30), default="pending")
    ai_explanation = Column(Text)
    resolution_note = Column(Text)

    resolved_by = Column(String, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    upload = relationship("LoanUpload", back_populates="exceptions")
    record = relationship("LoanRecord", back_populates="exceptions")
    resolver = relationship("User", back_populates="resolutions", foreign_keys=[resolved_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    upload_id = Column(String, ForeignKey("loan_uploads.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
