from bert.integrated_sanitizer import sanitize

NON_PII_TEXTS = [
    "Library budget report for 2024.",
    "Financial analysis document.",
    "The office will close soon.",
    "Project timeline updated.",
]

def test_false_positive_rate():
    false_positive_count = 0

    for text in NON_PII_TEXTS:
        result = sanitize(text)
        notices = result["notices"]

        if notices:
            false_positive_count += 1

    assert false_positive_count <= 1