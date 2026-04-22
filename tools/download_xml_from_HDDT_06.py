# Tự động download HÓA ĐƠN ĐIỆN TỬ từ web THUẾ
# ============================================
import requests
import os
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= LOAD CONFIG =================
def load_config(file_path=r"tools\config.txt"):
    config = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip()

    required = ["FOLDER_PREFIX", "STORE_NAME", "FROM_DATE", "TO_DATE", "JWT_TOKEN", "COOKIE_TS"]
    for k in required:
        if k not in config:
            raise ValueError(f"Thiếu config: {k}")

    config["MAX_WORKERS"] = int(config.get("MAX_WORKERS", 5))

    return config


cfg = load_config()

FOLDER_PREFIX = cfg["FOLDER_PREFIX"]
STORE_NAME = cfg["STORE_NAME"]
FROM_DATE = cfg["FROM_DATE"]
TO_DATE   = cfg["TO_DATE"]
JWT_TOKEN = cfg["JWT_TOKEN"]
COOKIE_TS = cfg["COOKIE_TS"]
MAX_WORKERS = cfg["MAX_WORKERS"]
INVOICE_TYPE = cfg["INVOICE_TYPE"]

# ================= CONFIG =================
folder_suffix = datetime.strptime(FROM_DATE, "%d/%m/%Y").strftime("%Y-%m")
SAVE_FOLDER = rf"{FOLDER_PREFIX}\{STORE_NAME}\HDDT-In-{folder_suffix}"

LOG_FILE = "log.txt"

os.makedirs(SAVE_FOLDER, exist_ok=True)

# ================= LOGGER =================
lock = threading.Lock()

def log(msg):
    with lock:
        print(msg)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

# ================= SESSION =================
def create_session():
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {JWT_TOKEN}",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://hoadondientu.gdt.gov.vn/",
    })
    s.cookies.set("jwt", JWT_TOKEN)
    s.cookies.set("TS01c977ee", COOKIE_TS)
    return s

# def create_session():
#     s = requests.Session()
#     s.headers.update({
#         "Authorization": f"Bearer {JWT_TOKEN}",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#         "Referer": "https://hoadondientu.gdt.gov.vn/",
#         "Origin": "https://hoadondientu.gdt.gov.vn",
#         "Accept": "application/json, text/plain, */*",
#         "Accept-Language": "vi",
#         "Connection": "keep-alive",

#         # 🔥 QUAN TRỌNG
#         "Action": "tim-kiem",

#         # Cookie giữ nguyên như bạn đã có
#         "Cookie": f"jwt={JWT_TOKEN}; TS01c977ee={COOKIE_TS}"
#     })
#     return s

session = create_session()

# ================= TOKEN CHECK =================
def is_token_expired(resp):
    if resp.status_code == 401:
        return True
    try:
        data = resp.json()
        if "error" in data:
            return True
    except:
        pass
    return False


def refresh_token():
    log("⚠️ TOKEN EXPIRED → cập nhật config.txt rồi ENTER để chạy tiếp...")
    input()
    global session, JWT_TOKEN, COOKIE_TS

    cfg_new = load_config()
    JWT_TOKEN = cfg_new["JWT_TOKEN"]
    COOKIE_TS = cfg_new["COOKIE_TS"]

    session = create_session()
    log("✅ TOKEN UPDATED")


# ================= FETCH =================
def fetch_all():
    url = f"https://hoadondientu.gdt.gov.vn:30000/query/invoices/{INVOICE_TYPE}"

    all_inv = []
    seen = set()
    state = None

    while True:
        params = {
            "sort": "tdlap:desc",
            "size": 50,
            "search": f"tdlap=ge={FROM_DATE}T00:00:00;tdlap=le={TO_DATE}T23:59:59;ttxly==5"
        }

        if state:
            params["state"] = state

        r = session.get(url, params=params, timeout=20)

        if is_token_expired(r):
            refresh_token()
            continue

        if r.status_code != 200:
            log("[STOP] fetch lỗi")
            break

        data = r.json()
        invs = data.get("datas", [])
        new_state = data.get("state")

        if not invs:
            break

        for inv in invs:
            if inv["id"] not in seen:
                seen.add(inv["id"])
                all_inv.append(inv)

        if not new_state or new_state == state:
            break

        state = new_state
        time.sleep(0.5)

    return all_inv


# ================= DOWNLOAD =================
def download_invoice(inv):
    url = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/export-xml"

    filename = f'{inv["nbmst"]}_{inv["khhdon"]}_{inv["shdon"]}.zip'
    path = os.path.join(SAVE_FOLDER, filename)

    if os.path.exists(path):
        return "skip", filename

    params = {
        "nbmst": inv["nbmst"],
        "khhdon": inv["khhdon"],
        "shdon": inv["shdon"],
        "khmshdon": inv["khmshdon"]
    }

    for _ in range(3):
        try:
            r = session.get(url, params=params, timeout=30)

            if is_token_expired(r):
                refresh_token()
                continue

            if r.status_code == 429:
                time.sleep(5)
                continue

            if r.status_code == 200 and len(r.content) > 1000:
                with open(path, "wb") as f:
                    f.write(r.content)
                return "ok", filename

        except:
            pass

        time.sleep(random.uniform(1, 2))

    return "fail", filename


# ================= RUN =================
def run():
    all_inv = fetch_all()
    log(f"Tổng hóa đơn: {len(all_inv)}")

    while True:
        tasks = [inv for inv in all_inv if not os.path.exists(
            os.path.join(SAVE_FOLDER, f'{inv["nbmst"]}_{inv["khhdon"]}_{inv["shdon"]}.zip')
        )]

        if not tasks:
            log("🎯 DONE 100%")
            break

        log(f"Cần tải: {len(tasks)} | Threads: {MAX_WORKERS}")

        success = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(download_invoice, inv) for inv in tasks]

            for future in as_completed(futures):
                result, filename = future.result()

                if result == "ok":
                    log(f"[OK] {filename}")
                    success += 1
                elif result == "fail":
                    log(f"[FAIL] {filename}")
                # skip thì im

        if success == 0:
            log("⚠️ Không tiến triển → dừng")
            break


if __name__ == "__main__":
    run()