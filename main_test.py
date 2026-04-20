# TEST / DEBUG MATCHING LOGIC
# ===========================
from src.matcher import match_product
from src.loader import load_vocab

def main():
    synonym_map = load_vocab("vocab.xlsx")

    A = "cao atiso hũ 250gg"
    B = "thuốc Atiso hủ 250g"

    matched, explain = match_product(A, B, synonym_map, debug=True)

    print("MATCH:", matched)
    print(explain)

if __name__ == "__main__":
    main()