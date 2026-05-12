# Tách file Excel của Kiot Việt thành 2 file:
# 1- Các dòng có giá trị cột "Nhóm hàng (3 cấp)" bắt đầu bởi "_SỬA_TÊN_"
# 2- Những dòng còn lại
# ======================================================================
import pandas as pd

def tach_file_sanpham():
    store_name = "96TP"
    path_name = r"D:\CTY\TenSanPham\\" + store_name

    input_file = path_name + "\\" + "SanPham.xlsx"
    file_rename = path_name + "\\" + "SanPham_Rename.xlsx"
    file_done = path_name + "\\" + "SanPham_Done.xlsx"

    # Đọc file Excel (giữ nguyên cấu trúc)
    df = pd.read_excel(input_file)

    col_name = "Nhóm hàng(3 Cấp)"

    # Chuẩn hóa tránh lỗi NaN
    df[col_name] = df[col_name].astype(str)

    # Điều kiện bắt đầu bằng "_SỬA_TÊN_"
    mask = df[col_name].str.startswith("_SỬA_TÊN_")

    # Tách 2 nhóm
    df_rename = df[mask].copy()
    df_done = df[~mask].copy()

    # Ghi ra file (giữ nguyên cột)
    df_rename.to_excel(file_rename, index=False)
    df_done.to_excel(file_done, index=False)

    print(f"Tổng dòng: {len(df)}")
    print(f"Dòng cần rename: {len(df_rename)}")
    print(f"Dòng còn lại: {len(df_done)}")


if __name__ == "__main__":
    tach_file_sanpham()