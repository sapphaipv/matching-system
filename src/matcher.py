from src.attribute import classify_tokens, extract_attributes
from src.scorer import flavor_penalty
from src.normalizer import normalize_text
from src.tokenizer import tokenize
from src.synonym import expand_tokens
from src.weight_parser import parse_weight
from src.scorer import token_overlap, weight_score, fuzzy, compute_score
from src.explain import build_explain
from src.config import THRESHOLD_MATCH, THRESHOLD_REVIEW


CATEGORY_KEYWORDS = {
    "cao", "kem", "thuốc", "gel", "dầu",
    "cá", "gà", "vịt", "heo", "bò", "tôm",
    "bánh", "kẹo", "sữa", "nước", "trà"
}


def extract_category(tokens):
    return set([t for t in tokens if t in CATEGORY_KEYWORDS])


def category_conflict(tokens_a, tokens_b):
    ca = extract_category(tokens_a)
    cb = extract_category(tokens_b)

    if ca and cb and not ca.intersection(cb):
        return True
    return False


def match_product(a, b, synonym_map, attribute_vocab, debug=False):

    # ========================
    # NORMALIZE
    # ========================
    na = normalize_text(a)
    nb = normalize_text(b)

    # ✅ FIX: dùng attribute_vocab đúng
    attr_full_a = extract_attributes(na, attribute_vocab)
    attr_full_b = extract_attributes(nb, attribute_vocab)

    # ========================
    # TOKENIZE
    # ========================
    ta = tokenize(na)
    tb = tokenize(nb)

    # category guard
    if category_conflict(ta, tb):
        return False, build_explain(0, 0, 0, 0, "category conflict")

    # ========================
    # ATTRIBUTE CLASSIFICATION
    # ========================
    id_a, attr_a = classify_tokens(ta)
    id_b, attr_b = classify_tokens(tb)

    # ========================
    # SYNONYM EXPAND
    # ========================
    ea = expand_tokens(ta, synonym_map)
    eb = expand_tokens(tb, synonym_map)

    # ========================
    # PARSE WEIGHT
    # ========================
    w1 = parse_weight(na)
    w2 = parse_weight(nb)

    # HARD RULE: weight
    if w1 is not None and w2 is not None and w1 != w2:
        return False, build_explain(0, 0, -1, 0, "weight mismatch")

    # ========================
    # COMPUTE FEATURES
    # ========================
    tok = token_overlap(ea, eb)
    w = weight_score(w1, w2)
    fz = fuzzy(na, nb)

    # attribute conflict
    if attr_a and attr_b and not set(attr_a).intersection(set(attr_b)):
        return False, build_explain(0, tok, w, fz, "attribute conflict")

    # ========================
    # FINAL SCORE
    # ========================
    score = compute_score(tok, w, fz)

    # add flavor penalty
    score += flavor_penalty(attr_full_a, attr_full_b)

    # ========================
    # DECISION
    # ========================
    if score >= THRESHOLD_MATCH:
        return True, build_explain(score, tok, w, fz, "strong match")

    elif score >= THRESHOLD_REVIEW:
        return False, build_explain(score, tok, w, fz, "review")

    else:
        return False, build_explain(score, tok, w, fz, "low score")