import asyncio
import aiohttp
import os
import browser_cookie3
from datetime import datetime

# ================= CONFIG =================
FOLDER_PREFIX = r"D:\Cty\HoaDonXML"
STORE_NAME = "12NTMK"
FROM_DATE = "01/04/2026"
TO_DATE   = "01/04/2026"
JWT_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI0MjAyMDQzMzk1IiwidHlwZSI6MiwiZXhwIjoxNzc3MDgyOTQ1LCJpYXQiOjE3NzY5OTY1NDV9.eOjy77xXX7LCOWdTnJcO67aaGVnU8Hsv_46vk9r3X-FBhUFLabqLZhx4TNln29n_A5G5mJZFjRCAFyMpAbr6zA"

CONCURRENCY = 5
TIMEOUT = 20

folder_suffix = datetime.strptime(FROM_DATE, "%d/%m/%Y").strftime("%Y-%m")
SAVE_FOLDER = rf"{FOLDER_PREFIX}\{STORE_NAME}\HDDT-Out-{folder_suffix}"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# ================= LOAD COOKIE FROM CHROME =================
def load_cookie():
    cj = browser_cookie3.chrome(domain_name="hoadondientu.gdt.gov.vn")

    cookies = []
    for c in cj:
        cookies.append(f"{c.name}={c.value}")

    return "; ".join(cookies)

COOKIE = load_cookie()

BASE_HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://hoadondientu.gdt.gov.vn/",
    "Origin": "https://hoadondientu.gdt.gov.vn"
}

# ================= FETCH =================
async def fetch_all(session):
    url = "https://hoadondientu.gdt.gov.vn:30000/sco-query/invoices/sold"

    all_inv = []
    seen = set()
    state = None

    while True:
        params = {
            "sort": "tdlap:desc",
            "size": 15,
            "search": f"tdlap=ge={FROM_DATE}T00:00:00;tdlap=le={TO_DATE}T23:59:59"
        }
        if state:
            params["state"] = state

        async with session.get(
            url,
            params=params,
            headers={**BASE_HEADERS, "Action": "tim-kiem"},
            timeout=aiohttp.ClientTimeout(total=TIMEOUT)
        ) as r:

            if r.status != 200:
                print("Fetch lỗi:", r.status)
                break

            data = await r.json()

        invs = data.get("datas", [])
        new_state = data.get("state")

        if not invs:
            break

        prev = len(seen)

        for inv in invs:
            if inv["id"] not in seen:
                seen.add(inv["id"])
                all_inv.append(inv)

        print("Fetched:", len(seen))

        if not new_state or new_state == state:
            break
        if len(seen) == prev:
            break

        state = new_state
        await asyncio.sleep(1)

    return all_inv

# ================= DOWNLOAD =================
async def download_one(session, sem, inv):
    url = "https://hoadondientu.gdt.gov.vn:30000/query/invoices/export-xml"

    filename = f'{inv["nbmst"]}_{inv["khhdon"]}_{inv["shdon"]}.zip'
    path = os.path.join(SAVE_FOLDER, filename)

    if os.path.exists(path) and os.path.getsize(path) > 500:
        return "skip", filename

    params = {
        "id": inv["id"],
        "nbmst": inv["nbmst"],
        "khhdon": inv["khhdon"],
        "shdon": inv["shdon"],
        "khmshdon": inv["khmshdon"]
    }

    async with sem:
        try:
            async with session.get(
                url,
                params=params,
                headers={
                    **BASE_HEADERS,
                    "Action": "Xu%E1%BA%A5t%20xml"
                },
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as r:

                ct = r.headers.get("Content-Type", "")

                if r.status == 200 and ("zip" in ct or "octet-stream" in ct):
                    content = await r.read()
                    with open(path, "wb") as f:
                        f.write(content)
                    return "ok", filename
                else:
                    return "fail", filename

        except asyncio.TimeoutError:
            return "timeout", filename

# ================= RUN =================
async def main():
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        print("🔄 Fetching...")
        all_inv = await fetch_all(session)

        print("Tổng hóa đơn:", len(all_inv))

        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = [download_one(session, sem, inv) for inv in all_inv]

        ok = 0

        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            status, name = await coro
            print(f"[{i}/{len(all_inv)}]", status.upper(), name)

            if status == "ok":
                ok += 1

        print(f"\n✅ DONE {ok}/{len(all_inv)}")

if __name__ == "__main__":
    asyncio.run(main())