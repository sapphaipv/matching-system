# src/tokenizer.py

STOPWORDS = {
    "loai", "hang", "chinh", "hang", "san", "pham",
    "tui", "hop", "chai", "goi", "thung"
}


def is_valid_token(token: str) -> bool:
    if not token:
        return False

    # loại token quá ngắn (trừ số)
    if len(token) <= 1 and not token.isdigit():
        return False

    # loại stopword
    if token in STOPWORDS:
        return False

    return True


def tokenize(text: str):
    if not text:
        return []

    tokens = text.split()

    # filter
    tokens = [t for t in tokens if is_valid_token(t)]

    return tokens