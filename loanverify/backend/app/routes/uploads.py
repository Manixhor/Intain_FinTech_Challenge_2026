"""Upload routes — file upload, processing, and listing."""

import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models import User, LoanUpload, LoanRecord, ValidationException
from ..schemas import UploadResponse, UploadSummary, LoanRecordResponse, ExceptionResponse
from ..auth import get_current_user, require_analyst
from ..services.ingestion import ingest_file, normalize_column_name
from ..services.validation import validate_records, compute_quality_score
from ..services.audit import log_action

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


# ── CSV Preview ─────────────────────────────────────
class PreviewResponse(BaseModel):
    columns: List[str]
    total_rows: int
    preview_rows: List[dict]
    column_mappings: List[dict]  # {original, normalized, data_type, sample_values}
    detected_types: dict


@router.post("/preview")
async def preview_csv(
    file: UploadFile = File(...),
    user: User = Depends(require_analyst),
):
    """Preview a CSV/Excel file before processing — shows columns, mappings, and sample rows."""
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Parse file
    try:
        if file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    df.columns = [c.strip() for c in df.columns]

    # Build column mappings
    mappings = []
    for col in df.columns:
        norm = normalize_column_name(col)
        # Detect data type
        non_null = df[col].dropna()
        if len(non_null) == 0:
            dtype = "empty"
        elif pd.api.types.is_numeric_dtype(non_null):
            if non_null.apply(lambda x: x == int(x)).all():
                dtype = "integer"
            else:
                dtype = "float"
        else:
            dtype = "string"

        # Sample values (first 3 non-null)
        samples = [str(v) for v in non_null.head(3).tolist()]

        mappings.append({
            "original": col,
            "normalized": norm or "(unmapped)",
            "data_type": dtype,
            "sample_values": samples,
            "non_null_count": int(len(non_null)),
            "null_count": int(len(df) - len(non_null)),
        })

    # Preview rows (first 5)
    preview = df.head(5).fillna("").to_dict(orient="records")
    # Convert any non-serializable values to strings
    for row in preview:
        for k, v in row.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                row[k] = str(v)

    return PreviewResponse(
        columns=list(df.columns),
        total_rows=len(df),
        preview_rows=preview,
        column_mappings=mappings,
        detected_types={m["original"]: m["data_type"] for m in mappings},
    )


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV or Excel loan tape file for processing and validation."""
    # Validate file type
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Create upload record
    upload = LoanUpload(
        filename=f"{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}",
        original_filename=file.filename,
        uploaded_by=user.id,
        status="processing",
    )
    db.add(upload)
    await db.flush()

    await log_action(db, "file_uploaded", user.id, upload.id, {
        "filename": file.filename,
        "file_size": len(content),
    })

    try:
        # Ingest and normalize data
        records, raw_rows = await ingest_file(content, file.filename, upload, db, user.id)

        # Validate records
        exceptions = await validate_records(records, upload, db)

        # Compute quality score
        score = compute_quality_score(len(records), exceptions)
        upload.quality_score = score
        upload.record_count = len(records)
        upload.status = "completed"
        upload.completed_at = datetime.utcnow()

        await db.commit()
    except Exception as e:
        upload.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    await db.refresh(upload)

    await log_action(db, "file_processed", user.id, upload.id, {
        "record_count": len(records),
        "exception_count": len(exceptions),
        "quality_score": score,
    })

    return UploadResponse.model_validate(upload)


@router.get("", response_model=List[UploadResponse])
async def list_uploads(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all uploads. Analysts see only their own; reviewers/admins see all."""
    from ..models import UserRole

    query = select(LoanUpload)
    if user.role == UserRole.ANALYST:
        query = query.where(LoanUpload.uploaded_by == user.id)
    query = query.order_by(LoanUpload.created_at.desc())

    result = await db.execute(query)
    uploads = result.scalars().all()
    return [UploadResponse.model_validate(u) for u in uploads]


@router.get("/{upload_id}", response_model=UploadSummary)
async def get_upload_summary(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed upload summary with exception counts."""
    result = await db.execute(select(LoanUpload).where(LoanUpload.id == upload_id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Count exceptions by severity
    counts = {}
    for severity in ["critical", "warning", "info"]:
        result = await db.execute(
            select(func.count()).where(
                ValidationException.upload_id == upload_id,
                ValidationException.severity == severity,
            )
        )
        counts[severity] = result.scalar()

    total_exc = sum(counts.values())

    resolved_result = await db.execute(
        select(func.count()).where(
            ValidationException.upload_id == upload_id,
            ValidationException.status.in_(["resolved", "dismissed"]),
        )
    )
    resolved = resolved_result.scalar()

    return UploadSummary(
        upload=UploadResponse.model_validate(upload),
        total_records=upload.record_count,
        total_exceptions=total_exc,
        critical_count=counts["critical"],
        warning_count=counts["warning"],
        info_count=counts["info"],
        resolved_count=resolved,
        quality_score=upload.quality_score,
    )


@router.get("/{upload_id}/records", response_model=List[LoanRecordResponse])
async def get_upload_records(
    upload_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all normalized loan records for an upload."""
    result = await db.execute(
        select(LoanRecord)
        .where(LoanRecord.upload_id == upload_id)
        .order_by(LoanRecord.row_index)
    )
    records = result.scalars().all()
    return [LoanRecordResponse.model_validate(r) for r in records]


@router.get("/{upload_id}/exceptions", response_model=List[ExceptionResponse])
async def get_upload_exceptions(
    upload_id: str,
    severity: str = None,
    status: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all validation exceptions for an upload, optionally filtered."""
    query = select(ValidationException).where(ValidationException.upload_id == upload_id)

    if severity:
        query = query.where(ValidationException.severity == severity)
    if status:
        query = query.where(ValidationException.status == status)

    query = query.order_by(ValidationException.created_at.desc())
    result = await db.execute(query)
    exceptions = result.scalars().all()
    return [ExceptionResponse.model_validate(e) for e in exceptions]
