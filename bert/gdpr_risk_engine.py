# bert/gdpr_risk_engine.py

CATEGORY_WEIGHTS = { ... }  # paste weights above


def compute_gdpr_risk(categories, notices):

    base_scores = {
        "SPECIAL_CATEGORY_DATA": 10,
        "CRIMINAL_DATA": 10,
        "SECURITY_CREDENTIAL": 6,
        "FINANCIAL_DATA": 6,
        "PERSONAL_IDENTIFIER": 4,
        "LOCATION_DATA": 3,
        "CONTACT_DATA": 3,
        "DATA_GOVERNANCE": 3,
        "INTERNATIONAL_TRANSFER": 6,
        "EMPLOYEE_DATA": 4,
    }

    score = sum(base_scores.get(cat, 0) for cat in categories)

    entity_count = len(notices)

    if entity_count >= 5:
        score += 4
    elif entity_count >= 3:
        score += 2
    elif entity_count >= 1:
        score += 1

    # Compound escalation
    if "FINANCIAL_DATA" in categories and "PERSONAL_IDENTIFIER" in categories:
        score += 3

    if "SPECIAL_CATEGORY_DATA" in categories and "PERSONAL_IDENTIFIER" in categories:
        score += 4

    if score >= 20:
        level = "CRITICAL"
    elif score >= 12:
        level = "HIGH"
    elif score >= 6:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": score, "level": level}