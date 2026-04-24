import os
import subprocess
import json
import sys
import shutil
import db_helper

# Đường dẫn tương đối
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def execute_full_cycle(payload):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_data_path = os.path.join(OUTPUT_DIR, f"temp_data_{os.getpid()}.json")
    
    # 1. Tạo file temp_data.json
    with open(temp_data_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    
    try:
        # 2. Chạy convert-docs.py để tạo file Docx và PDF
        subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "convert-docs.py"), temp_data_path], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        
        # 3. Tìm file .docx vừa tạo trong output/
        docx_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".docx")]
        if not docx_files:
            return {"error": "Không tìm thấy file .docx được tạo ra trong thư mục output"}
        
        # Lấy file có thời gian sửa đổi mới nhất
        latest_docx = max([os.path.join(OUTPUT_DIR, f) for f in docx_files], key=os.path.getmtime)

        # 4. Chạy gdrive_helper.py để upload
        upload_cmd = ["python3", os.path.join(SCRIPTS_DIR, "gdrive_helper.py"), latest_docx]
        result = subprocess.run(upload_cmd, cwd=BASE_DIR, capture_output=True, text=True)
        
        # 5. Lấy link PDF từ dòng cuối của output gdrive_helper
        pdf_link = result.stdout.strip().split("\n")[-1]
        
        # 6. Dọn dẹp thư mục output ngay lập tức để tiết kiệm ổ cứng
        if os.path.exists(OUTPUT_DIR):
            for filename in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Không thể xóa {file_path}: {e}")
        
        if pdf_link.startswith("http"):
            # Khởi tạo bảng (nếu chưa có) và lưu thông tin khách hàng vào Postgres
            db_helper.init_db()
            db_helper.upsert_customer(payload, payload.get("type", "quotation"))
            
            return {"success": True, "links": {"pdf": pdf_link}}
        else:
            return {"error": "Không lấy được link từ Google Drive", "logs": result.stdout}

    except subprocess.CalledProcessError as e:
        return {"error": f"Lỗi thực thi script: {e.stderr}"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Xóa temp_data.json
        if 'temp_data_path' in locals() and os.path.exists(temp_data_path):
            os.remove(temp_data_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Thiếu Payload JSON"}))
        sys.exit(1)
        
    try:
        payload = json.loads(sys.argv[1])
        print(json.dumps(execute_full_cycle(payload), ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
