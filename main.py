import pandas as pd
from src.matcher import match_product
from src.loader import load_vocab, load_products, load_invoices

FILE_DATA = "data/raw/data.xlsx"
FILE_VOCAB = "vocab.xlsx"
OUTPUT_FILE = "output/result.xlsx"


def main():
    print("🚀 Loading data...")

    vocab = load_vocab(FILE_VOCAB)
    synonym_map = vocab["synonym"]
    attribute_vocab = vocab["attribute"]

    products = load_products(FILE_DATA, sheet="SP")
    invoices = load_invoices(FILE_DATA, sheet="HD")

    print(f"Products: {len(products)}")
    print(f"Invoices: {len(invoices)}")

    results = []

    print("🔍 Matching...")

    for i, inv in enumerate(invoices):
        inv = str(inv).strip()

        if i % 100 == 0:
            print(f"Processed {i}/{len(invoices)}")

        best_match = None
        best_score = 0
        best_code = ""
        best_explain = None

        for prod in products:
            prod_name = str(prod["tên hàng"]).strip()

            is_match, explain = match_product(
                inv,
                prod_name,
                synonym_map,
                attribute_vocab
            )

            score = explain["score"]

            # 🔥 FIX QUAN TRỌNG
            if is_match and score > best_score:
                best_score = score
                best_match = prod_name
                best_code = prod["mã hàng"]
                best_explain = explain

        results.append({
            "invoice_name": inv,
            "matched_product": best_match,
            "mã hàng": best_code,
            "score": best_score,
            "reason": best_explain["detail"]["reason"] if best_explain else ""
        })

    df = pd.DataFrame(results)

    # CLEAN
    df = df[df["matched_product"].notna()]
    df = df[df["matched_product"].astype(str).str.strip() != ""]
    df = df[df["score"] > 0]
    df = df.drop_duplicates(subset=["matched_product"])

    cols = ["mã hàng", "matched_product"] + [
        c for c in df.columns if c not in ["mã hàng", "matched_product"]
    ]
    df = df[cols]

    df.to_excel(OUTPUT_FILE, index=False)

    print("✅ DONE")


if __name__ == "__main__":
    main()