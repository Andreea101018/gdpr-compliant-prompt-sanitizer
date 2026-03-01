import unicodedata
import re

def normalize_text(text: str) -> str:
    # 1. Normalize Unicode (fix homoglyph attacks)
    text = unicodedata.normalize("NFKC", text)

    # 2. Remove zero-width characters
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

    # 3. Collapse excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text