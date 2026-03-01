import re

from .regex_patterns import (
    STRUCTURED_PATTERNS,
    HEALTH_PATTERN,
    luhn_check,
    valid_phone_number
)

def apply_health_masking(text, notices):

    has_identifier = any(
        n.get("type") in {"PERSON", "ID", "EMAIL", "PHONE"}
        for n in notices
    )

    if not has_identifier:
        return text

    def replace_health(match):
        value = match.group(0)

        notices.append({
            "type": "HEALTH",
            "text": value,
            "reason": "regex_contextual",
            "gdpr_category": "SPECIAL_CATEGORY_DATA"
        })

        return "[HEALTH_REMOVED]"

    return HEALTH_PATTERN.sub(replace_health, text)

def mask_structured_data(text, notices):

    updated_text = text

    GDPR_MAP = {
        "IBAN": "FINANCIAL_DATA",
        "CREDIT_CARD": "FINANCIAL_DATA",
        "EMAIL": "CONTACT_DATA",
        "PHONE": "CONTACT_DATA",
        "ID": "PERSONAL_IDENTIFIER",
        "AGE": "PERSONAL_IDENTIFIER",
        "ZIPCODE": "LOCATION_DATA",
        "ADDRESS": "LOCATION_DATA",
        "SECURITY_TOKEN": "SECURITY_CREDENTIAL",
        "FINANCIAL_AMOUNT": "FINANCIAL_DATA",
    }

    # ============================================================
    # 1️⃣ Structured PII Masking
    # ============================================================

    for label, pattern in STRUCTURED_PATTERNS.items():

        for match in list(pattern.finditer(updated_text)):

            # SECURITY TOKEN — mask only numeric part
            if label == "SECURITY_TOKEN":
                if match.lastindex:
                    original_value = match.group(1)
                else:
                    continue
            else:
                original_value = match.group(0)

            original_value = original_value.strip()

            # CREDIT CARD — Luhn validation
            if label == "CREDIT_CARD":
                if not luhn_check(original_value):
                    continue

            # PHONE — digit count validation
            if label == "PHONE":
                if not valid_phone_number(original_value):
                    continue

            # Prevent re-masking placeholders
            if original_value.startswith("[") and original_value.endswith("]"):
                continue
            print("DEBUG MATCH LABEL:", repr(label))
            print("DEBUG LOOKUP RESULT:", GDPR_MAP.get(label))
            notices.append({
                "type": label,
                "text": original_value,
                "reason": "regex",
                "gdpr_category": GDPR_MAP.get(label)
            })
            print("DEBUG STRUCTURED KEYS:", list(STRUCTURED_PATTERNS.keys()))
            escaped = re.escape(original_value)

            updated_text = re.sub(
                escaped,
                f"[{label}_REMOVED]",
                updated_text,
                count=1
            )
    # ============================================================
    # 1️⃣b Contextual City + ZIP Detection (Deterministic)
    # ============================================================

    CITY_ZIP_PATTERN = re.compile(r"\b([A-Z][a-z]+)\s+(\d{4})\b")

    for match in CITY_ZIP_PATTERN.finditer(text):

        city = match.group(1)
        zipcode = match.group(2)

        # Only apply if ZIPCODE was already detected
        if any(n["type"] == "ZIPCODE" and n["text"] == zipcode for n in notices):

            # Avoid double masking
            if city not in [n["text"] for n in notices]:

                notices.append({
                    "type": "ADDRESS",
                    "text": city,
                    "reason": "regex_contextual",
                    "gdpr_category": "LOCATION_DATA"
                })

                updated_text = re.sub(
                    rf"\b{re.escape(city)}\b",
                    "[ADDRESS_REMOVED]",
                    updated_text,
                    count=1
                )
    # ============================================================
    # 2️⃣ HEALTH DATA (Context-Aware Masking)
    # ============================================================


    return updated_text


def apply_regex_layer(text, notices):
    return mask_structured_data(text, notices)