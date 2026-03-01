from .regex_masking import apply_regex_layer
from .transformer_sanitizer import ml_mask
from .rule_engine import apply_rule_logic
from .topic_detector import detect_topic


def sanitize(text):
    notices = []

    # 1. regex masking
    text_after_regex = apply_regex_layer(text, notices)

    # 2. ML NER masking
    text_after_ml = ml_mask(text_after_regex, notices)

    # 3. GDPR rule logic
    final_text = apply_rule_logic(text_after_ml, notices)

    # 4. Topic detection
    topic = detect_topic(notices)

    # IMPORTANT: No DB write here — this keeps sanitize() safe and clean.
    return {
        "sanitized": final_text,
        "topic": topic,
        "notices": notices
    }
