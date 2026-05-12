STOPWORDS = set([
    "bánh", "g", "gram", "ml", "chai", "túi", "hộp", "lon"
])

def clean_tokens(tokens):
    return [t for t in tokens if t not in STOPWORDS]