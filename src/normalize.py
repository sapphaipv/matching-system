import re
import pandas as pd

def normalize(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("gram", "g").replace("gr", "g")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text