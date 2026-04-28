# Lấy dữ liệu từ thư-mục chứa các files HÓA ĐƠN ĐIỆN TỬ
# rồi xuất ra file Excel có các cột "Tên hàng hóa, dịch vụ" và "Đơn giá"
# ======================================================================
import os
import pandas as pd
from bs4 import BeautifulSoup
import re

STORE_NAME = "96TP"

def quet_hoa_don_final():
    root_dir = 'D:\\CTY\\HoaDonXML\\' + STORE_NAME + '\\'  + '_XML_Data'
    output_file = 'D:\\CTY\\TenSanPham\\' + STORE_NAME + '\\' + 'HoaDonThue.xlsx'
    results = []

    if not os.path.exists(root_dir):
        print(f"Không tìm thấy thư mục {root_dir}")
        return

    # 1. Duyệt thư mục
    for sub_dir in os.listdir(root_dir):
        path_to_sub = os.path.join(root_dir, sub_dir)
        
        if os.path.isdir(path_to_sub):
            ma_so_match = re.search(r'\d+', sub_dir)
            ma_so = ma_so_match.group() if ma_so_match else ""

            file_path = os.path.join(path_to_sub, "invoice.html")

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "lxml")

                    rows = soup.find_all("tr")

                    for row in rows:
                        cells = row.find_all(["td", "th"])

                        if len(cells) >= 6:
                            stt = cells[0].get_text(strip=True)
                            ten_hang = cells[3].get_text(strip=True)

                            # 👉 bạn đã xác định index đúng → sửa tại đây nếu khác
                            don_gia = cells[6].get_text(strip=True)

                            if stt.isdigit() and ten_hang:
                                results.append({
                                    "Thư mục hiện hành": sub_dir,
                                    "Mã số": ma_so,
                                    "Tên hàng hóa, dịch vụ": ten_hang,
                                    "Đơn giá": don_gia
                                })

                except Exception as e:
                    print(f"Lỗi tại {sub_dir}: {e}")

    # 2. Xử lý pandas
    if results:
        df = pd.DataFrame(results)

        # Chuẩn hóa tên hàng
        df["Tên hàng hóa, dịch vụ"] = df["Tên hàng hóa, dịch vụ"].str.strip()

        # 👉 Deduplicate theo Tên + Đơn giá
        df_unique = df.drop_duplicates(
            subset=["Tên hàng hóa, dịch vụ", "Đơn giá"],
            keep='first'
        ).copy()

        # Sắp xếp A-Z
        df_sorted = df_unique.sort_values(
            by="Tên hàng hóa, dịch vụ",
            ascending=True
        )

        # 3. Xuất Excel
        df_final = df_sorted[
            ["Thư mục hiện hành", "Mã số", "Tên hàng hóa, dịch vụ", "Đơn giá"]
        ]

        df_final.to_excel(output_file, index=False)

        print(f"--- ĐÃ HOÀN TẤT ---")
        print(f"Tổng số dòng thô: {len(df)}")
        print(f"Số lượng hàng hóa duy nhất: {len(df_final)}")
        print(f"File xuất: {output_file}")

    else:
        print("Không tìm thấy dữ liệu.")


if __name__ == "__main__":
    quet_hoa_don_final()