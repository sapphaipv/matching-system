import pandas as pd
import os

# 1. Cấu hình đường dẫn

store_name = "96TP"
input_dir = r"D:\CTY\TenSanPham\\" + store_name

file_input = os.path.join(input_dir, "HoaDonThue.xlsx")
file_services = os.path.join(input_dir, "HD_Services.xlsx")
file_products = os.path.join(input_dir, "HD_Products.xlsx")

def split_services_and_products():
    try:
        if not os.path.exists(file_input):
            print(f"Lỗi: Không tìm thấy file {file_input}")
            return

        df = pd.read_excel(file_input)

        # 2. Định nghĩa bộ lọc
        # Danh sách gây nghi vấn dịch vụ
        service_keywords = [
            'dịch vụ', 'phí', 'chiết khấu', 'khuyến mãi', 'tặng kèm', 
            'lắp đặt', 'vận chuyển', 'thuê', 'sửa chữa', 'bảo dưỡng',
            'công nợ', 'hỗ trợ', 'quà tặng', 'không thu tiền', '(km)', 'hàng km', 'km'
        ]
        
        # Danh sách bảo vệ hàng hóa (để không bị lọc nhầm như KuFon, Sungaz)
        rescue_keywords = ['sản phẩm']

        names_lower = df['Tên hàng hóa, dịch vụ'].astype(str).str.lower()

        # 3. Tạo Logic lọc
        pattern_service = '|'.join(service_keywords)
        is_service_suspect = names_lower.str.contains(pattern_service, na=False)

        pattern_rescue = '|'.join(rescue_keywords)
        is_actually_product = names_lower.str.contains(pattern_rescue, na=False)

        # Điều kiện xác định Dịch vụ: Nghi vấn dịch vụ VÀ KHÔNG phải hàng hóa cứu vớt
        is_service_final = is_service_suspect & ~is_actually_product

        # 4. Tách dữ liệu
        df_services = df[is_service_final].copy()
        df_products = df[~is_service_final].copy() # Dấu ~ lấy các dòng NGƯỢC LẠI hoàn toàn với dịch vụ

        # 5. Xuất file
        df_services.to_excel(file_services, index=False)
        df_products.to_excel(file_products, index=False)

        print("-" * 30)
        print(f"Tổng cộng hóa đơn: {len(df)} dòng.")
        print(f"--> Đã tách {len(df_services)} dòng vào: {os.path.basename(file_services)}")
        print(f"--> Đã tách {len(df_products)} dòng vào: {os.path.basename(file_products)}")
        print("-" * 30)

    except Exception as e:
        print(f"Có lỗi phát sinh: {e}")

if __name__ == "__main__":
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    split_services_and_products()