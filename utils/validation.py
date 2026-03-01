import re

def validate_masking(text: str) -> None:
    # Detect broken masks
    if re.search(r"\[[A-Z_]+_REMOVED[^\]]", text):
        raise ValueError("Broken masking token detected.")

    # Detect nested masks
    if re.search(r"\[[^\]]*\[", text):
        raise ValueError("Nested masking detected.")

    # Detect partially removed patterns
    if "_REMOV" in text and not re.search(r"\[[A-Z_]+_REMOVED\]", text):
        raise ValueError("Corrupted mask structure.")