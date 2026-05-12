import pandas as pd


def load_data(file_path):
    df = pd.read_excel(file_path)

    required_cols = [
        "invoice_name",
        "matched_product",
        "ground_truth"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"❌ Missing column: {col}")

    return df


# ---------------------------
# BASIC METRICS
# ---------------------------

def compute_metrics(df):
    total = len(df)

    correct = (df["matched_product"] == df["ground_truth"]).sum()
    incorrect = total - correct

    accuracy = correct / total if total > 0 else 0

    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": round(accuracy, 4)
    }


# ---------------------------
# PRECISION / RECALL
# ---------------------------

def compute_precision_recall(df):
    """
    Treat matching as classification:
    predicted = matched_product
    actual = ground_truth
    """

    unique_products = df["ground_truth"].dropna().unique()

    results = []

    for product in unique_products:
        tp = ((df["matched_product"] == product) &
              (df["ground_truth"] == product)).sum()

        fp = ((df["matched_product"] == product) &
              (df["ground_truth"] != product)).sum()

        fn = ((df["matched_product"] != product) &
              (df["ground_truth"] == product)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        results.append({
            "product": product,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn
        })

    return pd.DataFrame(results)


# ---------------------------
# ERROR ANALYSIS
# ---------------------------

def get_wrong_matches(df):
    wrong_df = df[df["matched_product"] != df["ground_truth"]].copy()
    return wrong_df


def get_confusion_pairs(df):
    """
    Xem hay nhầm cái gì với cái gì
    """
    wrong_df = df[df["matched_product"] != df["ground_truth"]]

    pairs = (
        wrong_df
        .groupby(["ground_truth", "matched_product"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    return pairs


# ---------------------------
# MAIN RUN
# ---------------------------

def evaluate(file_path):
    df = load_data(file_path)

    print("📊 BASIC METRICS")
    metrics = compute_metrics(df)
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("\n📊 PRECISION / RECALL (per product)")
    pr_df = compute_precision_recall(df)
    print(pr_df.head(10))

    print("\n❌ TOP CONFUSIONS")
    conf_df = get_confusion_pairs(df)
    print(conf_df.head(10))

    # Export debug files
    pr_df.to_excel("eval/data/precision_recall.xlsx", index=False)
    conf_df.to_excel("eval/data/confusions.xlsx", index=False)
    get_wrong_matches(df).to_excel("eval/data/wrong_matches.xlsx", index=False)

    print("\n✅ Exported:")
    print("- precision_recall.xlsx")
    print("- confusions.xlsx")
    print("- wrong_matches.xlsx")