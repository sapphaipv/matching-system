# src/attribute.py

# 👇 bạn có thể mở rộng dần sau
ATTRIBUTE_KEYWORDS = {
    "khong", "duong", "it", "duong",   # không đường / ít đường
    "chocolate", "socola",
    "vanilla",
    "dau", "sau", "rieng",  # vị
}

def classify_tokens(tokens):
    """
    return:
        identity_tokens, attribute_tokens
    """
    identity = []
    attribute = []

    for t in tokens:
        if t in ATTRIBUTE_KEYWORDS:
            attribute.append(t)
        else:
            identity.append(t)

    return identity, attribute

def extract_by_type(text, vocab, target_type):
    text = str(text).lower()
    found = []

    for v in vocab:
        # ADD guard
        if not isinstance(v, dict):
            continue

        if v.get("type") == target_type:
            if v.get("keyword") in text:
                found.append(v["keyword"])

    return found

def extract_attributes(text, vocab):
    return {
        "flavor": extract_by_type(text, vocab, "flavor"),
        "sugar": extract_by_type(text, vocab, "sugar"),
        "type": extract_by_type(text, vocab, "type"),
    }