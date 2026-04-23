---
name: hop-dong
description: "Sử dụng khi khách hàng yêu cầu báo giá tủ lạnh Sanden hoặc soạn thảo Hợp Đồng. Skill này tự động tạo file Word và upload lên Google Drive."
allowed-tools: "Bash(*)"
metadata:
  author: Sanden Intercool
  version: "1.0"
---

# Hướng dẫn sử dụng Skill Hợp Đồng Sanden

Skill này giúp Agent tự động soạn thảo Hợp đồng và Báo giá dựa trên thông tin khách hàng cung cấp.

### Quy trình:
1. Agent thu thập thông tin khách hàng (Tên, địa chỉ, sản phẩm...).
2. Agent gọi script `scripts/quotation_content.py` để tạo nội dung.
3. Agent gọi script `scripts/convert-docs.py` để tạo file Word và upload lên Google Drive.
4. Agent cung cấp link PDF cho người dùng.

### Lưu ý bảo mật:
- Mọi Key Google Drive được lưu tại `gdrive_secrets/` trên VPS.
- Không chia sẻ file `token.json` cho bên thứ ba.
