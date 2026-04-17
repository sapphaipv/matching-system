from tqdm import tqdm
from src.semantic import parse_product
from src.scorer import final_score
from src.constraints import hard_constraints
from src.config import THRESHOLD_WEAK

def get_main_token(tokens):
    return tokens[0] if tokens else None

def build_sp_index(df_sp):
    index = {}
    for i, row in df_sp.iterrows():
        key = get_main_token(row["parsed"]["tokens"])
        if key:
            index.setdefault(key, []).append((i, row))
    return index

def build_candidates(df_hd, df_sp):
    candidates = []
    rejected = []

    df_hd["parsed"] = df_hd["name_norm"].apply(parse_product)
    df_sp["parsed"] = df_sp["name_norm"].apply(parse_product)

    sp_index = build_sp_index(df_sp)

    for i_hd, row_hd in tqdm(df_hd.iterrows(), total=len(df_hd)):
        p_hd = row_hd["parsed"]
        key = get_main_token(p_hd["tokens"])

        if key not in sp_index:
            continue

        for i_sp, row_sp in sp_index[key]:
            p_sp = row_sp["parsed"]

            # 🔒 HARD CONSTRAINT
            if not hard_constraints(p_hd, p_sp):
                rejected.append((i_hd, i_sp, "constraint_fail"))
                continue

            score = final_score(
                p_hd, p_sp,
                row_hd["name_norm"],
                row_sp["name_norm"]
            )

            if score >= THRESHOLD_WEAK:
                candidates.append({
                    "hd_index": i_hd,
                    "sp_index": i_sp,
                    "score": score
                })

    return candidates, rejected