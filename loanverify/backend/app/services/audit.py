"""Audit logging service — immutable record of all actions in the system."""

from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuditLog


async def log_action(
    db: AsyncSession,
    action: str,
    user_id: Optional[str] = None,
    upload_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Create an audit log entry for any significant action."""
    entry = AuditLog(
        upload_id=upload_id,
        user_id=user_id,
        action=action,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    return entry
