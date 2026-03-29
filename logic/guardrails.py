# """
# NeMo Guardrails Integration for ET AI Concierge
# ------------------------------------------------
# Uses NVIDIA NeMo Guardrails for topical control (financial queries only).
# Falls back gracefully to keyword-based guardrails if nemoguardrails
# is not installed (e.g., during development/testing without GPU).

# Phase 2 Task: Configure NeMo Guardrails for topical control and
# enforce Zero-trust data handling.
# """

# import os
# import logging
# from pathlib import Path

# logger = logging.getLogger(__name__)

# # ── Try importing NeMo Guardrails ────────────────────────────────────────────
# try:
#     from nemoguardrails import RailsConfig, LLMRails
#     NEMO_AVAILABLE = True
# except ImportError:
#     NEMO_AVAILABLE = False
#     logger.warning(
#         "nemoguardrails not installed. Falling back to keyword-based guardrails. "
#         "Install with: pip install nemoguardrails"
#     )

# # ── Config path ───────────────────────────────────────────────────────────────
# NEMO_CONFIG_PATH = Path(__file__).parent.parent / "nemo_guardrails_config"

# # ── Financial keyword list (fallback) ────────────────────────────────────────
# FINANCIAL_KEYWORDS = [
#     "invest", "money", "tax", "loan", "stock", "sip", "insurance",
#     "finance", "market", "wealth", "trading", "saving", "home",
#     "mutual fund", "portfolio", "equity", "debt", "nps", "elss",
#     "fd", "fixed deposit", "retirement", "dividend", "ipo", "nse",
#     "bse", "sebi", "rbi", "interest rate", "inflation", "budget",
#     "et prime", "et money", "et masterclass", "et markets",
#     "risk", "low", "medium", "high", "beginner", "experienced", "new to", "prefer", "appetite"
# ]

# # ── Zero-Trust Data Handling ──────────────────────────────────────────────────

# def sanitize_input(text: str) -> str:
#     """
#     Zero-Trust input sanitization:
#     - Strips leading/trailing whitespace
#     - Removes potential prompt injection patterns
#     - Truncates to safe max length
#     """
#     if not text:
#         return ""

#     MAX_INPUT_LENGTH = 500
#     text = text.strip()[:MAX_INPUT_LENGTH]

#     INJECTION_PATTERNS = [
#         "ignore previous instructions",
#         "ignore all instructions",
#         "disregard your instructions",
#         "you are now",
#         "act as",
#         "jailbreak",
#         "pretend you are",
#         "system prompt",
#         "forget everything",
#     ]
#     text_lower = text.lower()
#     for pattern in INJECTION_PATTERNS:
#         if pattern in text_lower:
#             logger.warning(f"Potential prompt injection blocked: '{pattern}'")
#             return ""

#     return text


# def mask_sensitive_data(data: dict) -> dict:
#     """
#     Zero-Trust: mask/redact sensitive fields before logging or storing.
#     Ensures PII is never exposed in logs.
#     """
#     SENSITIVE_KEYS = {"pan", "aadhaar", "account_number", "phone", "email", "dob"}
#     masked = {}
#     for key, value in data.items():
#         if key.lower() in SENSITIVE_KEYS:
#             masked[key] = "****REDACTED****"
#         else:
#             masked[key] = value
#     return masked


# # ── NeMo Guardrails wrapper ───────────────────────────────────────────────────

# class ETGuardrails:
#     """
#     Wraps NeMo Guardrails for the ET AI Concierge.
#     Enforces: only financial topics are allowed.
#     """

#     def __init__(self):
#         self.rails = None
#         if NEMO_AVAILABLE and NEMO_CONFIG_PATH.exists():
#             try:
#                 config = RailsConfig.from_path(str(NEMO_CONFIG_PATH))
#                 self.rails = LLMRails(config)
#                 logger.info("NeMo Guardrails loaded successfully.")
#             except Exception as e:
#                 logger.error(f"Failed to load NeMo Guardrails config: {e}")
#                 self.rails = None
#         else:
#             logger.info("Using keyword-based guardrails (NeMo not available).")

#     def is_allowed(self, text: str) -> bool:
#         """
#         Returns True if the query is financial/allowed, False otherwise.
#         Uses NeMo if available, else falls back to keyword check.
#         """
#         clean_text = sanitize_input(text)
#         if not clean_text:
#             return False

#         if self.rails:
#             try:
#                 response = self.rails.generate(
#                     messages=[{"role": "user", "content": clean_text}]
#                 )
#                 refusal_phrases = [
#                     "i am here to help with financial",
#                     "please ask a finance-related",
#                     "i can only assist with",
#                 ]
#                 response_lower = response.lower() if isinstance(response, str) else ""
#                 if any(phrase in response_lower for phrase in refusal_phrases):
#                     return False
#                 return True
#             except Exception as e:
#                 logger.error(f"NeMo guardrail check failed: {e}. Falling back.")

#         return _keyword_check(clean_text)

#     def get_refusal_message(self) -> str:
#         return (
#             "I am here to help with financial guidance and ET services. "
#             "Please ask a finance-related question."
#         )


# # ── Keyword fallback ──────────────────────────────────────────────────────────

# def _keyword_check(text: str) -> bool:
#     text_lower = text.lower()
#     return any(kw in text_lower for kw in FINANCIAL_KEYWORDS)


# # ── Public API ────────────────────────────────────────────────────────────────

# _guardrails_instance = ETGuardrails()


# def is_financial_query(text: str) -> bool:
#     """Public function — checks if query is finance-related."""
#     return _guardrails_instance.is_allowed(text)


# def get_guardrail_response() -> str:
#     """Public function — returns the standard refusal message."""
#     return _guardrails_instance.get_refusal_message()









"""
NeMo Guardrails Integration for ET AI Concierge
------------------------------------------------
Uses NVIDIA NeMo Guardrails for topical control (financial queries only).
Falls back gracefully to keyword-based guardrails if nemoguardrails
is not installed (e.g., during development/testing).

Also implements:
✔ Zero-trust input sanitization
✔ Sensitive data masking
✔ Clean integration with main_logic.py
✔ Demo-friendly rejection responses
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Try importing NeMo Guardrails ────────────────────────────────────────────
try:
    from nemoguardrails import RailsConfig, LLMRails
    NEMO_AVAILABLE = True
except ImportError:
    NEMO_AVAILABLE = False
    logger.warning(
        "nemoguardrails not installed. Falling back to keyword-based guardrails."
    )

# ── Config path ───────────────────────────────────────────────────────────────
NEMO_CONFIG_PATH = Path(__file__).parent.parent / "nemo_guardrails_config"

# ── Financial keyword list (fallback) ────────────────────────────────────────
FINANCIAL_KEYWORDS = [
    "invest", "money", "tax", "loan", "stock", "sip", "insurance",
    "finance", "market", "wealth", "trading", "saving", "portfolio",
    "mutual fund", "equity", "debt", "nps", "elss", "fd",
    "retirement", "dividend", "ipo", "nse", "bse", "sebi", "rbi",
    "interest rate", "inflation", "budget", "risk", "beginner"
]

# ── Zero-Trust Input Sanitization ─────────────────────────────────────────────

def sanitize_input(text: str) -> str:
    """
    Removes malicious prompt injection patterns and trims input.
    """
    if not text:
        return ""

    MAX_LENGTH = 500
    text = text.strip()[:MAX_LENGTH]

    BLOCK_PATTERNS = [
        "ignore previous instructions",
        "ignore all instructions",
        "act as",
        "jailbreak",
        "system prompt",
        "pretend you are",
        "forget everything",
    ]

    lower = text.lower()
    for pattern in BLOCK_PATTERNS:
        if pattern in lower:
            logger.warning(f"Blocked prompt injection pattern: {pattern}")
            return ""

    return text


# ── Sensitive Data Masking ────────────────────────────────────────────────────

def mask_sensitive_data(data):
    """
    Redacts sensitive fields before logging or storing.
    Handles both dict and str inputs.
    For strings, returns as-is (masking free text requires NLP).
    """
    if isinstance(data, str):
        # For string inputs, return as-is since masking requires structured data
        return data
    
    if isinstance(data, dict):
        SENSITIVE_KEYS = {"pan", "aadhaar", "account_number", "phone", "email", "dob"}
        masked = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_KEYS:
                masked[key] = "****REDACTED****"
            else:
                masked[key] = value
        return masked
    
    # For other types, return as-is
    return data


# ── Guardrails Engine ─────────────────────────────────────────────────────────

class ETGuardrails:
    """
    Handles finance-only topic control.
    """

    def __init__(self):
        self.rails = None

        if NEMO_AVAILABLE and NEMO_CONFIG_PATH.exists():
            try:
                config = RailsConfig.from_path(str(NEMO_CONFIG_PATH))
                self.rails = LLMRails(config)
                logger.info("NeMo Guardrails loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load NeMo Guardrails: {e}")
        else:
            logger.info("Using keyword-based guardrails (fallback mode).")

    # ─────────────────────────────────────────────────────────

    def is_financial_query(self, user_input: str) -> bool:
        """
        Main function used by main_logic.py
        Returns True if the query is finance-related.
        """

        clean_input = sanitize_input(user_input)

        if not clean_input:
            return False

        # If NeMo is available → use it
        if self.rails:
            try:
                response = self.rails.generate(
                    messages=[{"role": "user", "content": clean_input}]
                )

                refusal_phrases = [
                    "finance-related",
                    "financial questions",
                    "only assist with finance",
                ]

                response_text = str(response).lower()

                if any(phrase in response_text for phrase in refusal_phrases):
                    return False

                return True

            except Exception as e:
                logger.error(f"NeMo check failed, using fallback. {e}")

        # Fallback keyword-based detection
        clean_lower = clean_input.lower()
        return any(keyword in clean_lower for keyword in FINANCIAL_KEYWORDS)

    # ─────────────────────────────────────────────────────────

    def get_rejection_message(self) -> str:
        """
        Demo-friendly message when query is not finance-related.
        """

        return (
            "I’m designed to help only with financial guidance, investing, and ET services.\n\n"
            "Try asking something like:\n"
            "• Where should I invest as a beginner?\n"
            "• What is SIP and how does it work?\n"
            "• Best low-risk investment options in India"
        )


# ── Create a global instance (important for integration) ──────────────────────

guardrails = ETGuardrails()


# ── Public helper functions (used in main_logic.py) ───────────────────────────

def is_financial_query(text: str) -> bool:
    return guardrails.is_financial_query(text)


def get_guardrail_response() -> str:
    return guardrails.get_rejection_message()