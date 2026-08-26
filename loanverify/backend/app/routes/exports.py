"""Export routes — download verified data, audit report, hash chain manifest."""

import io
import csv
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, LoanUpload, LoanRecord, ValidationException, AuditLog
from ..auth import get_current_user, require_reviewer

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/{upload_id}/verified-csv")
async def export_verified_csv(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a CSV of records with no unresolved critical/warning exceptions."""
    # Get upload
    result = await db.execute(select(LoanUpload).where(LoanUpload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Get all records
    rec_result = await db.execute(
        select(LoanRecord)
        .where(LoanRecord.upload_id == upload_id)
        .order_by(LoanRecord.row_index)
    )
    records = rec_result.scalars().all()

    # Get exception record IDs (only critical/warning that are NOT resolved)
    exc_result = await db.execute(
        select(ValidationException.record_id).where(
            ValidationException.upload_id == upload_id,
            ValidationException.severity.in_(["critical", "warning"]),
            ValidationException.status.notin_(["resolved", "dismissed"]),
        )
    )
    bad_record_ids = set(exc_result.scalars().all())

    # Filter records
    clean_records = [r for r in records if r.id not in bad_record_ids]

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "loan_id", "borrower_name", "loan_amount", "interest_rate",
        "loan_term_months", "origination_date", "monthly_payment",
        "remaining_balance", "status", "credit_score", "ltv_ratio",
        "property_type", "state", "record_hash"
    ])

    for rec in clean_records:
        writer.writerow([
            rec.loan_id or "", rec.borrower_name or "",
            rec.loan_amount or "", rec.interest_rate or "",
            rec.loan_term_months or "", rec.origination_date or "",
            rec.monthly_payment or "", rec.remaining_balance or "",
            rec.status or "", rec.credit_score or "",
            rec.ltv_ratio or "", rec.property_type or "",
            rec.state or "", rec.record_hash or ""
        ])

    output.seek(0)
    filename = f"verified_{upload.original_filename.replace('.csv', '')}_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{upload_id}/full-csv")
async def export_full_csv(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download ALL records (including ones with exceptions) as CSV."""
    result = await db.execute(select(LoanUpload).where(LoanUpload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    rec_result = await db.execute(
        select(LoanRecord)
        .where(LoanRecord.upload_id == upload_id)
        .order_by(LoanRecord.row_index)
    )
    records = rec_result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "loan_id", "borrower_name", "loan_amount", "interest_rate",
        "loan_term_months", "origination_date", "monthly_payment",
        "remaining_balance", "status", "credit_score", "ltv_ratio",
        "property_type", "state", "record_hash"
    ])

    for rec in records:
        writer.writerow([
            rec.loan_id or "", rec.borrower_name or "",
            rec.loan_amount or "", rec.interest_rate or "",
            rec.loan_term_months or "", rec.origination_date or "",
            rec.monthly_payment or "", rec.remaining_balance or "",
            rec.status or "", rec.credit_score or "",
            rec.ltv_ratio or "", rec.property_type or "",
            rec.state or "", rec.record_hash or ""
        ])

    output.seek(0)
    filename = f"full_{upload.original_filename.replace('.csv', '')}_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{upload_id}/audit-report")
async def export_audit_report(
    upload_id: str,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Download a JSON audit report with all records, exceptions, and audit log."""
    # Get upload
    result = await db.execute(select(LoanUpload).where(LoanUpload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Get records
    rec_result = await db.execute(
        select(LoanRecord).where(LoanRecord.upload_id == upload_id).order_by(LoanRecord.row_index)
    )
    records = rec_result.scalars().all()

    # Get exceptions
    exc_result = await db.execute(
        select(ValidationException).where(ValidationException.upload_id == upload_id)
    )
    exceptions = exc_result.scalars().all()

    # Get audit log
    log_result = await db.execute(
        select(AuditLog).where(AuditLog.upload_id == upload_id).order_by(AuditLog.created_at)
    )
    audit_logs = log_result.scalars().all()

    # Build report
    report = {
        "report_title": "LoanVerify Audit Report",
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": user.username,
        "upload": {
            "id": upload.id,
            "filename": upload.original_filename,
            "record_count": upload.record_count,
            "quality_score": upload.quality_score,
            "status": upload.status,
            "uploaded_at": upload.created_at.isoformat() if upload.created_at else None,
        },
        "records": [
            {
                "row_index": r.row_index,
                "loan_id": r.loan_id,
                "borrower_name": r.borrower_name,
                "loan_amount": r.loan_amount,
                "interest_rate": r.interest_rate,
                "status": r.status,
                "credit_score": r.credit_score,
                "record_hash": r.record_hash,
                "prev_hash": r.prev_hash,
                "chain_index": r.chain_index,
            }
            for r in records
        ],
        "exceptions": [
            {
                "row_index": e.row_index,
                "field": e.field_name,
                "rule": e.rule_name,
                "severity": e.severity,
                "message": e.message,
                "actual_value": e.actual_value,
                "expected_value": e.expected_value,
                "status": e.status,
                "ai_explanation": e.ai_explanation,
                "resolved_by": e.resolved_by,
                "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            }
            for e in exceptions
        ],
        "audit_trail": [
            {
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ],
        "hash_chain": {
            "total_records": len(records),
            "genesis_hash": "GENESIS",
            "final_hash": records[-1].record_hash if records else None,
        },
    }

    content = json.dumps(report, indent=2, default=str)
    filename = f"audit_report_{upload.original_filename.replace('.csv', '')}_{datetime.utcnow().strftime('%Y%m%d')}.json"

    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{upload_id}/hash-manifest")
async def export_hash_manifest(
    upload_id: str,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Download the hash chain manifest for all records."""
    result = await db.execute(select(LoanUpload).where(LoanUpload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    rec_result = await db.execute(
        select(LoanRecord).where(LoanRecord.upload_id == upload_id).order_by(LoanRecord.row_index)
    )
    records = rec_result.scalars().all()

    manifest = {
        "manifest_title": "LoanVerify Hash Chain Manifest",
        "upload_id": upload_id,
        "filename": upload.original_filename,
        "generated_at": datetime.utcnow().isoformat(),
        "total_records": len(records),
        "chain": [
            {
                "index": r.chain_index,
                "loan_id": r.loan_id,
                "hash": r.record_hash,
                "prev_hash": r.prev_hash,
            }
            for r in records
        ],
        "genesis": "GENESIS",
        "final_hash": records[-1].record_hash if records else None,
    }

    content = json.dumps(manifest, indent=2)
    filename = f"hash_manifest_{upload.original_filename.replace('.csv', '')}_{datetime.utcnow().strftime('%Y%m%d')}.json"

    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
