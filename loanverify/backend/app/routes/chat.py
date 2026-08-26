"""Chat routes — AI copilot chat for follow-up questions about exceptions."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, LoanRecord, ValidationException
from ..auth import get_current_user
from ..services.ai_copilot import chat_with_copilot

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    record_id: Optional[str] = None
    upload_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    context_used: Dict[str, Any]


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat with the AI copilot about a specific record and its exceptions."""
    if not data.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    record_context = {}
    exceptions_context = []

    # If a record_id is provided, get its context
    if data.record_id:
        rec_result = await db.execute(
            select(LoanRecord).where(LoanRecord.id == data.record_id)
        )
        record = rec_result.scalar_one_or_none()
        if record:
            record_context = {
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
                "record_hash": record.record_hash,
            }

            # Get exceptions for this record
            exc_result = await db.execute(
                select(ValidationException).where(
                    ValidationException.record_id == record.id
                )
            )
            exceptions_context = [
                {
                    "field": e.field_name,
                    "rule": e.rule_name,
                    "severity": e.severity,
                    "message": e.message,
                    "actual_value": e.actual_value,
                    "expected_value": e.expected_value,
                    "status": e.status,
                }
                for e in exc_result.scalars().all()
            ]

    # Build message list for the AI
    messages = [{"role": m.role, "content": m.content} for m in data.messages]

    # Get AI response
    reply = await chat_with_copilot(messages, record_context, exceptions_context)

    return ChatResponse(
        reply=reply,
        context_used={
            "has_record": bool(record_context),
            "exception_count": len(exceptions_context),
            "record_id": data.record_id,
        },
    )
