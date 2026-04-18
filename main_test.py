# TEST / DEBUG MATCHING LOGIC
# ===========================
from src.matcher import match_product
from src.loader import load_vocab

def main():
    synonym_map = load_vocab("vocab.xlsx")

    A = "xoai say deo ola 200g"
    B = "xoai say deo ola 200 g"

    matched, explain = match_product(A, B, synonym_map, debug=True)

    print("MATCH:", matched)
    print(explain)

if __name__ == "__main__":
    main()