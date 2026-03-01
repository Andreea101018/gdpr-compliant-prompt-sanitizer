from .ner_model import TransformerNER
from .regex_patterns import SAFE_FIRST_NAMES
import re

NER_MODEL = TransformerNER()

PASSWORD_KEYWORDS = {"password", "passcode"}

ML_LABEL_MAPPING = {
    "GIVENNAME": ("PERSON", "PERSONAL_IDENTIFIER"),
    "SURNAME": ("PERSON", "PERSONAL_IDENTIFIER"),
    "DATEOFBIRTH": ("DATE_OF_BIRTH", "PERSONAL_IDENTIFIER"),
    "SOCIALNUM": ("NATIONAL_ID", "PERSONAL_IDENTIFIER"),
    "DRIVERLICENSENUM": ("DRIVER_LICENSE", "PERSONAL_IDENTIFIER"),
    "IDCARDNUM": ("ID_CARD", "PERSONAL_IDENTIFIER"),
    "TAXNUM": ("TAX_NUMBER", "PERSONAL_IDENTIFIER"),
    "ACCOUNTNUM": ("ACCOUNT_NUMBER", "FINANCIAL_DATA"),
    "CREDITCARDNUMBER": ("CREDIT_CARD", "FINANCIAL_DATA"),
    "EMAIL": ("EMAIL", "CONTACT_DATA"),
    "TELEPHONENUM": ("PHONE", "CONTACT_DATA"),
    "USERNAME": ("USERNAME", "PERSONAL_IDENTIFIER"),
    "CITY": ("LOCATION", "LOCATION_DATA"),
    "STREET": ("ADDRESS", "LOCATION_DATA"),
    "ZIPCODE": ("ZIPCODE", "LOCATION_DATA"),
    "BUILDINGNUM": ("ADDRESS_NUMBER", "LOCATION_DATA"),
}
# ------------------------------------------------------------
# Extract password after keyword
# ------------------------------------------------------------
def extract_password_value(text):
    m = re.search(
        r"\b(password|passcode)\s*(is|=|:)\s*([^\s]+)",
        text,
        flags=re.IGNORECASE,
    )
    return m.group(3) if m else None


# ------------------------------------------------------------
# Heuristic: detect strong/secret-looking tokens
# ------------------------------------------------------------
def looks_like_password(token):
    if len(token) < 8:
        return False

    has_upper = any(c.isupper() for c in token)
    has_lower = any(c.islower() for c in token)
    has_digit = any(c.isdigit() for c in token)
    has_symbol = any(not c.isalnum() for c in token)

    score = has_upper + has_lower + has_digit + has_symbol
    return score >= 3


# ------------------------------------------------------------
# Normalize BIO label
# ------------------------------------------------------------
def normalize_label(label):
    if label.startswith("B-") or label.startswith("I-"):
        return label[2:]
    return label
def merge_bio_entities(raw_entities):
    """
    Merge B- / I- token sequences into full entity spans.
    Works for both tuple and dict formats.
    """

    merged = []
    current = None

    for entity in raw_entities:

        # Support tuple format
        if isinstance(entity, tuple):
            word, label = entity

        # Support dict format (HF pipeline style)
        elif isinstance(entity, dict):
            word = entity.get("word") or entity.get("text")
            label = entity.get("entity") or entity.get("label")

        else:
            continue

        if not word or not label:
            continue

        # Normalize SentencePiece/XLM-R tokens
        if word.startswith("▁"):
            word = word[1:]

        # BIO handling
        if label.startswith("B-"):
            if current:
                merged.append(current)
            current = {
                "text": word,
                "label": label[2:]
            }

        elif label.startswith("I-") and current and current["label"] == label[2:]:
            current["text"] += word

        else:
            if current:
                merged.append(current)
            current = None

    if current:
        merged.append(current)

    return merged

# ------------------------------------------------------------
# ML Masking Layer
# ------------------------------------------------------------
def ml_mask(text, notices):

    # ------------------------------------------------------------
    # 0) Freeze existing placeholders
    # ------------------------------------------------------------
    frozen_map = {}
    idx = 0

    for match in re.findall(r"\[[A-Z_]+_REMOVED\]", text):
        placeholder = f"§FROZEN_{idx}§"
        frozen_map[placeholder] = match
        text = text.replace(match, placeholder)
        idx += 1

    # ------------------------------------------------------------
    # 1) Strong password keyword masking
    # ------------------------------------------------------------
    pwd_val = extract_password_value(text)
    if pwd_val:
        notices.append({"type": "PASSWORD", "text": pwd_val, "reason": "regex"})
        text = text.replace(pwd_val, "[PASSWORD_REMOVED]")

    # ------------------------------------------------------------
    # 2) Run NER
    # ------------------------------------------------------------
    raw_entities = NER_MODEL.predict(text)
    updated = text

    regex_spans = [n["text"] for n in notices if n["reason"] == "regex"]

    COMMON_STOPWORDS = {
        "and", "or", "from", "to", "in", "at", "for", "with",
        "call", "meet", "send", "near", "park", "road",
        "street", "office", "city", "team", "budget",
        "update", "morning", "evening"
    }

    # ------------------------------------------------------------
    # 3) Iterate ML predictions (robust format handling)
    # ------------------------------------------------------------
    for entity in raw_entities:

        # Support tuple format: ("John", "B-PERSON")
        if isinstance(entity, tuple):
            word, label = entity

        # Support dict format from HF pipeline
        elif isinstance(entity, dict):
            word = entity.get("word") or entity.get("text")
            label = entity.get("entity") or entity.get("label")

        else:
            continue

        if not word or not label:
            continue

        label = normalize_label(label)

        clean = word.strip()

        # Basic sanitation
        if not clean:
            continue

        if clean.lower() in COMMON_STOPWORDS:
            continue

        # Skip SentencePiece artifacts (XLM-R uses ▁)
        if clean.startswith("▁"):
            clean = clean[1:]

        if any(clean in span for span in regex_spans):
            continue

        if any(ph in clean for ph in frozen_map.keys()):
            continue

        # Ensure full word boundary exists
        if clean not in updated:
            continue

        # ------------------------------------------------------------
        # PASSWORD logic (only if model supports it)
        # ------------------------------------------------------------
        if label == "PASSWORD":
            if looks_like_password(clean):
                notices.append({
                    "type": "PASSWORD",
                    "text": clean,
                    "reason": "ml"
                })
                updated = re.sub(
                    rf"\b{re.escape(clean)}\b",
                    "[PASSWORD_REMOVED]",
                    updated
                )
            continue



        # ------------------------------------------------------------
        # ------------------------------------------------------------
        # Strict LOCATION validation (extra validation only)
        # ------------------------------------------------------------
        if label in {"CITY", "LOCATION", "STREET"}:
            if not clean[0].isupper():
                continue
            if clean.lower() in COMMON_STOPWORDS:
                continue

        # ------------------------------------------------------------
        # General ML label mapping (ALL labels)
        # ------------------------------------------------------------
        mapped = ML_LABEL_MAPPING.get(label)

        if not mapped:
            continue

        mapped_type, gdpr_category = mapped

        notices.append({
            "type": mapped_type,
            "text": clean,
            "reason": "ml",
            "gdpr_category": gdpr_category
        })

        updated = re.sub(
            rf"\b{re.escape(clean)}\b",
            f"[{mapped_type}_REMOVED]",
            updated
        )
    # ------------------------------------------------------------
    # 3b) Conservative single-name fallback (handles possessive)
    # ------------------------------------------------------------
    SINGLE_NAME_PATTERN = re.compile(r"\b([A-Z][a-z]{2,})(?:'s)?\b")

    for m in SINGLE_NAME_PATTERN.finditer(updated):
        word = m.group(1)

        # Skip if already masked
        if word.startswith("["):
            continue

        # Skip if already detected
        if any(n["text"] == word for n in notices):
            continue

        # Skip location entities
        if any(n["type"] in {"ADDRESS", "LOCATION"} and n["text"] == word for n in notices):
            continue

        # Only allow known safe names
        if (
            word[0].isupper()
            and word.lower() not in COMMON_STOPWORDS
            and not any(n["text"] == word for n in notices)
        ):

            notices.append({
                "type": "PERSON",
                "text": word,
                "reason": "regex_fallback",
                "gdpr_category": "PERSONAL_IDENTIFIER"
            })

            updated = re.sub(
                rf"\b{re.escape(word)}(?:'s)?\b",
                "[PERSON_REMOVED]",
                updated
            )
    # ------------------------------------------------------------
    # 4) Restore frozen placeholders
    # ------------------------------------------------------------
    for placeholder, original in frozen_map.items():
        updated = updated.replace(placeholder, original)

    return updated