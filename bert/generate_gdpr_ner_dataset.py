import csv
import random
import re

# -----------------------------------------
# GDPR-SAFE SYNTHETIC VOCABULARY
# -----------------------------------------

PERSONS = [
    "Sarah Thompson", "Daniel Ruiz", "Anna Keller",
    "John Anderson", "Maria Popescu", "Liam Becker",
    "Sofia Dimitri", "Victor Novak", "Laura Schmidt"
]

LOCATIONS = [
    "Berlin", "Munich", "Paris", "London", "Rome",
    "Hamburg", "Frankfurt", "Barcelona", "Vienna"
]

ADDRESSES = [
    "221B Baker Street", "12 Hauptstrasse", "44 Market Road",
    "5 Industrial Avenue", "10 Park Lane"
]

HEALTH = [
    "asthma", "diabetes", "depression", "autism",
    "hypertension", "flu", "migraines"
]

FINANCIAL = [
    "tax return", "salary", "pension",
    "reimbursement", "financial report"
]

PASSWORDS = [
    "Winter2024!", "Passcode33", "SecureKey998",
    "sunshine123!", "Token445@"
]

# SECURITY tokens are alphanumeric to avoid PHONE regex
SECURITY_CODES = [
    "alpha2356", "sec9981", "otp0321",
    "pin7134", "code4421"
]

# NOISE TOKENS (look like email/phone/iban/credit card but labeled O)
NOISE_EMAIL = [
    "demo.user@mailservice.net",
    "test.account@placeholder.org",
    "abc.xyz@demo.co"
]

NOISE_PHONE = [
    "+11 222 333 4444",
    "(555) 123-7788",
    "01928 338822"
]

NOISE_NUMERIC = [
    "A123B55X", "Z91X0021", "REF-99321",
    "X0A1-T22Q", "CODE-55120"
]

# -----------------------------------------
# TEMPLATE SENTENCES
# -----------------------------------------

TEMPLATES = [
    # PERSON
    "{person} will join the meeting.",
    "{person} approved the request yesterday.",
    "I spoke with {person} this morning.",

    # LOCATION
    "Our office in {location} will close soon.",
    "The package is going to {location}.",
    "{person} relocated to {location} last year.",

    # ADDRESS
    "The event takes place at {address}.",
    "Please send the documents to {address}.",
    "{person} lives at {address}.",

    # HEALTH
    "{person} was diagnosed with {health}.",
    "I am receiving treatment for {health}.",
    "{person} suffers from {health}.",

    # FINANCIAL
    "I need help with {financial}.",
    "{person} submitted the {financial}.",
    "The accountant reviewed the {financial}.",

    # PASSWORD
    "My password is {password}.",
    "{person}'s passcode is {password}.",

    # SECURITY
    "The security token is {security}.",
    "{person} used security code {security}.",

    # NOISE (not labeled)
    "You can reach support at {noise_email}.",
    "My reference number is {noise_num}.",
    "Customer hotline: {noise_phone}."
]

# -----------------------------------------
# TOKENIZER
# -----------------------------------------

def tokenize(text):
    text = text.replace(".", "")
    text = text.replace("’", "'")
    text = re.sub(r"(\w)'s\b", r"\1 's", text)
    return text.split()

# -----------------------------------------
# BIO TAGGING
# -----------------------------------------

def apply_entity_labels(tokens, entity_tokens, label, labels):
    n = len(entity_tokens)
    for i in range(len(tokens) - n + 1):
        if tokens[i:i+n] == entity_tokens:
            labels[i] = f"B-{label}"
            for j in range(1, n):
                labels[i+j] = f"I-{label}"
    return labels

# -----------------------------------------
# GENERATE ONE SENTENCE
# -----------------------------------------

def generate_sentence():
    tmpl = random.choice(TEMPLATES)

    values = {
        "person": random.choice(PERSONS),
        "location": random.choice(LOCATIONS),
        "address": random.choice(ADDRESSES),
        "health": random.choice(HEALTH),
        "financial": random.choice(FINANCIAL),
        "password": random.choice(PASSWORDS),
        "security": random.choice(SECURITY_CODES),
        "noise_email": random.choice(NOISE_EMAIL),
        "noise_num": random.choice(NOISE_NUMERIC),
        "noise_phone": random.choice(NOISE_PHONE),
    }

    sentence = tmpl.format(**values)
    tokens = tokenize(sentence)
    labels = ["O"] * len(tokens)

    #	entity map for BIO tagging (noise is excluded)
    entity_map = {
        "PERSON": tokenize(values["person"]),
        "LOCATION": tokenize(values["location"]),
        "ADDRESS": tokenize(values["address"]),
        "HEALTH": tokenize(values["health"]),
        "FINANCIAL": tokenize(values["financial"]),
        "PASSWORD": tokenize(values["password"]),
        "SECURITY": tokenize(values["security"]),
    }

    for label, parts in entity_map.items():
        if set(parts).issubset(tokens):
            labels = apply_entity_labels(tokens, parts, label, labels)

    return tokens, labels

# -----------------------------------------
# WRITE CSV
# -----------------------------------------

def generate_csv(path="ner_training_data_bio.csv", n=5000):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence_id", "token", "label"])

        for sid in range(n):
            tokens, labels = generate_sentence()
            for t, l in zip(tokens, labels):
                writer.writerow([sid, t, l])

    print(f"Generated {n} GDPR-safe BIO-tagged sentences → {path}")

# -----------------------------------------

if __name__ == "__main__":
    generate_csv()
