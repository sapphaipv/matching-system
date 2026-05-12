# main.py
# ================================
# PRODUCTION RUN - OPTIMIZED MATCHING
# ================================

import pandas as pd

from src.matcher import match_product
from src.loader import load_vocab, load_products, load_invoices

from src.normalizer import normalize_text
from src.tokenizer import tokenize
from src.weight_parser import parse_weight

# ========================
# CONFIG
# ========================
FILE_DATA = "data/raw/data.xlsx"
FILE_VOCAB = "vocab.xlsx"
OUTPUT_FILE = "output/result.xlsx"


def main():
    print("🚀 Loading data...")

    # ========================
    # LOAD
    # ========================
    vocab = load_vocab(FILE_VOCAB)
    synonym_map = vocab["synonym"]
    attribute_vocab = vocab["attribute"]

    products = load_products(FILE_DATA, sheet="SP")
    invoices = load_invoices(FILE_DATA, sheet="HD")

    print(f"Products: {len(products)}")
    print(f"Invoices: {len(invoices)}")

    # ========================
    # PREPROCESS PRODUCTS
    # ========================
    print("⚙️ Preprocessing products...")

    product_cache = []
    product_index = {}
    weight_bucket = {}

    for prod in products:
        name = str(prod["tên hàng"]).strip()

        norm = normalize_text(name)
        tokens = tokenize(norm)
        weight = parse_weight(norm)

        item = {
            "raw": prod,
            "name": name,
            "norm": norm,
            "tokens": tokens,
            "weight": weight
        }

        product_cache.append(item)

        # inverted index
        for t in tokens:
            product_index.setdefault(t, []).append(item)

        # weight bucket
        if weight is not None:
            weight_bucket.setdefault(weight, []).append(item)

    print(f"✅ Product cache built: {len(product_cache)}")
    print(f"🔎 Index size: {len(product_index)} tokens")

    # ========================
    # MATCH LOOP
    # ========================
    print("🔍 Matching...")

    results = []

    for i, inv in enumerate(invoices):
        inv = str(inv).strip()

        if i % 100 == 0:
            print(f"Processed {i}/{len(invoices)}")

        best_match = None
        best_score = 0
        best_code = ""
        best_explain = None

        # ========================
        # PREPROCESS INVOICE (CACHE)
        # ========================
        norm_inv = normalize_text(inv)
        tokens = tokenize(norm_inv)
        inv_weight = parse_weight(norm_inv)

        # ========================
        # GET CANDIDATES (TOKEN)
        # ========================
        candidates = set()

        for t in tokens:
            if t in product_index:
                for p in product_index[t]:
                    candidates.add(id(p))

        # ========================
        # FILTER BY WEIGHT
        # ========================
        if inv_weight is not None:
            if inv_weight in weight_bucket:
                weight_candidates = set(id(p) for p in weight_bucket[inv_weight])
                candidates = candidates.intersection(weight_candidates)

        # fallback nếu rỗng
        if not candidates:
            candidates = set(id(p) for p in product_cache)

        id_map = {id(p): p for p in product_cache}

        # ========================
        # MATCH ONLY CANDIDATES
        # ========================
        for pid in candidates:
            p = id_map[pid]

            # 🔥 length filter (cheap but effective)
            if abs(len(tokens) - len(p["tokens"])) > 5:
                continue

            is_match, explain = match_product(
                inv,
                p["name"],
                synonym_map,
                attribute_vocab
            )

            score = explain["score"]

            # 🔥 FIX CRITICAL BUG
            if is_match and score > best_score:
                best_score = score
                best_match = p["name"]
                best_code = p["raw"]["mã hàng"]
                best_explain = explain

        results.append({
            "invoice_name": inv,
            "matched_product": best_match,
            "mã hàng": best_code,
            "score": best_score,
            "reason": best_explain["detail"]["reason"] if best_explain else ""
        })

        # autosave nhẹ (an toàn)
        if i % 300 == 0 and i > 0:
            pd.DataFrame(results).to_excel("output/result_temp.xlsx", index=False)

    # ========================
    # CLEAN OUTPUT
    # ========================
    df = pd.DataFrame(results)

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
    print(f"📄 Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
