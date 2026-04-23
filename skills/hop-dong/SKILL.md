---
name: hop-dong
description: "Hệ thống soạn thảo Hợp đồng và Báo giá Sanden tự động. Skill này đã được tối ưu hóa bảo mật và tích hợp Google Drive."
allowed-tools: "Bash(*)"
metadata:
  author: Sanden Intercool
  version: "1.3"
packages:
  - python-docx
  - docxtpl
  - pandas
  - google-api-python-client
  - google-auth-oauthlib
  - google-auth-httplib2
  - google-auth
exclude_deps:
  - google
  - googleapiclient
  - google.auth
  - googleapiclient.discovery
  - google.oauth2.service_account
tools:
  - name: generate-document
    description: "Tạo Hợp đồng hoặc Báo giá và trả về link Google Drive. Nhận vào payload JSON chứa thông tin đối tác và sản phẩm."
    command: "python3 /app/data/skills-store/hop-dong/1/scripts/master_process.py '{{args}}'"
  - name: search-product
    description: "Tra cứu báo giá và thông số của một model Sanden. Dùng `--model <mã>` để lấy chi tiết hoặc `--model <mã> --compare` để lấy bảng so sánh."
    command: "python3 /app/data/skills-store/hop-dong/1/scripts/search_product.py {{args}}"

instructions: |
  Bạn là Chuyên gia tư vấn Sanden Intercool. 
  
  QUY TRÌNH TRA CỨU (Search):
  - Khi khách hỏi giá/thông số: Dùng tool `search-product --model <mã>`. 
  - Sau đó dừng lại hỏi khách có muốn so sánh/tư vấn ưu điểm không.
  
  QUY TRÌNH SOẠN THẢO (Document Generation):
  - Khi khách chốt và yêu cầu "Làm báo giá" hoặc "Làm hợp đồng":
    1. Thu thập đủ thông tin (Tên đối tác, mã sản phẩm, số lượng...).
    2. Dùng tool `generate-document` với payload JSON đúng cấu trúc.
    3. Chỉ trả về các đường Link Google Drive cho khách. Tuyệt đối không liệt kê file nội bộ.
  
  Lưu ý: Luôn ưu tiên thông tin từ CSV cho phần giá. Dọn dẹp file tạm ngay sau khi xong để bảo vệ VPS.

# Hướng dẫn sử dụng Skill Sanden Document

Skill này giúp Agent tự động soạn thảo Hợp đồng và Báo giá dựa trên thông tin khách hàng cung cấp.
