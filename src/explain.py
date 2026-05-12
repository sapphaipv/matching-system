# src/explain.py

def build_explain(score, token_overlap, weight, fuzzy, reason):
    return {
        "score": round(score, 3),
        "detail": {
            "token_overlap": round(token_overlap, 3),
            "weight": weight,
            "fuzzy": round(fuzzy, 3),
            "reason": reason
        }
    }