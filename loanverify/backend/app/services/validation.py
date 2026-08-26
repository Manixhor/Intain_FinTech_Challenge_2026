"""Validation engine — rule-based checks on normalized loan records, generates exceptions."""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import LoanRecord, ValidationException, LoanUpload


# ── Validation Rules ──────────────────────────────────
class ValidationRule:
    def __init__(self, field: str, rule_name: str, severity: str, check_fn, message_fn, expected_fn=None):
        self.field = field
        self.rule_name = rule_name
        self.severity = severity  # critical, warning, info
        self.check_fn = check_fn      # (value, record_dict) -> bool (True = violation)
        self.message_fn = message_fn   # (value, record_dict) -> str
        self.expected_fn = expected_fn  # (record_dict) -> str

    def validate(self, record_dict: dict) -> Optional[Dict[str, Any]]:
        val = record_dict.get(self.field)
        if val is None:
            # Skip null checks for optional fields (handled by completeness rule)
            return None
        if self.check_fn(val, record_dict):
            return {
                "field_name": self.field,
                "rule_name": self.rule_name,
                "severity": self.severity,
                "message": self.message_fn(val, record_dict),
                "expected_value": self.expected_fn(record_dict) if self.expected_fn else None,
                "actual_value": str(val),
            }
        return None


# ── Define all rules ──────────────────────────────────
RULES: List[ValidationRule] = [
    # Missing required fields
    ValidationRule(
        field="loan_id",
        rule_name="missing_loan_id",
        severity="critical",
        check_fn=lambda v, r: v is None or str(v).strip() == "",
        message_fn=lambda v, r: "Loan ID is missing — every record needs a unique identifier.",
        expected_fn=lambda r: "Non-empty string",
    ),
    ValidationRule(
        field="loan_amount",
        rule_name="missing_loan_amount",
        severity="critical",
        check_fn=lambda v, r: v is None,
        message_fn=lambda v, r: "Loan amount is missing — cannot validate the loan.",
        expected_fn=lambda r: "Numeric value",
    ),
    # Interest rate range
    ValidationRule(
        field="interest_rate",
        rule_name="interest_rate_outlier",
        severity="critical",
        check_fn=lambda v, r: v is not None and (v < 0.1 or v > 30.0),
        message_fn=lambda v, r: f"Interest rate {v}% is outside typical range (0.1% – 30%).",
        expected_fn=lambda r: "0.1% – 30%",
    ),
    ValidationRule(
        field="interest_rate",
        rule_name="interest_rate_unusually_high",
        severity="warning",
        check_fn=lambda v, r: v is not None and 12.0 < v <= 30.0,
        message_fn=lambda v, r: f"Interest rate {v}% is unusually high — verify this is correct.",
        expected_fn=lambda r: "Typically 3% – 12%",
    ),
    # Loan amount
    ValidationRule(
        field="loan_amount",
        rule_name="loan_amount_negative",
        severity="critical",
        check_fn=lambda v, r: v is not None and v < 0,
        message_fn=lambda v, r: f"Loan amount is negative ({v}). This is invalid.",
        expected_fn=lambda r: "Positive number",
    ),
    ValidationRule(
        field="loan_amount",
        rule_name="loan_amount_zero",
        severity="warning",
        check_fn=lambda v, r: v is not None and v == 0,
        message_fn=lambda v, r: "Loan amount is zero — possible data entry error.",
        expected_fn=lambda r: "Positive number",
    ),
    ValidationRule(
        field="loan_amount",
        rule_name="loan_amount_extreme",
        severity="warning",
        check_fn=lambda v, r: v is not None and v > 10_000_000,
        message_fn=lambda v, r: f"Loan amount ${v:,.0f} is very large — verify this is correct.",
        expected_fn=lambda r: "Under $10M typical",
    ),
    # Credit score
    ValidationRule(
        field="credit_score",
        rule_name="credit_score_range",
        severity="critical",
        check_fn=lambda v, r: v is not None and (v < 300 or v > 850),
        message_fn=lambda v, r: f"Credit score {v} is outside valid FICO range (300–850).",
        expected_fn=lambda r: "300 – 850",
    ),
    # LTV ratio
    ValidationRule(
        field="ltv_ratio",
        rule_name="ltv_ratio_range",
        severity="warning",
        check_fn=lambda v, r: v is not None and (v < 0 or v > 1.5),
        message_fn=lambda v, r: f"LTV ratio {v} is unusual — expected 0%–100% (0.0–1.0), max 150%.",
        expected_fn=lambda r: "0.0 – 1.0",
    ),
    # Loan term
    ValidationRule(
        field="loan_term_months",
        rule_name="loan_term_range",
        severity="warning",
        check_fn=lambda v, r: v is not None and (v <= 0 or v > 600),
        message_fn=lambda v, r: f"Loan term {v} months is unusual (max typical: 360 = 30 years).",
        expected_fn=lambda r: "1 – 360 months",
    ),
    # Status value
    ValidationRule(
        field="status",
        rule_name="status_invalid",
        severity="warning",
        check_fn=lambda v, r: v is not None and v.lower().strip() not in (
            "current", "late", "defaulted", "paid_off", "delinquent", "in_default", "paid", "active", "closed", "charged_off"
        ),
        message_fn=lambda v, r: f"Status '{v}' is not a recognized loan status.",
        expected_fn=lambda r: "current, late, defaulted, paid_off, delinquent, etc.",
    ),
    # Borrower name
    ValidationRule(
        field="borrower_name",
        rule_name="borrower_name_invalid",
        severity="warning",
        check_fn=lambda v, r: v is not None and len(str(v).strip()) < 2,
        message_fn=lambda v, r: f"Borrower name '{v}' seems too short.",
        expected_fn=lambda r: "Full name",
    ),
    # State validation
    ValidationRule(
        field="state",
        rule_name="state_invalid_format",
        severity="info",
        check_fn=lambda v, r: v is not None and not re.match(r"^[A-Z]{2}$", str(v).strip().upper()),
        message_fn=lambda v, r: f"State '{v}' doesn't match 2-letter US state format.",
        expected_fn=lambda r: "2-letter state code (e.g., CA, NY)",
    ),
]


async def validate_records(
    records: List[LoanRecord],
    upload: LoanUpload,
    db: AsyncSession,
) -> List[ValidationException]:
    """
    Run all validation rules against all records. Create ValidationException
    rows for each violation found. Returns list of exceptions.
    """
    exceptions = []

    for record in records:
        record_dict = {
            "loan_id": record.loan_id,
            "borrower_name": record.borrower_name,
            "loan_amount": record.loan_amount,
            "interest_rate": record.interest_rate,
            "loan_term_months": record.loan_term_months,
            "origination_date": record.origination_date,
            "monthly_payment": record.monthly_payment,
            "remaining_balance": record.remaining_balance,
            "status": record.status,
            "credit_score": record.credit_score,
            "ltv_ratio": record.ltv_ratio,
            "property_type": record.property_type,
            "state": record.state,
        }

        # Check null completeness for critical fields
        for field, display in [
            ("borrower_name", "Borrower Name"),
            ("origination_date", "Origination Date"),
        ]:
            if record_dict.get(field) is None:
                exceptions.append(ValidationException(
                    upload_id=upload.id,
                    record_id=record.id,
                    row_index=record.row_index,
                    field_name=field,
                    rule_name=f"missing_{field}",
                    severity="warning",
                    message=f"{display} is missing from this record.",
                    expected_value="Non-empty value",
                    actual_value="NULL",
                ))

        # Run all rules
        for rule in RULES:
            violation = rule.validate(record_dict)
            if violation:
                exceptions.append(ValidationException(
                    upload_id=upload.id,
                    record_id=record.id,
                    row_index=record.row_index,
                    **violation,
                ))

    # Bulk insert exceptions
    if exceptions:
        db.add_all(exceptions)
        await db.flush()

    return exceptions


def compute_quality_score(
    total_records: int,
    exceptions: List[ValidationException],
) -> float:
    """Compute a 0–100 quality score. Starts at 100, deducts per exception."""
    if total_records == 0:
        return 0.0

    deductions = 0
    for exc in exceptions:
        if exc.severity == "critical":
            deductions += 10
        elif exc.severity == "warning":
            deductions += 3
        else:
            deductions += 1

    # Normalize: average deduction per record, subtracted from 100
    per_record_deduction = deductions / total_records
    score = max(0.0, 100.0 - per_record_deduction)
    return round(min(100.0, score), 1)
