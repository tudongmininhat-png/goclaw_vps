UPDATE skills SET frontmatter = '{
  "name": "hop-dong",
  "description": "Hệ thống soạn thảo Hợp đồng và Báo giá Sanden tự động. Skill này đã được tối ưu hóa bảo mật và cài sẵn thư viện.",
  "allowed-tools": "Bash(*)",
  "metadata": {
    "author": "Sanden Intercool",
    "version": "1.1"
  },
  "packages": [
    "python-docx",
    "docxtpl",
    "pandas",
    "google-api-python-client",
    "google-auth-oauthlib",
    "google-auth-httplib2"
  ],
  "tools": [
    {
      "name": "search-product",
      "description": "Tra cứu báo giá và thông số của một model Sanden. Dùng --model <mã> để lấy chi tiết hoặc --model <mã> --compare để lấy bảng so sánh.",
      "command": "python3 /app/data/skills-store/hop-dong/1/scripts/search_product.py {{args}}"
    }
  ],
  "instructions": "Bạn là Chuyên gia tư vấn Sanden Intercool. Khi khách hỏi về model hoặc tìm sản phẩm, hãy tuân thủ QUY TRÌNH 2 ĐỢT:\n\nĐỢT 1 (Báo cáo giá & Thông số):\n1. Dùng tool `search-product --model <mã>` để lấy bảng giá 3 tầng và thông số từ CSV.\n2. Tuyệt đối KHÔNG chào hỏi rườm rà. Trả về bảng giá ngay.\n3. Kết thúc bằng câu hỏi: \"Em đã báo cáo xong Giá & Thông số cơ bản của dòng [Tên Tủ]. Anh có muốn em liệt kê tiếp các Ưu Điểm Công Nghệ và Lập bảng so sánh với 2-3 tủ đối thủ cùng loại không?\"\n4. PHẢI DỪNG TRẢ LỜI TẠI ĐÂY.\n\nĐỢT 2 (Khi khách đồng ý/tiếp tục):\n1. Lấy Ưu điểm công nghệ từ kiến thức (knowledge) của bạn.\n2. Dùng tool `search-product --model <mã> --compare` để xuất bảng so sánh Markdown trực quan.\n\nLưu ý: Luôn ưu tiên thông tin từ Tool (CSV) cho phần giá và thông số kỹ thuật."
}' WHERE slug = 'hop-dong';

INSERT INTO skill_agent_grants (id, skill_id, agent_id, pinned_version, granted_by, tenant_id)
SELECT uuid_generate_v7(), '019dba97-3da7-7f2a-bccc-7ef5412495f6', '019d95a0-acad-70fa-96a2-eaedf17c75aa', 1, 'admin', '0193a5b0-7000-7000-8000-000000000001'
WHERE NOT EXISTS (
    SELECT 1 FROM skill_agent_grants WHERE skill_id = '019dba97-3da7-7f2a-bccc-7ef5412495f6' AND agent_id = '019d95a0-acad-70fa-96a2-eaedf17c75aa'
);
