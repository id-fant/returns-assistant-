import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')


# Configure Gemini once at module load time
# os.getenv reads from your .env file via python-dotenv
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_return_decision(product_name: str, reason: str) -> tuple[str, str]:
    """
    Sends return request details to Gemini and parses the response.

    Returns:
        (decision, explanation) — e.g. ("APPROVE", "Item was damaged on arrival.")

    The prompt is structured so Gemini responds in a predictable format
    that we can reliably parse. This is basic prompt engineering.
    """

    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = f"""
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

    try:
        response = model.generate_content(prompt)
        return _parse_response(response.text.strip())
    except Exception as e:
        # Fallback if the API call fails — don't crash the whole request
        print(f"[ai_engine] Gemini API error: {e}")
        return ("ESCALATE", "AI analysis unavailable. Manual review required.")


def _parse_response(raw: str) -> tuple[str, str]:
    """
    Parses the structured response from Gemini.

    Expected format:
        DECISION: APPROVE
        EXPLANATION: The item arrived damaged so a refund is warranted.

    Falls back gracefully if the format is unexpected.
    """
    decision = "ESCALATE"
    explanation = raw  # Default: store the full raw text if parsing fails

    lines = raw.splitlines()
    for line in lines:
        if line.startswith("DECISION:"):
            raw_decision = line.replace("DECISION:", "").strip().upper()
            # Only accept known values
            if raw_decision in ("APPROVE", "EXCHANGE", "ESCALATE"):
                decision = raw_decision
        elif line.startswith("EXPLANATION:"):
            explanation = line.replace("EXPLANATION:", "").strip()

    return (decision, explanation)
