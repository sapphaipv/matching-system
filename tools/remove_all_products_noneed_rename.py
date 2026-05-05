import os
import pandas as pd

store_name = "96TP"
input_dir = r"D:\CTY\TenSanPham\\" + store_name

file_hd = os.path.join(input_dir, "HD_Products.xlsx")
file_result = os.path.join(input_dir, "Result.xlsx")
output_file = os.path.join(input_dir, "HD_Products_Clean.xlsx")

def xoa_ten_hang():

    col = "Tên hàng"

    # Đọc dữ liệu
    df_hd = pd.read_excel(file_hd)
    df_rs = pd.read_excel(file_result)

    # Chuẩn hóa
    df_hd[col] = df_hd[col].astype(str).str.strip()
    df_rs[col] = df_rs[col].astype(str).str.strip()

    # Tập tên cần xóa
    ten_xoa = set(df_rs[col])

    # Lọc giữ lại những dòng KHÔNG nằm trong Result
    df_clean = df_hd[~df_hd[col].isin(ten_xoa)].copy()

    # Ghi file
    df_clean.to_excel(output_file, index=False)

    print(f"Tổng ban đầu: {len(df_hd)}")
    print(f"Số dòng bị xóa: {len(df_hd) - len(df_clean)}")
    print(f"Còn lại: {len(df_clean)}")
    print(f"✔ File xuất: {output_file}")


if __name__ == "__main__":
    xoa_ten_hang()
