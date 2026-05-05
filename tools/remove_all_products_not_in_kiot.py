# 1) Giữ lại trong PRODUCT_NAME:
#    → những dòng CÓ "Mã hàng" tồn tại trong SanPham.xlsx

# 2) Xuất ra KhongCo_MaHang.xlsx:
#    → những dòng KHÔNG có "Mã hàng" trong SanPham.xlsx


import pandas as pd

PRODUCT_NAME = "TenHang_Tuyet.xlsx"

def xu_ly_ma_hang():

    store_name = "205NTT"
    path_name = r"D:\CTY\TenSanPham\\" + store_name

    file_tenhang = path_name + "\\" + PRODUCT_NAME
    file_sanpham = path_name + "\\" + "SanPham.xlsx"

    output_khong_co = path_name + "\\" + "KhongCo_MaHang.xlsx"
    output_da_loc = path_name + "\\" + PRODUCT_NAME + "_Filtered.xlsx"

    col = "Mã hàng"

    # Đọc dữ liệu
    df_tenhang = pd.read_excel(file_tenhang)
    df_sanpham = pd.read_excel(file_sanpham)

    # Chuẩn hóa
    df_tenhang[col] = df_tenhang[col].astype(str).str.strip()
    df_sanpham[col] = df_sanpham[col].astype(str).str.strip()

    # Tạo set để so sánh nhanh
    ma_hang_set = set(df_sanpham[col])

    # 1. Các dòng CÓ trong SanPham
    df_co = df_tenhang[df_tenhang[col].isin(ma_hang_set)].copy()

    # 2. Các dòng KHÔNG có trong SanPham
    df_khong_co = df_tenhang[~df_tenhang[col].isin(ma_hang_set)].copy()

    # Ghi file
    df_co.to_excel(output_da_loc, index=False)
    df_khong_co.to_excel(output_khong_co, index=False)

    print(f"Tổng TenHang: {len(df_tenhang)}")
    print(f"Có mã hàng: {len(df_co)}")
    print(f"Không có mã hàng: {len(df_khong_co)}")
    print(f"✔ File đã lọc: {output_da_loc}")
    print(f"✔ File không có mã: {output_khong_co}")


if __name__ == "__main__":
    xu_ly_ma_hang()

