"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ── Auth ──────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str
    password: str = Field(min_length=6)
    role: str = "analyst"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Upload ────────────────────────────────────────────
class UploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    record_count: int
    quality_score: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UploadSummary(BaseModel):
    upload: UploadResponse
    total_records: int
    total_exceptions: int
    critical_count: int
    warning_count: int
    info_count: int
    resolved_count: int
    quality_score: float


# ── Loan Record ───────────────────────────────────────
class LoanRecordResponse(BaseModel):
    id: str
    row_index: int
    loan_id: Optional[str]
    borrower_name: Optional[str]
    loan_amount: Optional[float]
    interest_rate: Optional[float]
    loan_term_months: Optional[int]
    origination_date: Optional[str]
    monthly_payment: Optional[float]
    remaining_balance: Optional[float]
    status: Optional[str]
    credit_score: Optional[int]
    ltv_ratio: Optional[float]
    property_type: Optional[str]
    state: Optional[str]
    record_hash: Optional[str]
    chain_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Validation Exception ──────────────────────────────
class ExceptionResponse(BaseModel):
    id: str
    upload_id: str
    record_id: Optional[str]
    row_index: Optional[int]
    field_name: str
    rule_name: str
    severity: str
    message: str
    expected_value: Optional[str]
    actual_value: Optional[str]
    status: str
    ai_explanation: Optional[str]
    resolution_note: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExceptionResolve(BaseModel):
    resolution_note: str
    action: str = "resolved"  # resolved or dismissed


class AIExplanationResponse(BaseModel):
    exception_id: str
    explanation: str
    suggested_fix: Optional[str]


# ── Audit Log ─────────────────────────────────────────
class AuditLogResponse(BaseModel):
    id: str
    upload_id: Optional[str]
    user_id: Optional[str]
    action: str
    details: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────
class DashboardStats(BaseModel):
    total_uploads: int
    total_records: int
    total_exceptions: int
    resolved_exceptions: int
    avg_quality_score: float
    recent_uploads: List[UploadResponse]
    exception_breakdown: Dict[str, int]  # critical/warning/info counts
