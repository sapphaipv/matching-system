# src/matcher.py

from src.attribute import classify_tokens, extract_attributes
from src.scorer import flavor_penalty
from src.normalizer import normalize_text
from src.tokenizer import tokenize
from src.synonym import expand_tokens
from src.weight_parser import parse_weight
from src.scorer import token_overlap, weight_score, fuzzy, compute_score
from src.explain import build_explain
from src.config import THRESHOLD_MATCH, THRESHOLD_REVIEW


# ========================
# CATEGORY GROUPS (STRONGER)
# ========================
CATEGORY_GROUPS = {
    "cosmetic": {"kem", "mặt", "mask", "serum", "gel", "dưỡng", "nạ"},
    "food": {"cá", "bánh", "kẹo", "sữa", "trà", "nước"},
    "medicine": {"thuốc", "cao", "viên", "dược"},

    # NEW
    "alcohol": {"rum", "vodka", "whisky", "rượu", "ruou", "tửu", "tuu"},
    "oil": {"dầu", "dau"},
    "powder": {"bột", "bot"},
}


def get_category(tokens):
    found = set()
    for t in tokens:
        for cat, words in CATEGORY_GROUPS.items():
            if t in words:
                found.add(cat)
    return found


def category_conflict(tokens_a, tokens_b):
    ca = get_category(tokens_a)
    cb = get_category(tokens_b)

    if ca and cb and ca.isdisjoint(cb):
        return True
    return False


# ========================
# ANTI CONFUSION (FIXED)
# ========================
def anti_conflict_text(a, b):
    a = a.lower()
    b = b.lower()

    pairs = [
        ("cam", "cám"),
        ("cám", "cam"),
        ("cacao", "cao"),
        ("cao", "cacao"),
    ]

    for x, y in pairs:
        if x in a and y in b:
            return True
        if y in a and x in b:
            return True

    return False


# ========================
# MAIN MATCH FUNCTION
# ========================
def match_product(a, b, synonym_map, attribute_vocab, debug=False):

    # ========================
    # NORMALIZE
    # ========================
    na = normalize_text(a)
    nb = normalize_text(b)

    # ========================
    # ATTRIBUTE (FULL)
    # ========================
    attr_full_a = extract_attributes(na, attribute_vocab)
    attr_full_b = extract_attributes(nb, attribute_vocab)

    # ========================
    # HARD ATTRIBUTE CHECK
    # ========================
    def attr_conflict(a, b, key):
        if a.get(key) and b.get(key):
            return set(a[key]).isdisjoint(set(b[key]))
        return False

    # HARD RULE
    if attr_conflict(attr_full_a, attr_full_b, "flavor"):
        return False, build_explain(0, 0, 0, 0, "flavor conflict")

    # penalty
    sugar_penalty = 0
    if attr_conflict(attr_full_a, attr_full_b, "sugar"):
        sugar_penalty = -0.3

    # ========================
    # TOKENIZE
    # ========================
    ta = tokenize(na)
    tb = tokenize(nb)

    # ========================
    # CATEGORY GUARD (HARD)
    # ========================
    if category_conflict(ta, tb):
        return False, build_explain(0, 0, 0, 0, "category conflict")

    # ========================
    # ANTI CONFUSION (SOFT - FIX)
    # ========================
    anti_penalty = 0
    if anti_conflict_text(a, b):
        anti_penalty = -0.5   # không reject nữa

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

    if w1 is not None and w2 is not None and w1 != w2:
        return False, build_explain(0, 0, -1, 0, "weight mismatch")

    # ========================
    # COMPUTE FEATURES
    # ========================
    tok = token_overlap(ea, eb)
    w = weight_score(w1, w2)
    fz = fuzzy(na, nb)

    if attr_a and attr_b and not set(attr_a).intersection(set(attr_b)):
        return False, build_explain(0, tok, w, fz, "attribute conflict")

    # ========================
    # FINAL SCORE
    # ========================
    score = compute_score(tok, w, fz)

    score += flavor_penalty(attr_full_a, attr_full_b)
    score += sugar_penalty
    score += anti_penalty   # ⭐ FIX QUAN TRỌNG

    # ========================
    # PREFER SPECIFIC NAME
    # ========================
    if len(tb) > len(ta):
        score += 0.05

    # ========================
    # DECISION
    # ========================
    if score >= THRESHOLD_MATCH:
        return True, build_explain(score, tok, w, fz, "strong match")

    elif score >= THRESHOLD_REVIEW:
        return False, build_explain(score, tok, w, fz, "review")

    else:
        return False, build_explain(score, tok, w, fz, "low score")