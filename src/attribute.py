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