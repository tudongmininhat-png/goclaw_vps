---
name: hop-dong
description: "Sử dụng khi khách hàng yêu cầu báo giá tủ lạnh Sanden hoặc soạn thảo Hợp Đồng. Skill này tự động tạo file Word và upload lên Google Drive."
allowed-tools: "Bash(*)"
packages:
  python:
    - google-api-python-client
    - google-auth-httplib2
    - google-auth-oauthlib
    - python-docx
    - docxtpl
metadata:
  author: Sanden Intercool
  version: "1.0"
---

# Hướng dẫn Kỹ năng soạn thảo Hợp đồng & Báo giá Sanden

Skill này giúp bạn tự động hóa việc tạo tài liệu (Word/PDF) và lưu trữ lên Google Drive.

## Quy trình Thực hiện (Dành cho Agent)

**Bước 1:** Trích xuất thông tin khách hàng
Hãy trích xuất: `ten_khach_hang`, `dia_chi`, `so_dien_thoai`, và `danh_sach_san_pham` (model, số lượng, đơn giá).
Lưu dữ liệu vào file tạm:
```bash
echo '<json_data_da_trich_xuat>' > /tmp/temp_data.json
```

**Bước 2:** Chạy Script tạo file Word (.docx)
Tìm thư mục chứa script và thực thi:
```bash
SCRIPTS_DIR=$(find . -name "convert-docs.py" -path "*hop-dong*" 2>/dev/null | head -1 | xargs dirname) && python3 $SCRIPTS_DIR/convert-docs.py /tmp/temp_data.json
```
> 👉 *Script này sẽ in ra đường dẫn file `.docx` vừa tạo.*

**Bước 3:** Tải lên Google Drive
Lấy đường dẫn file `.docx` từ output Bước 2 và chạy lệnh upload:
```bash
SCRIPTS_DIR=$(find . -name "gdrive_helper.py" -path "*hop-dong*" 2>/dev/null | head -1 | xargs dirname) && python3 $SCRIPTS_DIR/gdrive_helper.py <duong_dan_file_docx_buoc_2>
```

**Bước 4:** Trả kết quả cho khách
Script ở Bước 3 sẽ trả về link PDF. Hãy gửi link đó cho khách hàng.

---
*Lưu ý: Nếu gặp lỗi "Blocked by policy", hãy luôn sử dụng đường dẫn tương đối (bắt đầu bằng dấu chấm `.`) thay vì đường dẫn tuyệt đối.*
