import pandas as pd


# ========================
# COMMON
# ========================

def normalize_columns(df):
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def safe_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


# ========================
# VOCAB (Synonym)
# ========================

def load_vocab(path="vocab.xlsx", sheet="Synonym_Map"):
    df = pd.read_excel(path, sheet_name=sheet)
    df = normalize_columns(df)

    if "keyword" not in df.columns:
        raise Exception("❌ Synonym_Map missing column 'keyword'")

    synonym_map = {}

    for _, row in df.iterrows():
        key = safe_str(row["keyword"])

        if not key:
            continue

        raw = safe_str(row.get("synonyms", ""))
        values = [v.strip() for v in raw.split(",") if v.strip()]

        synonym_map[key] = values

    return synonym_map


# ========================
# PRODUCT LIST (SP)
# ========================

def load_products(path, sheet="SP"):
    import pandas as pd

    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [c.strip().lower() for c in df.columns]

    for col in ["ten hang", "tên hàng"]:
        if col in df.columns:
            return df[col].dropna().astype(str).tolist()

    return df.iloc[:, 0].dropna().astype(str).tolist()

# ========================
# INVOICE LIST (HD)
# ========================

def load_invoices(path, sheet="HD"):
    import pandas as pd

    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [c.strip().lower() for c in df.columns]

    for col in [
        "tên hàng hóa, dịch vụ",   # 🔥 CÁI NÀY
        "ten hang hoa, dich vu",
        "ten hang",
        "tên hàng"
    ]:
        if col in df.columns:
            return df[col].dropna().astype(str).tolist()

    return df.iloc[:, 0].dropna().astype(str).tolist()