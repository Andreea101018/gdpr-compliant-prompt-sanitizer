import re

# ============================================================
# 1. IBAN (high priority)
# ============================================================
IBAN_PATTERN = re.compile(
    r"\b[A-Z]{2}[0-9]{2}(?:[ ]?[A-Z0-9]{4}){3,7}\b",
    re.IGNORECASE
)

# ============================================================
# 2. CREDIT CARD
# ============================================================
CREDIT_CARD_PATTERN = re.compile(
    r"\b(?:" 
    r"4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"                # Visa
    r"|5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"         # MasterCard
    r"|3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}"                     # Amex
    r")\b"
)

# ============================================================
# 3. EMAIL
# ============================================================
EMAIL_PATTERN = re.compile(
    r"(?!\.)[A-Za-z0-9._%+-]+(?<!\.)@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}",
    re.IGNORECASE
)

# ============================================================
# 4. PHONE NUMBER
# ============================================================
PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)                      # do not allow preceding digit
    (
        # +1 415 983 2231 or +45 20 11 55 66
        \+?\d{1,3}[-\s.]?\d{1,4}[-\s.]?\d{2,4}[-\s.]?\d{2,4}
        |
        # (415) 983-2231
        \(\d{3}\)\s*\d{3}[-\s.]?\d{4}
        |
        # 415-983-2231 or 415 983 2231 or 415.983.2231
        \d{3}[-\s.]?\d{3}[-\s.]?\d{4}
    )
    (?!\d)                      # do not allow trailing digit
    """,
    re.VERBOSE
)


# ============================================================
# 5. FINANCIAL AMOUNTS
# ============================================================
FINANCIAL_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(EUR|USD|€|\$|euros?|dollars?|pounds?)\b",
    re.IGNORECASE
)

# ============================================================
# 6. STREET ADDRESSES
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
# 7. SECURITY TOKENS
# ============================================================
SECURITY_PATTERN = re.compile(
    r"\b(?:otp\d+|code\d+|token\d+|passcode\d+|key\d+|alpha\d+|sec\d+)\b",
    re.IGNORECASE
)

# ============================================================
# 8. HEALTH TERMS
# ============================================================
HEALTH_KEYWORDS = [
    "asthma", "diabetes", "depression", "autism",
    "hypertension", "migraine", "migraines",
    "anxiety", "cancer", "flu", "covid"
]

HEALTH_PATTERN = re.compile(
    r"\b(" + "|".join(map(re.escape, HEALTH_KEYWORDS)) + r")\b",
    re.IGNORECASE
)

# ============================================================
# 9. LANDMARKS / WELL-KNOWN LOCATIONS
# ============================================================
LANDMARK_KEYWORDS = [
    "Times Square", "Central Park", "Union Square", "Piccadilly Circus",
    "Trafalgar Square", "Golden Gate Bridge", "Hyde Park",
    "Silicon Valley", "Eiffel Tower", "Grand Central Station"
]

LANDMARK_PATTERN = re.compile(
    r"\b(" + "|".join(map(re.escape, LANDMARK_KEYWORDS)) + r")\b",
    re.IGNORECASE
)

# ============================================================
# 10. PERSON fallback (capitalized first names)
# ============================================================
FIRST_NAME_PATTERN = re.compile(
    r"\b([A-Za-z][a-zA-Z]{2,20})\b"
)


# Words that should NOT be treated as names
COMMON_WORDS = {
    "Street", "Road", "Drive", "Lane", "Way", "Court", "Office",
    "Invoice", "Emergency", "Budget", "Security", "Park", "Gate",
    "Meeting", "Contact", "Please", "Email", "Doctor", "Prof", "Dr"
}

ID_PATTERN = re.compile(
    r"""
    (?:
        (?:badge|employee|staff|user|id|ticket|ref|reference)   # keywords
        [\s:#]*                                                # separators
        (\d{4,10})                                             # 4–10 digit ID
    )
    """,
    re.IGNORECASE | re.VERBOSE
)

# Ordered structured patterns
STRUCTURED_PATTERNS = {
    "IBAN": IBAN_PATTERN,
    "CREDIT_CARD": CREDIT_CARD_PATTERN,
    "EMAIL": EMAIL_PATTERN,
    "PHONE": PHONE_PATTERN,
    "ID": ID_PATTERN,
}

SAFE_FIRST_NAMES = {
    "Sarah", "Daniel", "Anna", "John", 
    "Liam", "Sofia", "Victor", "Laura",
    "Andrew", "Michael", "James", "Robert", "David", "Mark",
    "Paul", "Peter", "George", "Emma", "Emily", "Hannah",
    "Oliver", "Lucas", "Noah", "Isabella", "Sophie",
    "Björn", "Lukasz", "Łukasz", "Hans", "Jean", "Paul",
    "O’Reilly", "Constantin", "Popescu", "Evans", "Ahmad",
}
# ============================================================
# 11. EMPLOYEE / BADGE / INTERNAL IDS
# ============================================================




__all__ = [
    "IBAN_PATTERN", "CREDIT_CARD_PATTERN", "EMAIL_PATTERN", "PHONE_PATTERN",
    "FINANCIAL_PATTERN", "ADDRESS_PATTERN", "SECURITY_PATTERN", "HEALTH_PATTERN",
    "LANDMARK_PATTERN", "FIRST_NAME_PATTERN", "COMMON_WORDS", "STRUCTURED_PATTERNS","SAFE_FIRST_NAMES","ID_PATTERN",
]
