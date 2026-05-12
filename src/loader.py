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
# VOCAB (Synonym + Attribute)
# ========================

def load_vocab(path="vocab.xlsx"):
    xls = pd.ExcelFile(path)

    # ========================
    # 1. SYNONYM MAP (2 chiều)
    # ========================
    df_syn = pd.read_excel(xls, sheet_name="Synonym_Map")
    df_syn.columns = [c.strip().lower() for c in df_syn.columns]

    if "keyword" not in df_syn.columns or "synonyms" not in df_syn.columns:
        raise Exception("❌ Synonym_Map cần 'keyword', 'synonyms'")

    df_syn["keyword"] = df_syn["keyword"].astype(str).str.strip().str.lower()
    df_syn["synonyms"] = df_syn["synonyms"].astype(str).str.strip().str.lower()

    synonym_map = {}

    for _, row in df_syn.iterrows():
        k = row["keyword"]
        syns = [s.strip() for s in row["synonyms"].split(",") if s.strip()]

        for s in syns:
            synonym_map.setdefault(k, set()).add(s)
            synonym_map.setdefault(s, set()).add(k)

    synonym_map = {k: list(v) for k, v in synonym_map.items()}

    # ========================
    # 2. ATTRIBUTE MAP
    # ========================
    attribute_vocab = []

    if "Attribute_Map" in xls.sheet_names:
        df_attr = pd.read_excel(xls, sheet_name="Attribute_Map")
        df_attr.columns = [c.strip().lower() for c in df_attr.columns]

        if "keyword" not in df_attr.columns or "type" not in df_attr.columns:
            raise Exception("❌ Attribute_Map cần 'keyword', 'type'")

        df_attr["keyword"] = df_attr["keyword"].astype(str).str.strip().str.lower()
        df_attr["type"] = df_attr["type"].astype(str).str.strip().str.lower()

        attribute_vocab = df_attr.to_dict("records")

    return {
        "synonym": synonym_map,
        "attribute": attribute_vocab
    }


# ========================
# PRODUCT LIST (SP)
# ========================

def load_products(path, sheet="SP"):
    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [c.strip().lower() for c in df.columns]

    name_col = None
    code_col = None

    for col in df.columns:
        if col in ["tên hàng", "ten hang"]:
            name_col = col
        if col in ["mã hàng", "ma hang", "code"]:
            code_col = col

    if name_col is None:
        raise Exception("❌ Không tìm thấy cột 'Tên hàng' trong SP")

    if code_col is None:
        df["mã hàng"] = ""
        code_col = "mã hàng"

    df[name_col] = df[name_col].astype(str).str.strip()

    return df[[code_col, name_col]].dropna().to_dict("records")


# ========================
# INVOICE LIST (HD)
# ========================

def load_invoices(path, sheet="HD"):
    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [c.strip().lower() for c in df.columns]

    for col in [
        "tên hàng hóa, dịch vụ",
        "ten hang hoa, dich vu",
        "ten hang",
        "tên hàng"
    ]:
        if col in df.columns:
            return df[col].dropna().astype(str).tolist()

    return df.iloc[:, 0].dropna().astype(str).tolist()