from .regex_masking import apply_regex_layer, apply_health_masking
from .transformer_sanitizer import ml_mask
from .rule_engine import apply_rule_logic
from .topic_detector import detect_topic
from .sensitive_classifier import detect_gdpr_categories
from .gdpr_risk_engine import compute_gdpr_risk
from utils.normalization import normalize_text


def sanitize(text: str):

    normalized_text = normalize_text(text)
    notices = []

    # 1. Regex masking
    text_after_regex = apply_regex_layer(normalized_text, notices)
    text_after_ml = ml_mask(text_after_regex, notices)

    text_after_health = apply_health_masking(text_after_ml, notices)

    final_text = apply_rule_logic(text_after_health, notices)

    # 4. Entity-based GDPR categories
    entity_categories = {
        n.get("gdpr_category")
        for n in notices
        if n.get("gdpr_category")
    }

    # 5. Semantic GDPR classification
    if len(normalized_text.split()) >= 6:
        semantic_raw = detect_gdpr_categories(normalized_text)
    else:
        semantic_raw = []

    semantic_risk_groups = {
        item["risk_group"]
        for item in semantic_raw
        if isinstance(item, dict) and "risk_group" in item
    }

    # 6. Merge entity + semantic
    gdpr_categories = list(entity_categories.union(semantic_risk_groups))

    # 7. Risk scoring
    risk_assessment = compute_gdpr_risk(
        gdpr_categories,
        notices
    )

    # 8. Topic detection
    topic = detect_topic(
        notices,
        gdpr_categories,
        risk_assessment
    )

    return {
        "sanitized": final_text,
        "topic": topic,
        "notices": notices,
        "gdpr_categories": gdpr_categories,
        "risk_assessment": risk_assessment
    }