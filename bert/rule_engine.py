def apply_rule_logic(text, notices):
    """
    Apply GDPR rule-based logic.
    """
    # 1. Fix consecutive PERSON labels
    text = text.replace("[PERSON_REMOVED] [PERSON_REMOVED]", "[PERSON_REMOVED]")

    # 2. Add GDPR category to notices
    for n in notices:
        n["gdpr_category"] = map_label_to_gdpr(n["type"])

    return text


def map_label_to_gdpr(label):
    mapping = {
        "PERSON": "Personal Identifier",
        "AGE": "Personal Identifier",
        "ADDRESS": "Location Data",
        "EMAIL": "Contact Information",
        "PHONE": "Contact Information",
        "HEALTH": "Special Category Data",
        "FINANCIAL": "Financial Data",
        "IBAN": "Financial Data",
        "CREDIT_CARD": "Financial Data",
        "SECURITY": "Security Credential",
        "PIN": "Security Credential",
    }
    return mapping.get(label, "General Personal Data")
