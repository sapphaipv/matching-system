def resolve_one_to_one(candidates):
    clean_candidates = []

    for x in candidates:
        if isinstance(x, dict):
            clean_candidates.append(x)

        elif isinstance(x, (list, tuple)):
            if len(x) >= 3:
                clean_candidates.append({
                    "hd_index": x[0],
                    "sp_index": x[1],
                    "score": x[2]
                })

    # 🔥 chỉ làm việc với dict
    candidates = sorted(clean_candidates, key=lambda x: x["score"], reverse=True)

    used_hd = set()
    used_sp = set()
    results = []

    for c in candidates:
        if c["hd_index"] in used_hd:
            continue
        if c["sp_index"] in used_sp:
            continue

        results.append(c)
        used_hd.add(c["hd_index"])
        used_sp.add(c["sp_index"])

    return results