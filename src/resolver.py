def resolve_one_to_one(candidates):
    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

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