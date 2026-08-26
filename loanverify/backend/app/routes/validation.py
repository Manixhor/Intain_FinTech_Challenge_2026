"""Validation exception routes — resolve, explain, and manage exceptions."""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, ValidationException, LoanRecord, UserRole
from ..schemas import ExceptionResponse, ExceptionResolve, AIExplanationResponse
from ..auth import get_current_user, require_reviewer
from ..services.ai_copilot import explain_exception, generate_batch_explanations
from ..services.audit import log_action

router = APIRouter(prefix="/api/exceptions", tags=["validation"])


@router.get("/{exception_id}", response_model=ExceptionResponse)
async def get_exception(
    exception_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single validation exception by ID."""
    result = await db.execute(
        select(ValidationException).where(ValidationException.id == exception_id)
    )
    exc = result.scalar_one_or_none()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    return ExceptionResponse.model_validate(exc)


@router.post("/{exception_id}/explain", response_model=AIExplanationResponse)
async def get_ai_explanation(
    exception_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated explanation for a validation exception."""
    result = await db.execute(
        select(ValidationException).where(ValidationException.id == exception_id)
    )
    exc = result.scalar_one_or_none()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    # Get record context
    record_context = {}
    if exc.record_id:
        record_result = await db.execute(
            select(LoanRecord).where(LoanRecord.id == exc.record_id)
        )
        record = record_result.scalar_one_or_none()
        if record:
            record_context = {
                "loan_id": record.loan_id,
                "borrower_name": record.borrower_name,
                "loan_amount": record.loan_amount,
                "interest_rate": record.interest_rate,
                "credit_score": record.credit_score,
                "status": record.status,
            }

    # Generate explanation
    ai_result = await explain_exception(
        exception_id=exc.id,
        field_name=exc.field_name,
        rule_name=exc.rule_name,
        message=exc.message,
        actual_value=exc.actual_value,
        record_context=record_context,
    )

    # Save explanation to database
    exc.ai_explanation = ai_result["explanation"]
    exc.status = "explained"
    await db.commit()

    await log_action(
        db, "ai_explanation_generated",
        user.id, exc.upload_id,
        {"exception_id": exc.id, "field": exc.field_name, "rule": exc.rule_name},
    )

    return AIExplanationResponse(
        exception_id=exc.id,
        explanation=ai_result["explanation"],
        suggested_fix=ai_result.get("suggested_fix"),
    )


@router.post("/{exception_id}/resolve", response_model=ExceptionResponse)
async def resolve_exception(
    exception_id: str,
    data: ExceptionResolve,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Resolve or dismiss a validation exception. Requires reviewer role."""
    result = await db.execute(
        select(ValidationException).where(ValidationException.id == exception_id)
    )
    exc = result.scalar_one_or_none()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    exc.status = data.action
    exc.resolution_note = data.resolution_note
    exc.resolved_by = user.id
    exc.resolved_at = __import__("datetime").datetime.utcnow()

    await db.commit()
    await db.refresh(exc)

    await log_action(
        db, f"exception_{data.action}",
        user.id, exc.upload_id,
        {"exception_id": exc.id, "note": data.resolution_note},
    )

    return ExceptionResponse.model_validate(exc)


@router.post("/batch-explain")
async def batch_explain_exceptions(
    exception_ids: List[str],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI explanations for multiple exceptions at once."""
    if len(exception_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 exceptions per batch")

    result = await db.execute(
        select(ValidationException).where(ValidationException.id.in_(exception_ids))
    )
    exceptions = result.scalars().all()

    if not exceptions:
        raise HTTPException(status_code=404, detail="No exceptions found")

    # Build record context lookup
    record_ids = [e.record_id for e in exceptions if e.record_id]
    record_lookup = {}
    if record_ids:
        rec_result = await db.execute(
            select(LoanRecord).where(LoanRecord.id.in_(record_ids))
        )
        for rec in rec_result.scalars().all():
            record_lookup[rec.id] = {
                "loan_id": rec.loan_id,
                "borrower_name": rec.borrower_name,
                "loan_amount": rec.loan_amount,
                "interest_rate": rec.interest_rate,
            }

    # Generate explanations
    explanations = await generate_batch_explanations(exceptions, record_lookup)

    # Save to database
    for exc, expl in zip(exceptions, explanations):
        exc.ai_explanation = expl["explanation"]
        exc.status = "explained"
    await db.commit()

    return {"explanations": explanations, "count": len(explanations)}


# ── Bulk Operations ─────────────────────────────────
class BulkResolveRequest(BaseModel):
    exception_ids: List[str]
    action: str = "resolved"  # resolved or dismissed
    resolution_note: str = "Bulk resolution"


class BulkExplainRequest(BaseModel):
    exception_ids: List[str]


@router.post("/bulk-resolve")
async def bulk_resolve_exceptions(
    data: BulkResolveRequest,
    user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Resolve or dismiss multiple exceptions at once. Requires reviewer role."""
    if not data.exception_ids:
        raise HTTPException(status_code=400, detail="No exception IDs provided")
    if len(data.exception_ids) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 exceptions per batch")

    result = await db.execute(
        select(ValidationException).where(ValidationException.id.in_(data.exception_ids))
    )
    exceptions = result.scalars().all()

    if not exceptions:
        raise HTTPException(status_code=404, detail="No exceptions found")

    resolved_count = 0
    for exc in exceptions:
        exc.status = data.action
        exc.resolution_note = data.resolution_note
        exc.resolved_by = user.id
        exc.resolved_at = datetime.utcnow()
        resolved_count += 1

    await db.commit()

    # Log bulk action
    upload_id = exceptions[0].upload_id if exceptions else None
    await log_action(
        db, f"bulk_{data.action}",
        user.id, upload_id,
        {
            "exception_count": resolved_count,
            "action": data.action,
            "note": data.resolution_note,
        },
    )

    return {
        "resolved_count": resolved_count,
        "action": data.action,
        "message": f"{resolved_count} exceptions {data.action} successfully",
    }


@router.post("/bulk-explain")
async def bulk_explain_exceptions(
    data: BulkExplainRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI explanations for multiple exceptions at once."""
    if not data.exception_ids:
        raise HTTPException(status_code=400, detail="No exception IDs provided")
    if len(data.exception_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 exceptions per batch")

    result = await db.execute(
        select(ValidationException).where(ValidationException.id.in_(data.exception_ids))
    )
    exceptions = result.scalars().all()

    if not exceptions:
        raise HTTPException(status_code=404, detail="No exceptions found")

    # Build record context lookup
    record_ids = [e.record_id for e in exceptions if e.record_id]
    record_lookup = {}
    if record_ids:
        rec_result = await db.execute(
            select(LoanRecord).where(LoanRecord.id.in_(record_ids))
        )
        for rec in rec_result.scalars().all():
            record_lookup[rec.id] = {
                "loan_id": rec.loan_id,
                "borrower_name": rec.borrower_name,
                "loan_amount": rec.loan_amount,
                "interest_rate": rec.interest_rate,
            }

    # Generate explanations
    explanations = await generate_batch_explanations(exceptions, record_lookup)

    # Save to database
    for exc, expl in zip(exceptions, explanations):
        exc.ai_explanation = expl["explanation"]
        exc.status = "explained"
    await db.commit()

    return {"explanations": explanations, "count": len(explanations)}
