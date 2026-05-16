# Tự động download HÓA ĐƠN ĐIỆN TỬ từ web THUẾ
# ============================================
import sys
import requests
import cloudscraper
import os
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import socket
# import requests.packages.urllib3.util.connection as urllib3_cn
import urllib3.util.connection as urllib3_cn

# =========================
# COMMAND ARGUMENT
# =========================

if len(sys.argv) < 2:

    print("Usage:")
    print("  python download.py /i")
    print("  python download.py /o")
    sys.exit()

arg = sys.argv[1].lower()

if arg in ["/i", "i", "in", "purchase"]:
    INVOICE_TYPE = "purchase"

elif arg in ["/o", "o", "out", "sale", "sold"]:
    INVOICE_TYPE = "sold"

else:
    print("Invalid argument!")
    print("Use /i or /o")
    sys.exit()

print(f"MODE = {INVOICE_TYPE.upper()}")

def force_ipv4():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = force_ipv4

def setup_invoice_mode(invoice_type):

    invoice_type = invoice_type.lower()

    if invoice_type in ["purchase", "in"]:
        return {
            "INV_TYPE": "purchase",
            "BASE_API": "query",
            "INV_FOLDER": "In"
        }

    elif invoice_type in ["sale", "sold", "out"]:
        return {
            "INV_TYPE": "sold",
            "BASE_API": "sco-query",
            "INV_FOLDER": "Out"
        }

    else:
        raise ValueError("INVOICE_TYPE không hợp lệ")
    
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
# INVOICE_TYPE = cfg["INVOICE_TYPE"]

# ================= CONFIG =================

mode = setup_invoice_mode(INVOICE_TYPE)

INV_TYPE = mode["INV_TYPE"]
BASE_API = mode["BASE_API"]
INV_FOLDER = mode["INV_FOLDER"]

FOLDER_SUFF = datetime.strptime(FROM_DATE, "%d/%m/%Y").strftime("%Y-%m")
SAVE_FOLDER = rf"{FOLDER_PREFIX}\{STORE_NAME}\HDDT-{INV_FOLDER}-{FOLDER_SUFF}"

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

    # s = requests.Session()
    s = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )

    invoice_type = INVOICE_TYPE.lower()

    # ================= PURCHASE =================
    if invoice_type in ["purchase", "in"]:
        s.headers.update({
            "Authorization": f"Bearer {JWT_TOKEN}",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://hoadondientu.gdt.gov.vn/",
        })

    # ================= SOLD / MÁY TÍNH TIỀN =================
    elif invoice_type in ["sale", "sold", "out"]:
        s.headers.update({
            "Authorization": f"Bearer {JWT_TOKEN}",

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",

            "Referer": "https://hoadondientu.gdt.gov.vn/",
            "Origin": "https://hoadondientu.gdt.gov.vn",

            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi",
            "Connection": "keep-alive",

            "End-Point": "/tra-cuu/tra-cuu-hoa-don",
            "Action": "TR%C3%ACm%20ki%E1%BA%BFm%20(h%C3%B3a%20C4%91%C6%A1n%20m%C3%A1y%20t%C3%ADnh)"
        })

        # QUAN TRỌNG
        s.headers["Cookie"] = f"jwt={JWT_TOKEN}; TS01c977ee={COOKIE_TS}"

    else:
        raise ValueError("INVOICE_TYPE không hợp lệ")

    # Cookie session
    s.cookies.set("jwt", JWT_TOKEN)
    s.cookies.set("TS01c977ee", COOKIE_TS)

    return s


def validate_token():

    try:

        url = f"https://hoadondientu.gdt.gov.vn/api/{BASE_API}/invoices/{INV_TYPE}"

        params = {
            "sort": "tdlap:desc",
            "size": 1,
        }

        r = session.get(
            url,
            params=params,
            timeout=(10, 30)
        )

        print("VALIDATE:", r.status_code)

        # chỉ coi là token chết khi 401/403
        if r.status_code in [401, 403]:
            return False

        # server lỗi -> bỏ qua
        if r.status_code >= 500:
            print("VALIDATE SERVER ERROR -> bỏ qua")
            return True

        ctype = r.headers.get("Content-Type", "")

        # đôi lúc HDDT trả HTML lỗi nginx/cloudflare
        if "text/html" in ctype:
            print("VALIDATE HTML RESPONSE -> bỏ qua")
            return True

        try:
            data = r.json()
            return isinstance(data, dict)

        except:
            print("VALIDATE JSON ERROR -> bỏ qua")
            return True

    except requests.exceptions.ReadTimeout:
        print("VALIDATE TIMEOUT -> bỏ qua")
        return True

    except requests.exceptions.ConnectionError:
        print("VALIDATE CONNECTION ERROR -> bỏ qua")
        return True

    except Exception as e:
        print("VALIDATE ERROR:", e)
        return True
    
def refresh_token():

    log("⚠️ TOKEN EXPIRED → cập nhật config.txt rồi ENTER để chạy tiếp...")
    input()

    global session
    global JWT_TOKEN, COOKIE_TS
    # global BASE_API, INV_TYPE, INV_FOLDER

    cfg_new = load_config()

    JWT_TOKEN = cfg_new["JWT_TOKEN"]
    COOKIE_TS = cfg_new["COOKIE_TS"]

    # INVOICE_TYPE = cfg_new["INVOICE_TYPE"]
    # mode = setup_invoice_mode(INVOICE_TYPE)

    # INV_TYPE = mode["INV_TYPE"]
    # BASE_API = mode["BASE_API"]
    # INV_FOLDER = mode["INV_FOLDER"]

    session = create_session()

    log("✅ TOKEN UPDATED")

session = create_session()

if not validate_token():
    log("⚠️ TOKEN INVALID/EXPIRED")
    refresh_token()


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


# ================= FETCH =================
def fetch_all():

    # url = f"https://hoadondientu.gdt.gov.vn:30000/{BASE_API}/invoices/{INV_TYPE}" 
    url = f"https://hoadondientu.gdt.gov.vn/api/{BASE_API}/invoices/{INV_TYPE}"

    all_inv = []
    seen = set()
    state = None

    while True:

        if INVOICE_TYPE.lower() in ["purchase", "in"]: 
            # url = (
            #     f"https://hoadondientu.gdt.gov.vn:30000/"  y
            #     f"{BASE_API}/invoices/{INV_TYPE}"
            # )

            params = {
                "sort": "tdlap:desc",
                "size": 50,
                "search": f"tdlap=ge={FROM_DATE}T00:00:00;tdlap=le={TO_DATE}T23:59:59;ttxly==5"
            }
        else:
            # url = (
            #     f"https://hoadondientu.gdt.gov.vn/api/"
            #     f"{BASE_API}/invoices/{INV_TYPE}"
            # )

            params = {
                "sort": "tdlap:desc",
                "size": 5,
                "search": f"tdlap=ge={FROM_DATE}T00:00:00;tdlap=le={TO_DATE}T23:59:59"
            }

        if state:
            params["state"] = state

        # print(url)
        # print(params)
        # print(session.headers)

        # r = session.get(url, params=params, timeout=20)

        success = False

        for attempt in range(5):
            try:
                r = session.get(
                    url,
                    params=params,
                    timeout=(10, 180)
                )

                print("FETCH STATUS:", r.status_code)

                if is_token_expired(r):
                    refresh_token()
                    continue

                if r.status_code == 200:

                    try:
                        data = r.json()
                        success = True
                        break

                    except Exception as e:
                        log(f"[JSON ERROR] {e}")

                else:
                    log(f"[FETCH ERROR] status={r.status_code}")

            except Exception as e:

                log(f"[FETCH RETRY {attempt+1}] {e}")

            time.sleep(5)

        if not success:

            log("[SKIP PAGE]")
            continue

        invs = data.get("datas", [])

        # print(r.text[:1000])

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

    url = (
        # f"https://hoadondientu.gdt.gov.vn:30000/"
        f"https://hoadondientu.gdt.gov.vn/api/"
        f"{BASE_API}/invoices/export-xml"
    )

    filename = (
        f'{inv["nbmst"]}_'
        f'{inv["khhdon"]}_'
        f'{inv["shdon"]}.zip'
    )

    path = os.path.join(SAVE_FOLDER, filename)

    # Đã tồn tại thì bỏ qua
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

            # ================= HEADER riêng cho HĐ MTT =================
            if INVOICE_TYPE.lower() in ["sale", "sold"]:

                session.headers["Action"] = (
                    "Xu%E1%BA%A5t%20xml"
                )

            r = session.get(
                url,
                params=params,
                timeout=30
            )

            # ================= RESET HEADER =================
            if INVOICE_TYPE.lower() in ["sale", "sold"]:

                session.headers["Action"] = (
                    "TR%C3%ACm%20ki%E1%BA%BFm%20"
                    "(h%C3%B3a%20C4%91%C6%A1n%20"
                    "m%C3%A1y%20t%C3%ADnh)"
                )

            # ================= TOKEN EXPIRED =================
            if is_token_expired(r):
                refresh_token()
                continue

            # ================= RATE LIMIT =================
            if r.status_code == 429:
                time.sleep(5)
                continue

            # ================= DOWNLOAD OK =================
            if (
                r.status_code == 200
                and len(r.content) > 1000
            ):

                with open(path, "wb") as f:
                    f.write(r.content)

                return "ok", filename

        except Exception as e:

            log(f"[ERROR] {filename} | {e}")

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