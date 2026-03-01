def detect_topic(notices):
    if not notices:
        return "GENERAL"

    # Count occurrences per label
    counts = {}
    for n in notices:
        label = n["type"]
        counts[label] = counts.get(label, 0) + 1

    # Map entity labels → topic categories
    TOPIC_MAP = {
        "PASSWORD": "SECURITY",
        "PIN": "SECURITY",
        "SECURITY": "SECURITY",

        "CREDIT_CARD": "FINANCIAL",
        "IBAN": "FINANCIAL",
        "FINANCIAL": "FINANCIAL",

        "HEALTH": "HEALTH",

        "EMAIL": "CONTACT",
        "PHONE": "CONTACT",

        "ADDRESS": "LOCATION",
        "LOCATION": "LOCATION",

        "PERSON": "IDENTITY",
        "AGE": "IDENTITY",
    }

    # Compute topic scores
    topic_scores = {}
    for label, count in counts.items():
        topic = TOPIC_MAP.get(label, "GENERAL")
        topic_scores[topic] = topic_scores.get(topic, 0) + count

    # Apply GDPR risk-based priority (higher = more sensitive)
    GDPR_RISK_PRIORITY = [
        "SECURITY",
        "HEALTH",
        "FINANCIAL",
        "IDENTITY",
        "LOCATION",
        "CONTACT",
        "GENERAL",
    ]

    # Select the highest-priority topic that appears
    for topic in GDPR_RISK_PRIORITY:
        if topic in topic_scores:
            return topic

    return "GENERAL"
