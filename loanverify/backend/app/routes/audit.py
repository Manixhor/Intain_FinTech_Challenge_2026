"""Audit log routes — view audit trail and dashboard statistics."""

from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from ..database import get_db
from ..models import (
    User, AuditLog, LoanUpload, LoanRecord, ValidationException, UserRole
)
from ..schemas import AuditLogResponse, DashboardStats, UploadResponse
from ..auth import get_current_user, require_admin, require_reviewer

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    upload_id: str = None,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Get audit logs. Reviewers see all; filtered by upload_id if provided."""
    query = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    if upload_id:
        query = query.where(AuditLog.upload_id == upload_id)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the current user."""
    # Total uploads
    total_uploads = (await db.execute(select(func.count()).select_from(LoanUpload))).scalar()

    # Total records
    total_records = (await db.execute(select(func.count()).select_from(LoanRecord))).scalar()

    # Exception counts
    total_exceptions = (await db.execute(select(func.count()).select_from(ValidationException))).scalar()
    resolved_exceptions = (await db.execute(
        select(func.count()).where(ValidationException.status.in_(["resolved", "dismissed"]))
    )).scalar()

    # Average quality score
    avg_score_result = await db.execute(select(func.avg(LoanUpload.quality_score)))
    avg_quality = round(avg_score_result.scalar() or 0.0, 1)

    # Recent uploads (last 10)
    recent_result = await db.execute(
        select(LoanUpload).order_by(desc(LoanUpload.created_at)).limit(10)
    )
    recent_uploads = [UploadResponse.model_validate(u) for u in recent_result.scalars().all()]

    # Exception breakdown by severity
    breakdown = {}
    for severity in ["critical", "warning", "info"]:
        count = (await db.execute(
            select(func.count()).where(ValidationException.severity == severity)
        )).scalar()
        breakdown[severity] = count

    return DashboardStats(
        total_uploads=total_uploads,
        total_records=total_records,
        total_exceptions=total_exceptions,
        resolved_exceptions=resolved_exceptions,
        avg_quality_score=avg_quality,
        recent_uploads=recent_uploads,
        exception_breakdown=breakdown,
    )


@router.get("/chain-verify/{upload_id}")
async def verify_hash_chain(
    upload_id: str,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Verify the hash chain integrity for all records in an upload."""
    result = await db.execute(
        select(LoanRecord)
        .where(LoanRecord.upload_id == upload_id)
        .order_by(LoanRecord.chain_index)
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="No records found for this upload")

    # Verify chain
    broken = []
    prev_hash = "GENESIS"

    for i, rec in enumerate(records):
        if rec.prev_hash != prev_hash:
            broken.append({
                "index": rec.chain_index,
                "record_id": rec.id,
                "expected_prev": prev_hash,
                "actual_prev": rec.prev_hash,
            })
        prev_hash = rec.record_hash

    return {
        "upload_id": upload_id,
        "total_records": len(records),
        "chain_valid": len(broken) == 0,
        "broken_links": broken,
    }
