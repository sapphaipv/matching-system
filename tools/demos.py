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

# def xoa_ma_hang():

#     col = "Mã hàng"

#     # Đọc dữ liệu
#     df_sp = pd.read_excel(file_sp)
#     df_rs = pd.read_excel(file_result)

#     # Chuẩn hóa
#     df_sp[col] = df_sp[col].astype(str).str.strip()
#     df_rs[col] = df_rs[col].astype(str).str.strip()

#     # Tạo tập mã cần xóa
#     ma_xoa = set(df_rs[col])

#     # Lọc giữ lại những dòng KHÔNG nằm trong Result
#     df_clean = df_sp[~df_sp[col].isin(ma_xoa)].copy()

#     # Ghi file
#     df_clean.to_excel(output_file, index=False)

#     print(f"Tổng ban đầu: {len(df_sp)}")
#     print(f"Số dòng bị xóa: {len(df_sp) - len(df_clean)}")
#     print(f"Còn lại: {len(df_clean)}")
#     print(f"✔ File xuất: {output_file}")


# if __name__ == "__main__":
#     xoa_ma_hang()

# def tim_trung():
#     excel_file = r"tools\excel_files\KQ.xlsx"

#     df = pd.read_excel(excel_file)

#     # Chuẩn hóa
#     df["Tên file"] = df["Tên file"].astype(str).str.strip()

#     # Tìm các dòng trùng
#     duplicates = df[df.duplicated(subset=["Tên file"], keep=False)]

#     # Sắp xếp cho dễ nhìn
#     duplicates = duplicates.sort_values(by="Tên file")

#     # Xuất ra file
#     duplicates.to_excel("duplicates.xlsx", index=False)

#     print(f"Số dòng trùng: {len(duplicates)}")
#     print("Đã lưu vào duplicates.xlsx")

#     # In nhanh ra màn hình
#     print("\nDanh sách trùng:")
#     print(duplicates["Tên file"].value_counts())


# if __name__ == "__main__":
#     tim_trung()

# def tim_file_thieu():
#     folder_path = r"d:\CTY\HoaDonXML\205Ntt\HDDT-In-2026-01"
#     excel_file = r"tools\excel_files\KQ.xlsx"
#     output_file = r"tools\excel_files\missing_in_folder.xlsx"

#     # 1. Lấy danh sách file trong thư mục
#     files_in_folder = {
#         f.strip() for f in os.listdir(folder_path)
#         if f.lower().endswith(".zip")
#     }

#     # 2. Đọc Excel
#     df = pd.read_excel(excel_file)

#     files_in_excel = {
#         str(f).strip() for f in df["Tên file"]
#     }

#     # 3. Tìm file có trong Excel nhưng KHÔNG có trong folder
#     missing_files = sorted(files_in_excel - files_in_folder)

#     # 4. Xuất kết quả
#     df_out = pd.DataFrame({
#         "File thiếu trong folder": missing_files
#     })

#     df_out.to_excel(output_file, index=False)

#     print(f"Tổng Excel: {len(files_in_excel)}")
#     print(f"Tổng Folder: {len(files_in_folder)}")
#     print(f"Số file thiếu: {len(missing_files)}")
#     print(f"Đã lưu: {output_file}")


# if __name__ == "__main__":
#     tim_file_thieu()

# def tao_ten_file():
#     input_file = r"tools\excel_files\HDDT 205_2026-01.xlsx"
#     output_file = r"tools\excel_files\KQ.xlsx"

#     # Đọc file Excel
#     df = pd.read_excel(input_file)

#     # Lấy cột cần thiết
#     mst = df["MST"].astype(str).str.strip()
#     so_hd = df["Số hóa đơn"].astype(str).str.strip()

#     # Tạo tên file
#     file_names = mst + "_" + so_hd + ".zip"

#     # Xuất ra DataFrame mới
#     df_out = pd.DataFrame({
#         "Tên file": file_names
#     })

#     # Ghi ra Excel
#     df_out.to_excel(output_file, index=False)

#     print(f"Đã tạo {len(df_out)} tên file → {output_file}")

# if __name__ == "__main__":
#     tao_ten_file()