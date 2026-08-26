"""AI Copilot service — generates human-readable explanations and chat for validation exceptions."""

import os
import json
from typing import Dict, Any, Optional, List
from functools import lru_cache

from openai import AsyncOpenAI

# Use environment variable or fallback to a mock mode
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_AI = bool(OPENAI_API_KEY)

if USE_AI:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# In-memory cache for explanations (keyed by rule_name + actual_value)
_explanation_cache: Dict[str, str] = {}

SYSTEM_PROMPT = """You are a Loan Data Verification AI assistant. Your job is to explain data quality issues in loan records to a human reviewer.

When given a validation exception and the full record context:
1. Explain the issue in plain, non-technical English
2. Explain WHY this is a problem for loan data quality
3. Suggest how to fix or resolve it
4. Rate the confidence that this is a real issue vs. a false positive

Be concise (2-4 sentences). Be helpful and specific. Reference the actual values."""

BATCH_EXPLAIN_PROMPT = """You are a Loan Data Verification AI assistant. Given a list of validation exceptions, provide a brief explanation for each.

For each exception, provide:
- A 1-2 sentence plain English explanation
- A suggested fix or resolution

Return a JSON array where each element has:
- "exception_id": the id
- "explanation": your explanation
- "suggested_fix": the suggested resolution
- "confidence": "high", "medium", or "low"

Exceptions:
{exceptions_json}"""

REVIEWER_NOTE_PROMPT = """You are a Loan Data Verification AI assistant. Write a brief summary for a human reviewer about the data quality of this loan upload.

Upload has {total_records} records with {exception_count} issues ({critical_count} critical, {warning_count} warnings).

Key issues found:
{top_issues}

Write a 3-5 sentence executive summary suitable for a reviewer to understand at a glance what needs attention."""


# ── Mock responses when no API key ───────────────────
MOCK_EXPLANATIONS = {
    "missing_loan_id": "This record is missing a Loan ID, which is a unique identifier required to track and reference the loan. Without it, this record cannot be reliably linked to any loan account. Please check the source data and populate the Loan ID field.",
    "interest_rate_outlier": "The interest rate of {actual} is outside the expected range for typical loans. This could indicate a data entry error (e.g., missing decimal point) or an unusually high-risk loan. Verify with the source system or origination documents.",
    "interest_rate_unusually_high": "The interest rate of {actual} is higher than typical but may still be valid for high-risk loans. Flag for manual review to confirm this is intentional.",
    "loan_amount_negative": "A negative loan amount ({actual}) is invalid. This likely indicates a data entry error or an adjustment entry that was miscoded. The amount should be positive.",
    "loan_amount_zero": "A zero-dollar loan amount is unusual and may indicate incomplete data or a test record that should be excluded.",
    "loan_amount_extreme": "The loan amount of {actual} is very large and should be verified against source documents.",
    "credit_score_range": "A credit score of {actual} falls outside the standard FICO range of 300-850. This suggests a data entry error — the score may have extra digits or missing digits.",
    "ltv_ratio_range": "The LTV ratio of {actual} is unusual. Standard LTV ratios are between 0 and 1.0 (0%-100%). Values above 1.0 indicate the loan exceeds the property value.",
    "loan_term_range": "A loan term of {actual} months is unusual. Most mortgage terms are 120-360 months (10-30 years). This may be an entry error.",
    "status_invalid": "The status value '{actual}' is not a recognized loan status. Standard statuses include: current, late, defaulted, paid_off.",
    "borrower_name_invalid": "The borrower name '{actual}' appears too short to be a valid name.",
    "state_invalid_format": "The state code '{actual}' doesn't match the expected 2-letter US state format (e.g., CA, NY).",
    "missing_borrower_name": "Borrower name is missing. This field is important for identification and communication purposes.",
    "missing_origination_date": "Origination date is missing. This field is needed to calculate loan age and track payment schedules.",
}


async def explain_exception(
    exception_id: str,
    field_name: str,
    rule_name: str,
    message: str,
    actual_value: Optional[str],
    record_context: Dict[str, Any],
) -> Dict[str, str]:
    """Generate an AI explanation for a single validation exception."""

    if USE_AI:
        try:
            user_msg = f"""Exception: {rule_name}
Field: {field_name}
Issue: {message}
Actual value: {actual_value}
Record context: {json.dumps(record_context, default=str, indent=2)}

Please explain this issue and suggest a resolution."""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=300,
                temperature=0.3,
            )
            explanation = response.choices[0].message.content.strip()
            return {
                "exception_id": exception_id,
                "explanation": explanation,
                "suggested_fix": "Review and correct based on AI suggestion above.",
            }
        except Exception as e:
            # Fall through to mock
            pass

    # Check cache first
    cache_key = f"{rule_name}:{actual_value}"
    if cache_key in _explanation_cache:
        return {
            "exception_id": exception_id,
            "explanation": _explanation_cache[cache_key],
            "suggested_fix": "Verify against source documents and update the record.",
        }

    # Mock response
    template = MOCK_EXPLANATIONS.get(rule_name, message)
    explanation = template.format(actual=actual_value or "N/A")
    _explanation_cache[cache_key] = explanation
    return {
        "exception_id": exception_id,
        "explanation": explanation,
        "suggested_fix": "Verify against source documents and update the record.",
    }


# ── AI Chat ─────────────────────────────────────────
CHAT_SYSTEM_PROMPT = """You are LoanVerify AI, a loan data verification assistant. You help human reviewers understand data quality issues in loan records.

You have access to:
- The current loan record being reviewed
- All exceptions found in that record
- The upload context (total records, quality score)

Guidelines:
- Be concise and helpful
- Explain financial concepts in plain English
- Suggest specific actions the reviewer can take
- If asked about false positives, evaluate whether the exception is truly an issue
- If asked about impact, explain what could go wrong if the issue is not fixed
- Never auto-resolve — always recommend human review
- Use the actual values from the record in your answers"""


async def chat_with_copilot(
    messages: List[Dict[str, str]],
    record_context: Dict[str, Any],
    exceptions_context: List[Dict[str, Any]],
) -> str:
    """Chat with the AI copilot about a specific record and its exceptions."""

    # Build context message
    context_msg = f"""Current record context:
{json.dumps(record_context, default=str, indent=2)}

Exceptions found in this record:
{json.dumps(exceptions_context, default=str, indent=2)}

Please answer the reviewer's question based on this context."""

    full_messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": context_msg},
    ] + messages

    if USE_AI:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                max_tokens=500,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI service temporarily unavailable. Error: {str(e)}"

    # Mock chat responses
    last_msg = messages[-1]["content"].lower() if messages else ""
    if "false positive" in last_msg:
        return (
            "Based on the record data, this exception appears to be a genuine issue. "
            f"The value {record_context.get('interest_rate', 'N/A')} is indeed outside normal ranges. "
            "However, I'd recommend checking with the original data source to confirm."
        )
    elif "impact" in last_msg or "consequence" in last_msg:
        return (
            "If this issue is not resolved:\n"
            "1. The loan may be incorrectly categorized in reports\n"
            "2. Risk calculations will be inaccurate\n"
            "3. Compliance audits may flag this record\n"
            "4. Downstream systems may reject or misprocess the data"
        )
    elif "fix" in last_msg or "resolve" in last_msg or "correct" in last_msg:
        return (
            "To fix this issue:\n"
            "1. Check the original loan documents or source system\n"
            "2. Verify the correct value with the data provider\n"
            "3. Update the record with the corrected value\n"
            "4. Document the change in the resolution note"
        )
    elif "explain" in last_msg or "what" in last_msg:
        return (
            f"This record has an exception for the field '{exceptions_context[0].get('field', 'unknown') if exceptions_context else 'unknown'}'. "
            f"The issue: {exceptions_context[0].get('message', 'No details') if exceptions_context else 'No details'}. "
            "This means the data in this field doesn't match expected patterns or ranges for loan data."
        )
    else:
        return (
            "I'm LoanVerify AI. I can help you understand data quality issues in this loan record. "
            "Try asking me:\n"
            "- Is this a false positive?\n"
            "- What's the impact if I don't fix this?\n"
            "- How should I fix this?\n"
            "- Explain this exception"
        )


async def generate_batch_explanations(
    exceptions: list,
    record_lookup: Dict[str, Dict[str, Any]],
) -> list:
    """Generate explanations for a batch of exceptions."""
    results = []
    for exc in exceptions:
        ctx = record_lookup.get(exc.record_id, {}) if exc.record_id else {}
        result = await explain_exception(
            exception_id=exc.id,
            field_name=exc.field_name,
            rule_name=exc.rule_name,
            message=exc.message,
            actual_value=exc.actual_value,
            record_context=ctx,
        )
        results.append(result)
    return results


async def generate_reviewer_summary(
    total_records: int,
    exception_count: int,
    critical_count: int,
    warning_count: int,
    top_issues: str,
) -> str:
    """Generate a summary note for a human reviewer."""

    if USE_AI:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data quality analyst writing executive summaries for loan data reviewers."},
                    {"role": "user", "content": REVIEWER_NOTE_PROMPT.format(
                        total_records=total_records,
                        exception_count=exception_count,
                        critical_count=critical_count,
                        warning_count=warning_count,
                        top_issues=top_issues,
                    )},
                ],
                max_tokens=300,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Mock summary
    return (
        f"This upload contains {total_records} loan records with {exception_count} data quality issues. "
        f"Of these, {critical_count} are critical issues that must be resolved before the data can be used. "
        f"There are {warning_count} warnings that require manual review. "
        f"Top issues include: {top_issues}. "
        f"Recommended action: resolve critical issues first, then review warnings with the source data provider."
    )
