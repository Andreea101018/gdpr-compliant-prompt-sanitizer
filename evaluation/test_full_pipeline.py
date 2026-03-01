from bert.integrated_sanitizer import sanitize
from bert.database import init_db, save_sensitive_message
import json
from backend.reformulator import reformulate
init_db()

TEST_CASES = [
    "John Doe's IBAN is DE89370400440532013000.",
    "The employee with badge 983742 was diagnosed with cancer.",
    "Send the password P@ssw0rd123 to john.doe@example.com.",
    "We transfer employee data to servers in the United States.",
    "This is just a normal sentence.",
    "Andreea lives in Ballerup 2789 and she is 23 years old and she doesn;t have cancer",
    "Andreea lives on Ballerup 2750"
    "On 14 March 2024, employee Andreea Popescu (badge 983742) reported that her password P@ssw0rd123 had been shared accidentally with john.doe@example.com. She lives in Ballerup 2789 at 12 Green Street and is 23 years old. Her phone number is +45 1234 5678.Her IBAN is DE89370400440532013000 and her credit card 4539 1488 0343 6467 was used for a payment of €1,250.00.The company transfers employee data to servers in the United States and sometimes shares payroll information with external vendors.Her username is andreea.popescu and her driver license number is AB1234567."
]

for text in TEST_CASES:
    print("=" * 80)
    print("INPUT:", text)

    result = sanitize(text)

    print("\nSANITIZED:", result["sanitized"])

    # 🔥 Reformulation test
    reformulated = reformulate(
        result["sanitized"],
        kept_items=[]   # or simulate kept items
    )

    print("\nREFORMULATED:", reformulated)

    print("\nNOTICES:")
    for n in result["notices"]:
        print(n)

    print("\nGDPR CATEGORIES:")
    print(result.get("gdpr_categories"))

    print("\nRISK ASSESSMENT:")
    print(result.get("risk_assessment"))

    print("\nTOPIC:")
    print(result.get("topic"))

    # Optional: save to DB to test persistence
    save_sensitive_message(
        sanitized=result["sanitized"],
        topic=result["topic"],
        notices=result["notices"],
        gdpr_categories=result["gdpr_categories"],
        risk_assessment=result["risk_assessment"]
    )