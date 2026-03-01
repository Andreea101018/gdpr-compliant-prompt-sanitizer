def detect_topic(notices, gdpr_categories, risk_assessment):
    """
    GDPR-aware topic detection.

    Priority order:
    1. Incident / Breach
    2. Critical risk override
    3. Special Category (Art. 9)
    4. Criminal Data (Art. 10)
    5. International transfer / governance
    6. Vulnerable subjects
    7. Security credentials
    8. Financial data
    9. Contact / location
    10. Default personal data
    """

    # --------------------------------------------------------
    # Defensive defaults
    # --------------------------------------------------------
    notices = notices or []
    gdpr_categories = gdpr_categories or []
    risk_assessment = risk_assessment or {}

    if not notices and not gdpr_categories:
        return "GENERAL"

    categories = set(gdpr_categories)
    notice_types = {n.get("type") for n in notices}

    risk_level = risk_assessment.get("level", "LOW")

    # ========================================================
    # 1️⃣ DATA BREACH / INCIDENT
    # ========================================================
    if "DATA_BREACH" in categories:
        return "SECURITY_INCIDENT"

    # ========================================================
    # 2️⃣ CRITICAL RISK OVERRIDE
    # ========================================================
    if risk_level == "CRITICAL":
        return "HIGH_RISK_PROCESSING"

    # ========================================================
    # 3️⃣ SPECIAL CATEGORY DATA (Art. 9 GDPR)
    # ========================================================
    if "SPECIAL_CATEGORY_DATA" in categories:
        return "SENSITIVE_PERSONAL_DATA"

    # ========================================================
    # 4️⃣ CRIMINAL DATA (Art. 10 GDPR)
    # ========================================================
    if "CRIMINAL_DATA" in categories:
        return "CRIMINAL_DATA"

    # ========================================================
    # 5️⃣ INTERNATIONAL TRANSFER / GOVERNANCE
    # ========================================================
    if "INTERNATIONAL_TRANSFER" in categories:
        return "INTERNATIONAL_TRANSFER"

    if "DATA_GOVERNANCE" in categories:
        return "DATA_GOVERNANCE"

    # ========================================================
    # 6️⃣ VULNERABLE SUBJECTS
    # ========================================================
    if "VULNERABLE_SUBJECT" in categories:
        return "VULNERABLE_SUBJECT"

    if "EMPLOYEE_DATA" in categories:
        return "EMPLOYEE_DATA"

    # ========================================================
    # 7️⃣ AUTHENTICATION / SECURITY CREDENTIALS
    # ========================================================
    if "SECURITY_CREDENTIAL" in categories:
        return "AUTHENTICATION_DATA"

    # Fallback based on raw notice types
    if {"PASSWORD", "PIN", "SECURITY_TOKEN"}.intersection(notice_types):
        return "AUTHENTICATION_DATA"

    # ========================================================
    # 8️⃣ FINANCIAL DATA
    # ========================================================
    if "FINANCIAL_DATA" in categories:
        return "FINANCIAL_DATA"

    if {"CREDIT_CARD", "IBAN", "FINANCIAL_AMOUNT"}.intersection(notice_types):
        return "FINANCIAL_DATA"

    # ========================================================
    # 9️⃣ CONTACT / LOCATION
    # ========================================================
    if "CONTACT_DATA" in categories:
        return "CONTACT_DATA"

    if {"EMAIL", "PHONE"}.intersection(notice_types):
        return "CONTACT_DATA"

    if "LOCATION_DATA" in categories:
        return "LOCATION_DATA"

    if {"ADDRESS", "LOCATION"}.intersection(notice_types):
        return "LOCATION_DATA"

    # ========================================================
    # 🔟 DEFAULT PERSONAL DATA
    # ========================================================
    if "PERSONAL_IDENTIFIER" in categories:
        return "PERSONAL_DATA"

    if notice_types:
        return "PERSONAL_DATA"

    return "GENERAL"