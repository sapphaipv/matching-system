import pandas as pd
import random
import re


# ---------------------------
# LOAD CONFUSION MAP
# ---------------------------

def load_confusion_map(path):
    return pd.read_excel(path)


# ---------------------------
# APPLY CONFUSION ON INVOICE
# ---------------------------

def apply_confusion(text, confusion_df, prob=0.3):
    text = str(text).lower()

    for _, row in confusion_df.iterrows():
        src = str(row["source"])
        tgt = str(row["target"])

        if src in text and random.random() < prob:
            text = text.replace(src, tgt)

    return text


# ---------------------------
# SIMPLE MATCH FUNCTION (FAKE HUMAN)
# ---------------------------

def fake_match(noisy_text, product_pool):
    """
    giả lập người chọn sản phẩm dựa trên text bị nhiễu
    """
    candidates = []

    for p in product_pool:
        p_lower = str(p).lower()

        # nếu có overlap keyword → candidate
        if any(word in p_lower for word in noisy_text.split()):
            candidates.append(p)

    if candidates:
        return random.choice(candidates)

    return random.choice(product_pool)


# ---------------------------
# MAIN
# ---------------------------

def generate_adversarial_gt(
    file_path,
    confusion_path,
    output_path,
    correct_ratio=0.7
):
    try:
        df = pd.read_excel(file_path)
    except:
        print("File not found! " + file_path)
        return
    
    confusion_df = load_confusion_map(confusion_path)

    required_cols = ["invoice_name", "matched_product"]
    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"❌ Missing column: {col}")

    product_pool = df["matched_product"].dropna().unique().tolist()

    gt_list = []

    for _, row in df.iterrows():
        invoice = row["invoice_name"]
        matched = row["matched_product"]

        r = random.random()

        if r < correct_ratio:
            # giữ đúng (giả lập system đúng)
            gt = matched

        else:
            # tạo lỗi có chủ đích
            noisy = apply_confusion(invoice, confusion_df, prob=0.5)

            # fake human chọn dựa trên text bị nhiễu
            gt = fake_match(noisy, product_pool)

        gt_list.append(gt)

    df["ground_truth"] = gt_list
    df.to_excel(output_path, index=False)

    print(f"✅ Saved: {output_path}")

if __name__ == "__main__":

    data = [
        {"source": "cám", "target": "cam"},
        {"source": "cacao", "target": "cao"},
        {"source": "xoài", "target": "mít"},
        {"source": "200", "target": "180"},
        {"source": "túi", "target": "hộp"},
    ]

    df = pd.DataFrame(data)
    df.to_excel("eval/data/confusion_map.xlsx", index=False)

    print("✅ Created confusion_map.xlsx")


    generate_adversarial_gt(
        file_path="output/result_16.3.3.xlsx",
        confusion_path="eval/data/confusion_map.xlsx",
        output_path="output/result_16.3.3_fake_gt.xlsx",
        correct_ratio=0.7
    )