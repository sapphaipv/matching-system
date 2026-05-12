def log_unmatched(a, b, file="logs/unmatched.txt"):
    with open(file, "a", encoding="utf-8") as f:
        f.write(f"{a} || {b}\n")