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

def load_vocab(path="vocab.xlsx"):
    import pandas as pd

    xls = pd.ExcelFile(path)

    # ========================
    # 1. SYNONYM MAP (cũ)
    # ========================
    df_syn = pd.read_excel(xls, sheet_name="Synonym_Map")
    df_syn.columns = [c.strip().lower() for c in df_syn.columns]

    if "keyword" not in df_syn.columns:
        raise Exception("❌ Sheet 'Synonym_Map' thiếu cột 'keyword'")

    df_syn["keyword"] = df_syn["keyword"].astype(str).str.strip().str.lower()

    synonym_vocab = df_syn.to_dict("records")

    # ========================
    # 2. ATTRIBUTE MAP (mới)
    # ========================
    if "Attribute_Map" in xls.sheet_names:
        df_attr = pd.read_excel(xls, sheet_name="Attribute_Map")
        df_attr.columns = [c.strip().lower() for c in df_attr.columns]

        if "keyword" not in df_attr.columns or "type" not in df_attr.columns:
            raise Exception("❌ Sheet 'Attribute_Map' cần 'keyword' và 'type'")

        df_attr["keyword"] = df_attr["keyword"].astype(str).str.strip().str.lower()
        df_attr["type"] = df_attr["type"].astype(str).str.strip().str.lower()

        attribute_vocab = df_attr.to_dict("records")
    else:
        attribute_vocab = []

    return {
        "synonym": synonym_vocab,
        "attribute": attribute_vocab
    }

# ========================
# PRODUCT LIST (SP)
# ========================

def load_products(path, sheet="SP"):
    import pandas as pd

    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [c.strip().lower() for c in df.columns]

    # detect column
    name_col = None
    code_col = None

    for col in df.columns:
        if col in ["tên hàng", "ten hang"]:
            name_col = col
        if col in ["mã hàng", "ma hang", "code"]:
            code_col = col

    if name_col is None:
        raise Exception("❌ Không tìm thấy cột 'Tên hàng' trong SP")

    # fallback nếu chưa có mã
    if code_col is None:
        df["mã hàng"] = ""
        code_col = "mã hàng"

    df[name_col] = df[name_col].astype(str).str.strip()

    return df[[code_col, name_col]].dropna().to_dict("records")

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