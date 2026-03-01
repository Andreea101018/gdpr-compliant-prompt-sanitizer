from transformers import pipeline
import torch
import re

# ============================================================
# Device Selection (safe)
# ============================================================

DEVICE = 0 if torch.cuda.is_available() else -1

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=DEVICE
)

# ============================================================
# GDPR Hypothesis Taxonomy
# ============================================================

GDPR_HYPOTHESES = {

    # =========================
    # Article 9 – Special Categories
    # =========================
    "HEALTH_DATA":
        "This text contains health information about an identifiable person.",

    "GENETIC_DATA":
        "This text contains genetic data about a person.",

    "BIOMETRIC_DATA":
        "This text contains biometric data used to identify a person.",

    "RELIGIOUS_BELIEF":
        "This text reveals religious or philosophical beliefs of a person.",

    "POLITICAL_OPINION":
        "This text contains political opinions of a person.",

    "TRADE_UNION_MEMBERSHIP":
        "This text reveals trade union membership of a person.",

    "SEXUAL_ORIENTATION":
        "This text contains information about sexual orientation of a person.",

    "RACIAL_OR_ETHNIC_ORIGIN":
        "This text reveals racial or ethnic origin of a person.",

    # =========================
    # Article 10 – Criminal Data
    # =========================
    "CRIMINAL_CONVICTION":
        "This text contains information about criminal convictions of a person.",

    "CRIMINAL_OFFENCE":
        "This text contains information about criminal offences involving a person.",

    # =========================
    # Processing Context (Compliance Risk)
    # =========================
    "DATA_STORAGE":
        "This text describes storing personal data.",

    "DATA_SHARING":
        "This text describes sharing personal data with others.",

    "DATA_TRANSFER_OUTSIDE_EU":
        "This text describes transferring personal data outside the European Union.",

    "DATA_RETENTION":
        "This text describes retaining personal data over time.",

    "DATA_BREACH":
        "This text describes a personal data breach.",

    "PROFILING_ACTIVITY":
        "This text describes profiling or automated decision-making about a person.",

    # =========================
    # Vulnerable Subjects
    # =========================
    "CHILD_DATA":
        "This text contains personal data of a child or minor.",

    "EMPLOYEE_DATA":
        "This text contains personal data of employees.",

    "PATIENT_DATA":
        "This text contains personal data of patients."
}

CATEGORY_THRESHOLDS = {

    # --- Article 9 ---
    "HEALTH_DATA": 0.75,
    "GENETIC_DATA": 0.7,
    "BIOMETRIC_DATA": 0.7,
    "RELIGIOUS_BELIEF": 0.75,
    "POLITICAL_OPINION": 0.75,
    "SEXUAL_ORIENTATION": 0.75,
    "RACIAL_OR_ETHNIC_ORIGIN": 0.75,
    "TRADE_UNION_MEMBERSHIP": 0.75,

    # --- Article 10 ---
    "CRIMINAL_CONVICTION": 0.8,
    "CRIMINAL_OFFENCE": 0.8,

    # --- Processing Context ---
    "DATA_TRANSFER_OUTSIDE_EU": 0.7,
    "DATA_BREACH": 0.8,
    "DATA_RETENTION": 0.85,
    "DATA_STORAGE": 0.85,
    "DATA_SHARING": 0.85,
    "PROFILING_ACTIVITY": 0.75,

    # --- Vulnerable Subjects ---
    "CHILD_DATA": 0.75,
    "EMPLOYEE_DATA": 0.75,
    "PATIENT_DATA": 0.75
}
HYPOTHESIS_LIST = list(GDPR_HYPOTHESES.values())
REVERSE_MAP = {v: k for k, v in GDPR_HYPOTHESES.items()}

# ============================================================
# Sentence Splitter
# ============================================================

def split_sentences(text, max_sentences=8):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    return sentences[:max_sentences]  # latency control

def normalize_category(cat):
    mapping = {
        "HEALTH_DATA": "SPECIAL_CATEGORY_DATA",
        "GENETIC_DATA": "SPECIAL_CATEGORY_DATA",
        "BIOMETRIC_DATA": "SPECIAL_CATEGORY_DATA",
        "RELIGIOUS_BELIEF": "SPECIAL_CATEGORY_DATA",
        "POLITICAL_OPINION": "SPECIAL_CATEGORY_DATA",
        "SEXUAL_ORIENTATION": "SPECIAL_CATEGORY_DATA",
        "RACIAL_OR_ETHNIC_ORIGIN": "SPECIAL_CATEGORY_DATA",
        "TRADE_UNION_MEMBERSHIP": "SPECIAL_CATEGORY_DATA",

        "CRIMINAL_CONVICTION": "CRIMINAL_DATA",
        "CRIMINAL_OFFENCE": "CRIMINAL_DATA",

        "DATA_STORAGE": "DATA_GOVERNANCE",
        "DATA_RETENTION": "DATA_GOVERNANCE",
        "DATA_SHARING": "DATA_GOVERNANCE",
        "PROFILING_ACTIVITY": "DATA_GOVERNANCE",

        "DATA_TRANSFER_OUTSIDE_EU": "INTERNATIONAL_TRANSFER",
        "PATIENT_DATA": "SPECIAL_CATEGORY_DATA",
    }

    return mapping.get(cat, cat)

# ============================================================
# Optimized GDPR Detection
# ============================================================

def detect_gdpr_categories(text, default_threshold=0.7):

    text_clean = text.strip()

    if len(text_clean.split()) < 4:
        return []

    if "password" in text_clean.lower() or "passcode" in text_clean.lower():
        return []

    sentences = split_sentences(text_clean)

    if not sentences:
        return []

    results = classifier(
        sentences,
        HYPOTHESIS_LIST,
        multi_label=True,
        truncation=True,
        max_length=512
    )

    if isinstance(results, dict):
        results = [results]

    aggregated_scores = {}

    for result in results:
        for label, score in zip(result["labels"], result["scores"]):

            category = REVERSE_MAP[label]
            cat_threshold = CATEGORY_THRESHOLDS.get(category, default_threshold)

            if score >= cat_threshold:
                aggregated_scores[category] = max(
                    aggregated_scores.get(category, 0),
                    score
                )



    return [
        {
            "category": category,
            "risk_group": normalize_category(category),
            "score": round(float(score), 4)
        }
        for category, score in aggregated_scores.items()
    ]