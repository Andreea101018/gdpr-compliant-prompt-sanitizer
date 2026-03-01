from bert.regex_masking import apply_regex_layer

def test_case(text):
    print("=" * 60)
    print("INPUT:")
    print(text)

    notices = []
    result = apply_regex_layer(text, notices)

    print("\nSANITIZED:")
    print(result)

    print("\nNOTICES:")
    for n in notices:
        print(n)


if __name__ == "__main__":

    test_samples = [

        # IBAN
        "My IBAN is DE89370400440532013000.",

        # Credit card (valid Visa test number)
        "Card number is 4111 1111 1111 1111.",

        # Invalid credit card
        "Card number is 4111 1111 1111 1234.",

        # Email
        "Contact me at john.doe@example.com.",

        # Phone
        "Call me at +1 415 983 2231 tomorrow.",

        # Short invalid phone
        "Number is 12345.",

        # Financial amount
        "The payment was €1,250.50 yesterday.",

        # Address
        "I live at 221B Baker Street.",

        # Security token
        "Your otp code 456789 expires soon.",

        # ID
        "Employee ID: 983742",

        # Mixed case
        "Transfer 5000 USD to IBAN FR1420041010050500013M02606 immediately."
    ]

    for sample in test_samples:
        test_case(sample)