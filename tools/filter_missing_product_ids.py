import pandas as pd
import argparse


def find_column(df, target_name):
    """
    Tìm cột không phân biệt hoa/thường + bỏ khoảng trắng
    """
    target = target_name.lower().strip()

    for col in df.columns:
        if col.lower().strip() == target:
            return col

    return None


def filter_missing_product_ids(file_a, file_b, output_file):
    df_a = pd.read_excel(file_a)
    df_b = pd.read_excel(file_b)

    # 🔥 Tìm cột linh hoạt
    col_a = find_column(df_a, "mã hàng")
    col_b = find_column(df_b, "mã hàng")

    if not col_a:
        raise Exception(f"❌ File A không có cột 'Mã hàng'. Columns: {list(df_a.columns)}")

    if not col_b:
        raise Exception(f"❌ File B không có cột 'Mã hàng'. Columns: {list(df_b.columns)}")

    # Chuẩn hóa dữ liệu
    ma_hang_a = df_a[col_a].astype(str).str.strip()
    ma_hang_b = set(df_b[col_b].astype(str).str.strip())

    # Lọc
    df_filtered = df_a[~ma_hang_a.isin(ma_hang_b)]

    # Save
    df_filtered.to_excel(output_file, index=False)

    print(f"✅ Done!")
    print(f"🔢 Tổng dòng A: {len(df_a)}")
    print(f"🔢 Giữ lại: {len(df_filtered)}")
    print(f"📁 Output: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_a", required=True)
    parser.add_argument("--file_b", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    filter_missing_product_ids(args.file_a, args.file_b, args.output)