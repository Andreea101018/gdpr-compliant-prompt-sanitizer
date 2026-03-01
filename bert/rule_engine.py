def apply_rule_logic(text, notices):
    """
    Apply GDPR rule-based logic.
    """
    # 1. Fix consecutive PERSON labels
    text = text.replace("[PERSON_REMOVED] [PERSON_REMOVED]", "[PERSON_REMOVED]")

    # 2. Add GDPR category to notices
    for n in notices:
        if not n.get("gdpr_category"):
            n["gdpr_category"] = map_label_to_gdpr(n["type"])

    return text


def map_label_to_gdpr(label):
    mapping = {
        "HEALTH": "SPECIAL_CATEGORY_DATA",
        "GENETIC": "SPECIAL_CATEGORY_DATA",
        "BIOMETRIC": "SPECIAL_CATEGORY_DATA",
        "POLITICAL": "SPECIAL_CATEGORY_DATA",

        "CRIMINAL": "CRIMINAL_DATA",

        "IBAN": "FINANCIAL_DATA",
        "CREDIT_CARD": "FINANCIAL_DATA",
        "FINANCIAL_AMOUNT": "FINANCIAL_DATA",

        "SECURITY_TOKEN": "SECURITY_CREDENTIAL",
        "PIN": "SECURITY_CREDENTIAL",
        "PASSWORD": "SECURITY_CREDENTIAL",

        "PERSON": "PERSONAL_IDENTIFIER",
        "AGE": "PERSONAL_IDENTIFIER",
        "ID": "PERSONAL_IDENTIFIER",

        "EMAIL": "CONTACT_DATA",
        "PHONE": "CONTACT_DATA",

        "ADDRESS": "LOCATION_DATA",
        "LOCATION": "LOCATION_DATA",
        "ADDRESS_NUMBER": "LOCATION_DATA",
        "ZIPCODE": "LOCATION_DATA",
    }

    return mapping.get(label)
