# src/scorer.py

from difflib import SequenceMatcher


# ========================
# TOKEN OVERLAP
# ========================
def token_overlap(exp1, exp2):
    """
    exp1, exp2 = list of token groups
    ví dụ:
    [["cf", "cafe"], ["sua"], ["da"]]
    """

    match = 0
    total = len(exp1)

    for g1 in exp1:
        for g2 in exp2:
            if any(t in g2 for t in g1):
                match += 1
                break

    return match / total if total > 0 else 0


# ========================
# WEIGHT SCORE (FIX LỖI CHÍNH)
# ========================
def weight_score(w1, w2):
    if w1 and w2:
        if w1 == w2:
            return 1
        elif abs(w1 - w2) / max(w1, w2) < 0.1:
            return 0.5
        else:
            return -1
    elif not w1 or not w2:
        return 0.2  # recovery nhẹ


# ========================
# FUZZY MATCH
# ========================
def fuzzy(a, b):
    return SequenceMatcher(None, a, b).ratio()


# ========================
# FINAL SCORE
# ========================
def compute_score(tok, weight, fuzzy_score):
    return (
        0.5 * tok +
        0.2 * weight +
        0.3 * fuzzy_score
    )

def flavor_penalty(attr_a, attr_b):
    f1 = attr_a.get("flavor", [])
    f2 = attr_b.get("flavor", [])

    if f1 and f2:
        if set(f1) != set(f2):
            return -0.5

    return 0