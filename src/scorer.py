from rapidfuzz import fuzz

def score_name(a, b):
    return fuzz.token_set_ratio(a, b)

def keyword_boost(a, b):
    return len(set(a.split()) & set(b.split()))

def final_score(a, b):
    s = score_name(a, b)
    boost = keyword_boost(a, b)
    return s + boost * 2