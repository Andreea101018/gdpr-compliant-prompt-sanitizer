import re
from .regex_patterns import (
    STRUCTURED_PATTERNS,
    ADDRESS_PATTERN,
    FINANCIAL_PATTERN,
    SECURITY_PATTERN,
    HEALTH_PATTERN,
    LANDMARK_PATTERN,
    FIRST_NAME_PATTERN,
    COMMON_WORDS,
    SAFE_FIRST_NAMES, 
    ID_PATTERN, # strict person fallback list
)

# ---------------- PIN ----------------
PIN_PATTERN = re.compile(
    r"\bpin\s*(?:is|code)?\s*(\d{3,6})\b",
    re.IGNORECASE
)

# ---------------- AGE ----------------
AGE_PATTERN = re.compile(
    r"\b(?:aged\s+)?(\d{1,2})(?:\s*(years old|yrs|years|yo|y/o))\b",
    re.IGNORECASE
)


def mask_structured_data(text, notices):
    updated = text

    # ------------------------------------------------------------
    # 1. PIN
    # ------------------------------------------------------------
    def pin_digits(m):
        notices.append({
            "type": "PIN",
            "text": m.group(1),
            "reason": "regex"
        })
        return "pin is [PIN_REMOVED]"

    updated = PIN_PATTERN.sub(pin_digits, updated)

    # ------------------------------------------------------------
    # 2. HIGH-PRIORITY STRUCTURED PII
    # ------------------------------------------------------------
    for label, pattern in STRUCTURED_PATTERNS.items():
        for m in pattern.finditer(updated):
            notices.append({
                "type": label,
                "text": m.group(0),
                "reason": "regex"
            })
        updated = pattern.sub(f"[{label}_REMOVED]", updated)

    # ------------------------------------------------------------
    # 3. FINANCIAL
    # ------------------------------------------------------------
    for m in FINANCIAL_PATTERN.finditer(updated):
        notices.append({
            "type": "FINANCIAL",
            "text": m.group(0),
            "reason": "regex"
        })
    updated = FINANCIAL_PATTERN.sub("[FINANCIAL_REMOVED]", updated)

    # ------------------------------------------------------------
    # 4. ADDRESS
    # ------------------------------------------------------------
    for m in ADDRESS_PATTERN.finditer(updated):
        notices.append({
            "type": "ADDRESS",
            "text": m.group(0),
            "reason": "regex"
        })
    updated = ADDRESS_PATTERN.sub("[ADDRESS_REMOVED]", updated)

    # ------------------------------------------------------------
    # 5. AGE
    # ------------------------------------------------------------
    def repl_age(m):
        notices.append({
            "type": "AGE",
            "text": m.group(0),
            "reason": "regex"
        })
        return m.group(0).replace(m.group(1), "[AGE_REMOVED]")

    updated = AGE_PATTERN.sub(repl_age, updated)

    # ------------------------------------------------------------
    # 6. SECURITY
    # ------------------------------------------------------------
    for m in SECURITY_PATTERN.finditer(updated):
        notices.append({
            "type": "SECURITY",
            "text": m.group(0),
            "reason": "regex"
        })
    updated = SECURITY_PATTERN.sub("[SECURITY_REMOVED]", updated)

    # ------------------------------------------------------------
    # 7. HEALTH
    # ------------------------------------------------------------
    for m in HEALTH_PATTERN.finditer(updated):
        notices.append({
            "type": "HEALTH",
            "text": m.group(0),
            "reason": "regex"
        })
    updated = HEALTH_PATTERN.sub("[HEALTH_REMOVED]", updated)

    # ------------------------------------------------------------
    # 8. LANDMARKS
    # ------------------------------------------------------------
    for m in LANDMARK_PATTERN.finditer(updated):
        notices.append({
            "type": "LOCATION",
            "text": m.group(0),
            "reason": "regex"
        })
    updated = LANDMARK_PATTERN.sub("[LOCATION_REMOVED]", updated)

    # ------------------------------------------------------------
    # 9. PERSON FALLBACK (STRICT GDPR-SAFE MODE)
    # ------------------------------------------------------------
    for m in FIRST_NAME_PATTERN.finditer(updated):

        word = m.group(1)

        # Skip common non-names
        if word in COMMON_WORDS:
            continue

        # Normalize casing for whitelist match
        if word.capitalize() not in SAFE_FIRST_NAMES:
            continue

        # Check local overlap with placeholders ONLY
        start, end = m.span()
        surrounding = updated[max(0, start-1): min(len(updated), end+1)]

        if any(tag in surrounding for tag in [
            "[PERSON_REMOVED]", "[FINANCIAL_REMOVED]", "[EMAIL_REMOVED]",
            "[PHONE_REMOVED]", "[ADDRESS_REMOVED]", "[SECURITY_REMOVED]"
        ]):
            continue

        # Mask and record
        notices.append({
            "type": "PERSON",
            "text": word,
            "reason": "regex"
        })

        updated = re.sub(
            rf"\b{re.escape(word)}\b",
            "[PERSON_REMOVED]",
            updated
        )




    return updated
