"""
Gemini wrapper for the returns assistant.

The view layer calls `get_return_decision(product, reason)` and receives a
`(decision, explanation)` tuple. Decisions are restricted to the values in
`ReturnRequest.Decision` so the model's choices are the single source of truth.
"""

import logging
import os
import re
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

from .models import ReturnRequest

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Decisions Gemini is allowed to emit. PENDING is reserved for the pre-AI
# default on the model and is not a valid AI output.
_VALID_AI_DECISIONS = {
    ReturnRequest.Decision.APPROVE,
    ReturnRequest.Decision.EXCHANGE,
    ReturnRequest.Decision.ESCALATE,
}

_PROMPT_TEMPLATE = """\
You are a returns assistant for an eCommerce platform called EcoReturns.
A customer wants to return a product. Analyse the request and decide what to do.

Product: {product_name}
Customer reason: {reason}

Respond in EXACTLY this format, with nothing else:
DECISION: <one of: APPROVE, EXCHANGE, ESCALATE>
EXPLANATION: <one sentence explaining why>

Rules:
- APPROVE if the reason is clearly valid (damaged, wrong item, defective, never arrived)
- EXCHANGE if the issue could be resolved with a replacement or different size
- ESCALATE if the reason is vague, suspicious, or outside normal return policy
"""

_DECISION_RE = re.compile(r"^\s*DECISION\s*:\s*(\w+)", re.IGNORECASE | re.MULTILINE)
_EXPLANATION_RE = re.compile(
    r"^\s*EXPLANATION\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

_model: genai.GenerativeModel | None = None


def _get_model() -> genai.GenerativeModel:
    """Configure Gemini and cache the model on first use."""
    global _model
    if _model is not None:
        return _model

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    # transport="rest" avoids gRPC SSL handshake failures on Windows where
    # the system trust store isn't picked up by gRPC's bundled OpenSSL.
    genai.configure(api_key=api_key, transport="rest")
    _model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={
            # Low temperature → consistent, near-deterministic decisions
            "temperature": 0.1,
            # Gemini 2.5 models use "thinking" tokens that count against this
            # budget before any visible output is emitted. Keep it generous so
            # the EXPLANATION line is never truncated mid-sentence.
            "max_output_tokens": 1024,
        },
    )
    return _model


def get_return_decision(product_name: str, reason: str) -> tuple[str, str]:
    """
    Ask Gemini to classify a return request.

    Returns (decision, explanation). On any failure the decision is ESCALATE
    so a human can review — the request is never silently dropped.
    """
    prompt = _PROMPT_TEMPLATE.format(product_name=product_name, reason=reason)

    try:
        response = _get_model().generate_content(prompt)
        raw = (response.text or "").strip()
        if not raw:
            raise ValueError("Empty response from Gemini")
        return _parse_response(raw)
    except Exception:
        logger.exception("Gemini call failed; escalating for manual review")
        return (
            ReturnRequest.Decision.ESCALATE,
            "AI analysis unavailable. Manual review required.",
        )


def _parse_response(raw: str) -> tuple[str, str]:
    """Pull DECISION and EXPLANATION lines out of the Gemini response."""
    decision = ReturnRequest.Decision.ESCALATE
    explanation = ""

    m = _DECISION_RE.search(raw)
    if m:
        candidate = m.group(1).strip().upper()
        if candidate in _VALID_AI_DECISIONS:
            decision = candidate

    m = _EXPLANATION_RE.search(raw)
    if m:
        explanation = m.group(1).strip()
    else:
        # Strip out the DECISION line — anything left is the model's prose.
        # Drop short scraps (likely a truncated "EXPLAN…") so we don't
        # save junk into the database.
        leftover = _DECISION_RE.sub("", raw).strip()
        leftover = re.sub(r"^\s*EXPLANATION\s*:?\s*", "", leftover, flags=re.IGNORECASE)
        explanation = leftover if len(leftover) >= 20 else (
            "AI did not return an explanation. Manual review recommended."
        )

    return decision, explanation
