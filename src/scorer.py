from rapidfuzz import fuzz

def token_overlap(a, b):
    return len(set(a) & set(b))

def variant_score(v1, v2):
    if not v1 and not v2:
        return 0
    if set(v1) == set(v2):
        return 5
    return -10  # khác variant → phạt mạnh

def final_score(p1, p2, text1, text2):
    score = fuzz.token_set_ratio(text1, text2)

    score += token_overlap(p1["tokens"], p2["tokens"]) * 2
    score += variant_score(p1["variant"], p2["variant"])

    return score