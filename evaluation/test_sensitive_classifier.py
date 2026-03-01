from bert.sensitive_classifier import detect_gdpr_categories

test_cases = [
    "John was diagnosed with cancer last year.",
    "The company stores employee data for 10 years.",
    "Data was transferred to servers in the United States.",
    "She is a member of a trade union.",
    "The password is P@ssw0rd123",
    "This is just a normal sentence with no personal data."
]

for text in test_cases:
    print("=" * 60)
    print("TEXT:", text)
    result = detect_gdpr_categories(text)
    print("DETECTED:", result)