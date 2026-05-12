🚀 Workflow chuẩn (giữ nguyên dùng lâu dài)
git add .
git commit -m "v1.x.y: mô tả thay đổi"
git tag -a v1.x.y -m "v1.x.y"
git push origin main
git push origin v1.x.y

👉 Đây là baseline workflow — dùng được cho hầu hết project.

Nếu chỉ update tài liệu:

git add README.md
git commit -m "docs: update README"
git push origin main

👉 Thế là đủ. KHÔNG cần tạo tag mới.