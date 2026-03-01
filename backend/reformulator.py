import re
import spacy

# Load spaCy (small model is OK)
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------
# 1) INTENT RULES (Primary Deterministic Intent Classifier)
# ---------------------------------------------------------
INTENT_RULES = {
    "ACCESS_BADGE": [
        r"\bbadge\b", r"\baccess card\b", r"\bkeycard\b",
        r"\bemployee id\b", r"\bstaff id\b", r"\bid\s*\d{3,10}\b"
    ],
    "PASSWORD_LOGIN": [
        r"reset.*password", r"can't log in", r"cannot log in",
        r"login.*fail", r"authentication", r"account.*locked"
    ],
    "NETWORK_INTERNET": [
        r"internet", r"wi[ -]?fi", r"router", r"network.*down",
        r"slow connection", r"no connection"
    ],
    "RELOCATION_SERVICES": [
        r"moved to", r"recently moved", r"relocated", 
        r"new address", r"provider.*in\b"
    ],
    "DEVICE_PROBLEM": [
        r"laptop", r"computer", r"not turning on", r"phone.*broken",
        r"screen.*issue", r"keyboard not working"
    ],
    "BILLING": [
        r"invoice", r"charged", r"billing", r"payment.*issue"
    ],
    "HEALTH_ADVICE": [
        r"asthma", r"diabetes", r"migraine", r"flu", r"covid"
    ]
}


def detect_intent_rules(text: str):
    """Rule-based matching. Returns first matched intent or None."""
    t = text.lower()
    for intent, patterns in INTENT_RULES.items():
        for p in patterns:
            if re.search(p, t):
                return intent
    return None


# ---------------------------------------------------------
# 2) ML BACKUP CLASSIFIER (spaCy text categorizer)
# ---------------------------------------------------------
# NOTE: This classifier is intentionally simple — it predicts
#       ONLY when rule-based detection is uncertain.

INTENT_LABELS = [
    "ACCESS_BADGE",
    "PASSWORD_LOGIN",
    "NETWORK_INTERNET",
    "RELOCATION_SERVICES",
    "DEVICE_PROBLEM",
    "BILLING",
    "HEALTH_ADVICE",
    "GENERAL_QUESTION"
]


def ml_predict_intent(text):
    doc = nlp(text)
    # If no textcat model exists, fallback
    if "textcat_multilabel" not in nlp.pipe_names:
        return "GENERAL_QUESTION"
    
    scores = doc.cats
    if not scores:
        return "GENERAL_QUESTION"

    # Pick highest score
    best = max(scores, key=lambda k: scores[k])
    if scores[best] < 0.5:
        return "GENERAL_QUESTION"

    return best


# ---------------------------------------------------------
# 3) TEMPLATES (High-Level Reformulation Targets)
# ---------------------------------------------------------
TEMPLATES = {
    "ACCESS_BADGE":
        "Provide troubleshooting steps for resolving issues with a malfunctioning company badge or employee ID%s.",

    "PASSWORD_LOGIN":
        "Offer clear guidance for resolving a password or login authentication issue%s.",

    "NETWORK_INTERNET":
        "Provide support for diagnosing and fixing internet or network connectivity issues%s.",

    "RELOCATION_SERVICES":
        "Recommend reliable service providers or helpful resources for someone who has recently relocated%s.",

    "DEVICE_PROBLEM":
        "Provide troubleshooting steps for resolving a malfunctioning or non-responsive device%s.",

    "BILLING":
        "Offer assistance for resolving a billing or payment-related question%s.",

    "HEALTH_ADVICE":
        "Provide general advice or information relevant to this health-related concern%s.",

    "GENERAL_QUESTION":
        "Provide clear and helpful information addressing the user’s request%s."
}


# ---------------------------------------------------------
# 4) Insert User-Kept Sensitive Items Into Template
# ---------------------------------------------------------
def integrate_kept_items(intent: str, template: str, kept_items: list):
    """
    Only integrates items that user CHOSE TO KEEP.
    Allowed injected categories:
      - ADDRESS
      - LOCATION
      - DEVICE (could be added later)
      - other contextual non-identity data
    """

    context_items = []

    for item in kept_items:
        t = item["type"]
        text = item["text"]

        # Only inject contextual data, not identity:
        if t in ["ADDRESS", "LOCATION"]:
            context_items.append(text)

    if context_items:
        ctx = " in " + ", ".join(context_items)
    else:
        ctx = ""

    return template % ctx


# ---------------------------------------------------------
# 5) MAIN REFORMULATION FUNCTION
# ---------------------------------------------------------
def reformulate(sanitized_text: str, kept_items: list):
    # 1) Try rule-based detection
    intent = detect_intent_rules(sanitized_text)

    # 2) ML fallback
    if intent is None:
        intent = ml_predict_intent(sanitized_text)

    # 3) Final fallback
    if intent is None:
        intent = "GENERAL_QUESTION"

    # 4) Choose template
    template = TEMPLATES.get(intent, TEMPLATES["GENERAL_QUESTION"])

    # 5) Integrate user-kept data
    return integrate_kept_items(intent, template, kept_items)
