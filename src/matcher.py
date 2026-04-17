# src/matcher.py

from src.normalizer import normalize_text
from src.tokenizer import tokenize
from src.synonym import expand_tokens
from src.weight_parser import parse_weight
from src.scorer import token_overlap, weight_score, fuzzy, compute_score
from src.explain import build_explain
from src.config import THRESHOLD_MATCH, THRESHOLD_REVIEW


def match_product(a, b, synonym_map, debug=False):
    # ========================
    # NORMALIZE
    # ========================
    na = normalize_text(a)
    nb = normalize_text(b)

    # ========================
    # TOKENIZE
    # ========================
    ta = tokenize(na)
    tb = tokenize(nb)

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

    # ========================
    # HARD RULE: WEIGHT
    # chỉ check khi cả 2 có
    # ========================
    if w1 is not None and w2 is not None:
        if w1 != w2:
            return False, build_explain(
                0, 0, -1, 0,
                "weight mismatch (hard)"
            )

    # ========================
    # COMPUTE FEATURES
    # ========================
    tok = token_overlap(ea, eb)
    w = weight_score(w1, w2)
    fz = fuzzy(na, nb)

    # ========================
    # GUARDRAILS
    # ========================

    # ❌ token quá thấp → reject
    if tok < 0.5:
        return False, build_explain(
            0, tok, w, fz,
            "low token overlap"
        )

    # ⚠️ nếu thiếu weight → cần token cao hơn
    if (w1 is None or w2 is None) and tok < 0.7:
        return False, build_explain(
            0, tok, w, fz,
            "missing weight but weak token"
        )

    # ========================
    # FINAL SCORE
    # ========================
    score = compute_score(tok, w, fz)

    # ========================
    # DEBUG
    # ========================
    if debug:
        print("DEBUG:", {
            "A": a,
            "B": b,
            "na": na,
            "nb": nb,
            "tokens_a": ta,
            "tokens_b": tb,
            "token_overlap": tok,
            "weight_a": w1,
            "weight_b": w2,
            "weight_score": w,
            "fuzzy": fz,
            "score": score
        })

    # ========================
    # DECISION
    # ========================
    if score >= THRESHOLD_MATCH:
        return True, build_explain(score, tok, w, fz, "strong match")

    elif score >= THRESHOLD_REVIEW:
        return False, build_explain(score, tok, w, fz, "review")

    else:
        return False, build_explain(score, tok, w, fz, "low score")