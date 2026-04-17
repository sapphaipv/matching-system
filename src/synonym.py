# src/synonym.py

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
    expanded = []

    for t in tokens:
        if t in synonym_map:
            expanded.append([t] + synonym_map[t])
        else:
            expanded.append([t])

    return expanded