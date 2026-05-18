import json
import requests
import websocket


def get_hddt_auth():

    tabs = requests.get(
        "http://127.0.0.1:9222/json"
    ).json()

    target = None

    for t in tabs:

        url = t.get("url", "")

        if "hoadondientu.gdt.gov.vn" in url:

            target = t
            break

    if not target:
        raise Exception(
            "Không tìm thấy tab HDDT"
        )

    ws = websocket.create_connection(
        target["webSocketDebuggerUrl"]
    )

    ws.send(json.dumps({
        "id": 1,
        "method": "Network.enable"
    }))
    ws.recv()

    ws.send(json.dumps({
        "id": 2,
        "method": "Network.getCookies"
    }))

    result = json.loads(ws.recv())

    ws.close()

    cookies = {}

    for c in result["result"]["cookies"]:
        cookies[c["name"]] = c["value"]

    # ===== JWT =====
    jwt_token = cookies.get("jwt")

    # ===== TS Cookie =====
    cookie_ts = None

    for k, v in cookies.items():

        if k.startswith("TS01"):

            cookie_ts = f"{k}={v}"
            break

    return jwt_token, cookie_ts, cookies


jwt_token, cookie_ts, cookies = get_hddt_auth()

print("=" * 80)

print("JWT_TOKEN:")
print(jwt_token)

print()

print("COOKIE_TS:")
print(cookie_ts)

print()

print("ALL COOKIES:")
for k, v in cookies.items():
    print(k, "=", v[:80])