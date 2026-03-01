from bert.integrated_sanitizer import sanitize

def test_names_masked():
    text = "John Doe lives in Berlin."
    result = sanitize(text)
    output = result["sanitized"]
    assert "[PERSON_REMOVED]" in output

def test_location_masked():
    text = "I live in Paris."
    result = sanitize(text)
    output = result["sanitized"]
    assert "[LOCATION_REMOVED]" in output

def test_email_masked():
    text = "Contact me at test@example.com"
    result = sanitize(text)
    output = result["sanitized"]
    assert "[EMAIL_REMOVED]" in output

def test_password_masked():
    text = "My password is Secret123!"
    result = sanitize(text)
    output = result["sanitized"]
    assert "[PASSWORD_REMOVED]" in output