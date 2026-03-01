import re

# ============================================================
# SAFE FIRST NAMES (used by ML layer to reduce false positives)
# ============================================================

SAFE_FIRST_NAMES = {
    "John", "Michael", "David", "James",
    "Robert", "Daniel", "Anna", "Maria",
    "Laura", "Emma", "Olivia", "Sophia",
    "Liam", "Noah", "Lucas", "Mark",
    "Paul", "Peter", "Sarah", "Victor"
}

# ============================================================
# HEALTH TERMS (Contextual masking)
# ============================================================

HEALTH_TERMS = [
    "cancer",
    "diabetes",
    "hiv",
    "aids",
    "asthma",
    "stroke",
    "tumor",
    "depression",
    "anxiety",
    "covid",
    "covid-19",
    "heart disease",
]

HEALTH_PATTERN = re.compile(
    r"\b(" + "|".join(HEALTH_TERMS) + r")\b",
    re.IGNORECASE
)

# ============================================================
# 1️⃣ IBAN (Structured – tightened)
# ============================================================

IBAN_PATTERN = re.compile(
    r"\b(?:IBAN\s*)?[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b",
    re.IGNORECASE
)


# ============================================================
# 2️⃣ CREDIT CARD (Regex + Luhn validation required)
# ============================================================

CREDIT_CARD_PATTERN = re.compile(
    r"\b(?:"
    r"4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"        # Visa
    r"|5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}" # MasterCard
    r"|3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}"              # Amex
    r")\b"
)


def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", card_number)]
    checksum = 0
    parity = len(digits) % 2

    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


# ============================================================
# 3️⃣ EMAIL
# ============================================================

EMAIL_PATTERN = re.compile(
    r"(?!\.)[A-Za-z0-9._%+-]+(?<!\.)@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}",
    re.IGNORECASE
)


# ============================================================
# 4️⃣ PHONE NUMBER (Validated via digit count)
# ============================================================

PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (
        \+?\d{1,3}[-\s.]?\d{1,4}[-\s.]?\d{2,4}[-\s.]?\d{2,4}
        |
        \(\d{3}\)\s*\d{3}[-\s.]?\d{4}
        |
        \d{3}[-\s.]?\d{3}[-\s.]?\d{4}
    )
    (?!\d)
    """,
    re.VERBOSE
)


def valid_phone_number(phone: str) -> bool:
    digits_only = re.sub(r"\D", "", phone)

    # Too short or too long
    if not (8 <= len(digits_only) <= 12):
        return False

    # Reject sequences that look like credit cards (4-4-4 or 4-4-4-4)
    if re.match(r"^\d{4}[-\s]?\d{4}[-\s]?\d{4,4}", phone):
        return False

    return True


# ============================================================
# 5️⃣ FINANCIAL AMOUNTS (Improved coverage)
# ============================================================

FINANCIAL_PATTERN = re.compile(
    r"""
    \b
    (?:€|\$|EUR|USD|euros?|dollars?|pounds?)
    \s*
    \d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?
    \b
    """,
    re.IGNORECASE | re.VERBOSE
)


# ============================================================
# 6️⃣ STREET ADDRESS (Structured only)
# ============================================================

ADDRESS_PATTERN = re.compile(
    r"""
    \b
    \d{1,5}[A-Za-z]?
    \s+
    [A-Za-zÀ-ÿ0-9.\- ]+?
    \s+
    (Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Way|Boulevard|Blvd|Drive|Dr|Court|Ct)
    \b
    """,
    re.IGNORECASE | re.VERBOSE
)


# ============================================================
# 7️⃣ SECURITY TOKENS (Structured numeric tokens only)
# ============================================================

SECURITY_PATTERN = re.compile(
    r"\b(?:otp|code|token|passcode|key|sec)[\s:-]*(\d{4,10})\b",
    re.IGNORECASE
)


# ============================================================
# 8️⃣ STRUCTURED ID (Employee / Ticket / Reference)
# ============================================================

ID_PATTERN = re.compile(
    r"""
    (?:
        (?:badge|employee|staff|user|id|ticket|ref|reference)
        [\s:#-]*
        (\d{4,12})
    )
    """,
    re.IGNORECASE | re.VERBOSE
)

ZIPCODE_PATTERN = re.compile(r"\b\d{4}\b(?=\s|$)")

AGE_PATTERN = re.compile(
    r"\b(\d{1,3})\s*(years?\s*old|y/o)\b",
    re.IGNORECASE
)


# ============================================================
# ORDERED STRUCTURED PATTERNS
# ============================================================

STRUCTURED_PATTERNS = {
    "IBAN": IBAN_PATTERN,
    "CREDIT_CARD": CREDIT_CARD_PATTERN,
    "EMAIL": EMAIL_PATTERN,
    "PHONE": PHONE_PATTERN,
    "ID": ID_PATTERN,
    "AGE": AGE_PATTERN,
    "ZIPCODE": ZIPCODE_PATTERN,
    "ADDRESS": ADDRESS_PATTERN,
    "SECURITY_TOKEN": SECURITY_PATTERN,
    "FINANCIAL_AMOUNT": FINANCIAL_PATTERN,
}


__all__ = [
    "IBAN_PATTERN",
    "CREDIT_CARD_PATTERN",
    "EMAIL_PATTERN",
    "PHONE_PATTERN",
    "FINANCIAL_PATTERN",
    "ADDRESS_PATTERN",
    "SECURITY_PATTERN",
    "ID_PATTERN",
    "STRUCTURED_PATTERNS",
    "luhn_check",
    "valid_phone_number",
    "SAFE_FIRST_NAMES",
    "HEALTH_PATTERN",
]