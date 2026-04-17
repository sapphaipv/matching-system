import re

STOPWORDS = {"tui", "hop", "chai", "lon", "goi"}

VARIANT_KEYWORDS = [
    "khong duong", "it duong", "co duong",
    "nguyen chat", "truyen thong", "mix", "dac biet"
]

def extract_weight(text):
    text = text.replace("gr", "g")

    match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g)", text)
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2)

    if unit == "kg":
        value *= 1000

    return int(value)

def extract_variant(text):
    return [v for v in VARIANT_KEYWORDS if v in text]

def tokenize_main(text):
    words = text.split()
    return [w for w in words if w not in STOPWORDS]

def parse_product(text):
    return {
        "weight": extract_weight(text),
        "variant": extract_variant(text),
        "tokens": tokenize_main(text)
    }