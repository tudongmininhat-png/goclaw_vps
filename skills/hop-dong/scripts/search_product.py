import os
import csv
import re
import argparse
import sys

def normalize_model(model_code):
    if not model_code: return ""
    return re.sub(r"[^a-zA-Z0-9]", "", str(model_code)).lower()

def load_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Tìm CSV ở thư mục assets
    csv_path = os.path.join(base_dir, "..", "assets", "product_db.csv")
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)

def find_product(query, rows):
    q = normalize_model(query)
    # Tìm khớp hoàn toàn
    for row in rows:
        if q == normalize_model(row.get("Mã Model", "")):
            return row
    # Tìm khớp chứa
    for row in rows:
        m = normalize_model(row.get("Mã Model", ""))
        if q in m or m in q:
            return row
    return None

def format_detail_table(row):
    if not row: return "⚠️ Không tìm thấy model này trong database."
    
    model = row.get("Mã Model", "")
    name = row.get("Tên Model", "")
    cap = row.get("Dung tích (Lít)", "—")
    dims = row.get("Kích thước (w x D x H) (mm)", "—")
    p_vip = row.get("Giá hỗ trợ đại lý thân thiết (VAT 8%)", "—")
    p_dlr = row.get("Giá đại lý mới 2026 (VAT 8%)", "—")
    p_ret = row.get("Giá bán lẻ đề xuất (VAT 8%)", "—")

    return (
        f"📦 **{model}** — {name}\n\n"
        f"**Thông số cơ bản:**\n"
        f"| Thông số | Giá trị |\n"
        f"|:---|:---|\n"
        f"| Dung tích | {cap} Lít |\n"
        f"| Kích thước (RxSxC) | {dims} mm |\n\n"
        f"💰 **Bảng giá (đã bao gồm VAT 8%):**\n"
        f"| Mức giá | Đơn giá |\n"
        f"|:---|---:|\n"
        f"| 🥇 ĐL thân thiết | **{p_vip}** đ |\n"
        f"| 🏷️ ĐL mới 2026 | **{p_dlr}** đ |\n"
        f"| 🛒 Bán lẻ đề xuất | **{p_ret}** đ |"
    )

def find_similars(target, rows, n=3):
    if not target: return []
    target_name = target.get("Tên Model", "")
    target_model = target.get("Mã Model", "")
    
    similar = [
        r for r in rows
        if r.get("Tên Model", "") == target_name
        and r.get("Mã Model", "") != target_model
    ]
    
    # Sắp theo dung tích gần nhất
    try:
        t_cap = float(target.get("Dung tích (Lít)", 0) or 0)
        similar.sort(key=lambda r: abs(float(r.get("Dung tích (Lít)", 0) or 0) - t_cap))
    except:
        pass
    return similar[:n]

def format_comparison_table(target_model_code, rows):
    target = find_product(target_model_code, rows)
    similars = find_similars(target, rows)
    
    if not target and not similars:
        return "⚠️ Không có dữ liệu so sánh."
        
    all_rows = ([target] if target else []) + similars
    lines = [
        "**Bảng so sánh các model tương đồng:**",
        "| STT | Mã Model | Kích thước | Dung tích | Giá bán lẻ (VAT 8%) |",
        "|:---|:---|:---|---:|---:|",
    ]
    for i, r in enumerate(all_rows, 1):
        mark = " ⭐" if r.get("Mã Model") == (target or {}).get("Mã Model") else ""
        lines.append(
            f"| {i} | **{r.get('Mã Model','')}**{mark} "
            f"| {r.get('Kích thước (w x D x H) (mm)','')} "
            f"| {r.get('Dung tích (Lít)','')} Lít "
            f"| {r.get('Giá bán lẻ đề xuất (VAT 8%)','—')} đ |"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Mã model cần tìm")
    parser.add_argument("--compare", action="store_true", help="Yêu cầu xuất bảng so sánh")
    args = parser.parse_args()
    
    data = load_db()
    if not args.model:
        print("Lỗi: Thiếu tham số --model")
        sys.exit(1)
        
    if args.compare:
        print(format_comparison_table(args.model, data))
    else:
        print(format_detail_table(find_product(args.model, data)))
