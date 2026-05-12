# src/synonym.py

def build_bidirectional_map(synonym_map):
    """
    Support BOTH formats:

    1. list dict:
        [{"keyword": "cf", "synonyms": "cafe"}]

    2. dict:
        {"cf": ["cafe"]}
    """

    mapping = {}

    # ========================
    # CASE 1: dict
    # ========================
    if isinstance(synonym_map, dict):
        for k, values in synonym_map.items():
            if isinstance(values, str):
                values = [values]

            for v in values:
                k = str(k).strip()
                v = str(v).strip()

                if not k or not v:
                    continue

                mapping.setdefault(k, set()).add(v)
                mapping.setdefault(v, set()).add(k)

    # ========================
    # CASE 2: list of dict
    # ========================
    elif isinstance(synonym_map, list):
        for row in synonym_map:
            if not isinstance(row, dict):
                continue

            k = str(row.get("keyword", "")).strip()
            syns = str(row.get("synonyms", "")).strip()

            if not k or not syns:
                continue

            syn_list = [s.strip() for s in syns.split(",")]

            for s in syn_list:
                mapping.setdefault(k, set()).add(s)
                mapping.setdefault(s, set()).add(k)

    # ========================
    return {k: list(v) for k, v in mapping.items()}


def expand_tokens(tokens, synonym_map):
    """
    Input:
        tokens = ["cf", "sua", "da"]
        synonym_map = {"cf": ["cafe"]}

    Output:
        [
            ["cf", "cafe"],
            ["sua"],
            ["da"]
        ]
    """

    # 🔥 build 2 chiều (chỉ 1 lần)
    bi_map = build_bidirectional_map(synonym_map)

    expanded = []

    for t in tokens:
        if t in bi_map:
            expanded.append([t] + bi_map[t])
        else:
            expanded.append([t])

    return expanded