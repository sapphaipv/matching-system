# main.py
# PRODUCTION RUN - MATCH REAL DATA
# ================================
# main.py

import pandas as pd
from src.matcher import match_product
from src.loader import load_vocab, load_products, load_invoices

# ========================
# CONFIG
# ========================
FILE_DATA = "data/raw/data.xlsx"   # file chứa SP + HD
FILE_VOCAB = "vocab.xlsx"

OUTPUT_FILE = "output/result.xlsx"


def main():
    print("🚀 Loading data...")

    # load vocab
    synonym_map = load_vocab(FILE_VOCAB)

    # load data
    products = load_products(FILE_DATA, sheet="SP")
    invoices = load_invoices(FILE_DATA, sheet="HD")

    print(f"Products: {len(products)}")
    print(f"Invoices: {len(invoices)}")

    results = []

    print("🔍 Matching...")

    # ========================
    # MATCH LOOP
    # ========================
    try:
        for i, inv in enumerate(invoices):
            inv = str(inv).strip()   # 🔥 FIX 1

            # 🔥 (A) progress
            if i % 100 == 0:
                print(f"Processed {i}/{len(invoices)}")

            best_match = None
            best_score = 0
            best_explain = None

            for prod in products:
                prod = str(prod).strip()   # 🔥 FIX 2
                is_match, explain = match_product(inv, prod, synonym_map)
                score = explain["score"]

                if score > best_score:
                    best_score = score
                    best_match = prod
                    best_explain = explain

            results.append({
                "invoice_name": inv,
                "matched_product": best_match,
                "score": best_score,
                "reason": best_explain["detail"]["reason"] if best_explain else ""
            })

            # 🔥 (B) autosave
            if i % 200 == 0 and i > 0:
                pd.DataFrame(results).to_excel("output/result_temp.xlsx", index=False)

    except KeyboardInterrupt:
        print("\n⛔ Stopped by user")
        pd.DataFrame(results).to_excel("output/result_partial.xlsx", index=False)
        print("💾 Saved partial result")

    # ========================
    # SAVE OUTPUT
    # ========================
    df = pd.DataFrame(results)

    # df.to_excel(OUTPUT_FILE, index=False)

    # chỉ save full khi chạy xong bình thường
    if i == len(invoices) - 1:
        df.to_excel(OUTPUT_FILE, index=False)

    print("✅ DONE")
    print(f"📄 Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()