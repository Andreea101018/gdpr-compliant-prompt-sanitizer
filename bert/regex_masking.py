from .structured_masking import mask_structured_data

def apply_regex_layer(text, notices):
    """
    Pure REGEX structured identifiers.
    """
    return mask_structured_data(text, notices)
