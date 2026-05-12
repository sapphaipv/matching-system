import pandas as pd
import re
from thefuzz import process, fuzz

# Load 2 file của bạn
# sp = pd.read_csv('data_sp.csv')
# hd = pd.read_csv('data_hd.csv')

# Đọc trực tiếp các tab từ file Excel
file_name = f"data/raw/data.xlsx"
sp = pd.read_excel(file_name, sheet_name='SP')
hd = pd.read_excel(file_name, sheet_name='HD')

def get_weight(text):
    match = re.search(r'\d+\s?(g|kg|ml|l|gr)', str(text).lower())
    return match.group().replace(" ", "") if match else None

def find_match(name_hd, choices_sp):
    weight_hd = get_weight(name_hd)
    # Lọc danh mục SP có cùng trọng lượng
    potential_sp = [name for name in choices_sp if get_weight(name) == weight_hd]
    
    if not potential_sp: return None, 0
    
    # So khớp mờ trong danh sách đã lọc
    best_match, score = process.extractOne(name_hd, potential_sp, scorer=fuzz.token_set_ratio)
    return best_match, score

# Chạy so khớp
hd['Matched_SP'], hd['Score'] = zip(*hd['Tên hàng hóa, dịch vụ'].apply(lambda x: find_match(x, sp['Tên hàng'].tolist())))
hd.to_csv('ket_qua_cuoi_cung.csv', index=False)