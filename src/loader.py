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
    df = pd.read_excel(path, sheet_name=sheet)
    df = normalize_columns(df)

    # detect column name linh hoạt
    name_col = None
    for col in ["ten hang", "ten_hang", "name"]:
        if col in df.columns:
            name_col = col
            break

    if not name_col:
        raise Exception("❌ SP sheet missing product name column")

    products = []

    for _, row in df.iterrows():
        name = safe_str(row[name_col])
        if name:
            products.append(name)

    return products


# ========================
# INVOICE LIST (HD)
# ========================

def load_invoices(path, sheet="HD"):
    df = pd.read_excel(path, sheet_name=sheet)
    df = normalize_columns(df)

    name_col = None
    for col in ["ten hang", "ten_hang", "description"]:
        if col in df.columns:
            name_col = col
            break

    if not name_col:
        raise Exception("❌ HD sheet missing product column")

    invoices = []

    for _, row in df.iterrows():
        name = safe_str(row[name_col])
        if name:
            invoices.append(name)

    return invoices