import re
import unicodedata


# ========================
# REMOVE ACCENTS (VN)
# ========================
def remove_accents(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text


# ========================
# NORMALIZE UNIT
# ========================
def normalize_units(text: str) -> str:
    if not text:
        return ""

    # chuẩn hóa khoảng trắng giữa số và đơn vị
    text = re.sub(r"(\d)(g|kg|ml|l)\b", r"\1 \2", text)

    # chuẩn hóa đơn vị về dạng chuẩn
    text = re.sub(r"\bgr\b", "g", text)
    text = re.sub(r"\bkg\b", "kg", text)
    text = re.sub(r"\bl\b", "l", text)
    text = re.sub(r"\bml\b", "ml", text)

    return text


# ========================
# REMOVE NOISE
# ========================
def remove_noise(text: str) -> str:
    if not text:
        return ""

    # bỏ nội dung trong ngoặc
    text = re.sub(r"\(.*?\)", " ", text)

    # bỏ ký tự đặc biệt
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return text


# ========================
# MAIN NORMALIZE
# ========================
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = str(text).lower()

    text = remove_accents(text)
    text = normalize_units(text)
    text = remove_noise(text)

    # remove multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text