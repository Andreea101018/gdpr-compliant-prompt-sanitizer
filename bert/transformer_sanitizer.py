from .ner_model import TransformerNER
from .regex_patterns import SAFE_FIRST_NAMES      # <-- REQUIRED FIX
import re

NER_MODEL = TransformerNER()

PASSWORD_KEYWORDS = {"password", "passcode"}


# ------------------------------------------------------------
# Extract password after keyword
# ------------------------------------------------------------
def extract_password_value(text):
    m = re.search(
        r"(password|passcode)\s*(is|=|:)?\s*([^\s]+)",
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

    return score >= 3  # strong secret


# ------------------------------------------------------------
# ML Masking layer (GDPR safe)
# ------------------------------------------------------------
def ml_mask(text, notices):
    """
    ML masking layer with GDPR-compliant behavior:
      - Never masks inside regex-removed spans
      - Avoids subword and hallucinated masking
      - Fully masks passwords from both regex & ML
      - Only masks real PERSON/LOCATION entities
      - Avoids masking "Call", "Meet", "Park", etc.
    """

    # ---------------------------------------------
    # 0) Freeze existing placeholders
    # ---------------------------------------------
    frozen_map = {}
    idx = 0

    for match in re.findall(r"\[[A-Z_]+_REMOVED\]", text):
        placeholder = f"§FROZEN_{idx}§"
        frozen_map[placeholder] = match
        text = text.replace(match, placeholder)
        idx += 1

    # ---------------------------------------------
    # 1) Full PASSWORD masking (keyword-based)
    # ---------------------------------------------
    pwd_val = extract_password_value(text)
    if pwd_val:
        notices.append({"type": "PASSWORD", "text": pwd_val, "reason": "regex"})
        text = text.replace(pwd_val, "[PASSWORD_REMOVED]")

    # ---------------------------------------------
    # 2) Run NER
    # ---------------------------------------------
    entities = NER_MODEL.predict(text)
    updated = text

    # Store regex spans to prevent ML masking overlaps
    regex_spans = [n["text"] for n in notices if n["reason"] == "regex"]

    # ---------------------------------------------
    # 3) Iterate through ML entities
    # ---------------------------------------------
    for word, label in entities:

        clean = word.strip()

        # Skip empty or junk
        if not clean:
            continue

        # Skip tiny tokens
        if len(clean) <= 2:
            continue

        # Skip WordPiece fragments
        if clean.startswith("##"):
            continue

        # Skip ML entities that appear inside regex spans
        if any(clean in span for span in regex_spans):
            continue

        # Skip frozen placeholders (e.g., EMAIL_REMOVED)
        if any(ph in clean for ph in frozen_map.keys()):
            continue

        # ------------------------------------------------------------
        # **FIX ADDED HERE**
        # Force PERSON detection for whitelisted names (Ahmad, Björn, etc.)
        # ------------------------------------------------------------
        if clean in SAFE_FIRST_NAMES:
            label = "PERSON"

        # -----------------------------------------
        # 3A) ML-detected PASSWORD (heuristic-based)
        # -----------------------------------------
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
                    updated,
                )
            continue  # do not mask weak tokens

        # -----------------------------------------
        # 3B) Prevent junk PERSON detections
        # -----------------------------------------
        if label == "PERSON" and clean.lower() in {
            "call", "meet", "send", "park", "team", "budget", "road", "street",
            "office", "update", "city", "morning", "evening"
        }:
            continue  # not a real person

        # -----------------------------------------
        # 3C) Final entity masking
        # -----------------------------------------
        notices.append({"type": label, "text": clean, "reason": "ml"})

        updated = re.sub(
            rf"\b{re.escape(clean)}\b",
            f"[{label}_REMOVED]",
            updated,
        )

    # ---------------------------------------------
    # 4) Restore frozen content
    # ---------------------------------------------
    for placeholder, original in frozen_map.items():
        updated = updated.replace(placeholder, original)

    return updated
