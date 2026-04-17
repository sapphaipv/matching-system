import pandas as pd
from src.normalize import normalize
from src.matcher import build_candidates
from src.resolver import resolve_one_to_one
from src.config import *

def run_pipeline():
    df_hd = pd.read_excel(HD_FILE)
    df_sp = pd.read_excel(SP_FILE)

    df_hd["name_norm"] = df_hd["Tên hàng hóa, dịch vụ"].apply(normalize)
    df_sp["name_norm"] = df_sp["Tên hàng"].apply(normalize)

    candidates, rejected = build_candidates(df_hd, df_sp)
    matches = resolve_one_to_one(candidates)

    result = []
    for m in matches:
        hd = df_hd.loc[m["hd_index"]]
        sp = df_sp.loc[m["sp_index"]]

        result.append({
            "Tên HD": hd["Tên hàng hóa, dịch vụ"],
            "Tên SP": sp["Tên hàng"],
            "Mã hàng": sp["Mã hàng"],
            "Score": m["score"]
        })

    pd.DataFrame(result).to_excel(OUTPUT_FILE, index=False)

    # 🔥 export rejected
    pd.DataFrame(rejected, columns=["hd_index", "sp_index", "reason"])\
        .to_excel("output/rejected_log.xlsx", index=False)

    print(f"✅ Done SAFE! Match: {len(result)} / {len(df_hd)}")