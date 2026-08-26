"""Data ingestion service — parse CSV/Excel, normalize loan fields, store records."""

import io
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import LoanUpload, LoanRecord


# ── Field mapping (messy → normalized) ────────────────
FIELD_ALIASES = {
    "loan_id":        ["loan_id", "loanid", "id", "loan_number", "account_number", "loan#"],
    "borrower_name":  ["borrower_name", "borrower", "name", "borrowername", "customer_name", "full_name"],
    "loan_amount":    ["loan_amount", "amount", "principal", "loan_balance", "original_amount", "loanamount"],
    "interest_rate":  ["interest_rate", "rate", "int_rate", "interest", "apr", "annual_rate"],
    "loan_term_months": ["loan_term_months", "term", "term_months", "months", "loan_term"],
    "origination_date": ["origination_date", "orig_date", "start_date", "disbursement_date", "date_origination", "origination"],
    "monthly_payment": ["monthly_payment", "payment", "monthly_payment_amount", "pmt"],
    "remaining_balance": ["remaining_balance", "balance", "remaining", "outstanding", "current_balance"],
    "status":         ["status", "loan_status", "condition"],
    "credit_score":   ["credit_score", "fico", "score", "credit_rating"],
    "ltv_ratio":      ["ltv_ratio", "ltv", "loan_to_value", "loan-to-value"],
    "property_type":  ["property_type", "type", "collateral_type", "property"],
    "state":          ["state", "property_state", "region", "location"],
}

# Expected numeric ranges for validation hints
FIELD_TYPES = {
    "loan_amount": "float",
    "interest_rate": "float",
    "loan_term_months": "int",
    "monthly_payment": "float",
    "remaining_balance": "float",
    "credit_score": "int",
    "ltv_ratio": "float",
}


def normalize_column_name(col: str) -> Optional[str]:
    """Map a messy column name to a normalized field name."""
    clean = col.strip().lower().replace(" ", "_").replace("-", "_")
    for field, aliases in FIELD_ALIASES.items():
        if clean in aliases or clean == field:
            return field
    return None


def compute_record_hash(record_data: dict, prev_hash: str = "") -> str:
    """Compute SHA-256 hash of a record, chaining with previous hash."""
    # Sort keys for determinism
    canonical = "|".join(f"{k}={v}" for k, v in sorted(record_data.items()) if k not in ("id", "created_at"))
    chain_input = f"{prev_hash}||{canonical}"
    return hashlib.sha256(chain_input.encode("utf-8")).hexdigest()


async def ingest_file(
    file_content: bytes,
    filename: str,
    upload: LoanUpload,
    db: AsyncSession,
    uploaded_by: str,
) -> Tuple[List[LoanRecord], List[Dict]]:
    """
    Parse an uploaded CSV/Excel file, normalize fields, create LoanRecord rows.
    Returns (records, raw_rows) where raw_rows is the original data for each record.
    """
    # Read file into DataFrame
    if filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        df = pd.read_csv(io.BytesIO(file_content))

    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    # Build mapping: normalized_field → original_column
    col_map = {}
    for col in df.columns:
        norm = normalize_column_name(col)
        if norm:
            col_map[norm] = col

    records = []
    raw_rows = []
    prev_hash = "GENESIS"

    for idx, row in df.iterrows():
        raw_dict = row.to_dict()

        # Build normalized record
        record_data = {}
        for norm_field, orig_col in col_map.items():
            val = row[orig_col]
            if pd.isna(val):
                record_data[norm_field] = None
            elif FIELD_TYPES.get(norm_field) == "int":
                try:
                    record_data[norm_field] = int(float(val))
                except (ValueError, TypeError):
                    record_data[norm_field] = None
            elif FIELD_TYPES.get(norm_field) == "float":
                try:
                    record_data[norm_field] = round(float(val), 4)
                except (ValueError, TypeError):
                    record_data[norm_field] = None
            else:
                record_data[norm_field] = str(val).strip() if val else None

        # Compute hash chain
        rec_hash = compute_record_hash(record_data, prev_hash)

        record = LoanRecord(
            upload_id=upload.id,
            row_index=idx,
            loan_id=record_data.get("loan_id"),
            borrower_name=record_data.get("borrower_name"),
            loan_amount=record_data.get("loan_amount"),
            interest_rate=record_data.get("interest_rate"),
            loan_term_months=record_data.get("loan_term_months"),
            origination_date=record_data.get("origination_date"),
            monthly_payment=record_data.get("monthly_payment"),
            remaining_balance=record_data.get("remaining_balance"),
            status=record_data.get("status"),
            credit_score=record_data.get("credit_score"),
            ltv_ratio=record_data.get("ltv_ratio"),
            property_type=record_data.get("property_type"),
            state=record_data.get("state"),
            raw_data=raw_dict,
            normalized=True,
            record_hash=rec_hash,
            prev_hash=prev_hash,
            chain_index=idx,
        )

        prev_hash = rec_hash
        records.append(record)
        raw_rows.append(raw_dict)

    # Bulk insert
    db.add_all(records)
    await db.flush()

    return records, raw_rows
