import subprocess
import re

def run(cmd):
    return subprocess.check_output(cmd, shell=True).decode().strip()

# Lấy tag mới nhất
try:
    latest_tag = run("git describe --tags --abbrev=0")
except:
    latest_tag = "v0.0.0"

match = re.match(r"v(\d+)\.(\d+)\.(\d+)", latest_tag)
major, minor, patch = map(int, match.groups())

# Lấy commit message gần nhất
msg = run("git log -1 --pretty=%B").lower()

# Quy tắc tăng version
if "break" in msg:
    major += 1
    minor = 0
    patch = 0
elif "feat" in msg:
    minor += 1
    patch = 0
elif "fix" in msg:
    patch += 1
else:
    print("❌ Không xác định loại commit (feat/fix/break)")
    exit()

new_version = f"v{major}.{minor}.{patch}"

print(f"🚀 New version: {new_version}")

# Tạo tag + push
run(f"git tag {new_version}")
run(f"git push origin {new_version}")

print("✅ Done!")