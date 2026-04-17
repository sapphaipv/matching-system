from tqdm import tqdm
from src.scorer import final_score
from src.config import THRESHOLD_WEAK

def build_candidates(df_hd, df_sp):
    candidates = []

    for i_hd, row_hd in tqdm(df_hd.iterrows(), total=len(df_hd)):
        for i_sp, row_sp in df_sp.iterrows():

            score = final_score(row_hd["name_norm"], row_sp["name_norm"])

            if score >= THRESHOLD_WEAK:
                candidates.append({
                    "hd_index": i_hd,
                    "sp_index": i_sp,
                    "score": score
                })

    return candidates