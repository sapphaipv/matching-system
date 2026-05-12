from src.matcher import match_product
from src.loader import load_vocab

def run_tests():
    synonym_map = load_vocab("vocab.xlsx")

    tests = [
        # ✅ SHOULD MATCH
        ("xoai say deo ola 200g", "xoai say deo ola 200 g", True),
        ("cf sua da", "cafe sua da", True),
        ("xoai say deo 200g", "xoai say deo", True),

        # ❌ SHOULD FAIL
        ("cafe 200g", "cafe 500g", False),
        ("nuoc ngot", "xa hoi", False),
    ]

    correct = 0

    for a, b, expected in tests:
        result, explain = match_product(a, b, synonym_map)

        ok = (result == expected)
        if ok:
            correct += 1

        print("="*50)
        print("A:", a)
        print("B:", b)
        print("Expected:", expected)
        print("Result:", result)
        print("Explain:", explain)
        print("OK:", ok)

    print("\nACCURACY:", correct, "/", len(tests))


if __name__ == "__main__":
    run_tests()