import os
from urllib.parse import urlparse
from datetime import datetime
import pg8000

def get_connection():
    dsn = os.environ.get("GOCLAW_POSTGRES_DSN")
    if not dsn:
        print("[DB] Lỗi: Không tìm thấy GOCLAW_POSTGRES_DSN trong môi trường.")
        return None
        
    parsed = urlparse(dsn)
    
    try:
        conn = pg8000.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/')
        )
        # Enable autocommit for simpler script interactions
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"[DB] Lỗi kết nối CSDL: {e}")
        return None

def init_db():
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS quan_ly_khach_hang (
            id SERIAL PRIMARY KEY,
            ten_doi_tac VARCHAR(255) UNIQUE NOT NULL,
            dia_chi TEXT,
            nguoi_dai_dien VARCHAR(255),
            chuc_vu VARCHAR(100),
            sdt VARCHAR(50),
            mst VARCHAR(50),
            stk VARCHAR(100),
            trang_thai VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(query)
        print("[DB] Đã khởi tạo bảng quan_ly_khach_hang thành công.")
        return True
    except Exception as e:
        print(f"[DB] Lỗi khởi tạo bảng: {e}")
        return False
    finally:
        conn.close()

def upsert_customer(data, doc_type):
    # doc_type comes from payload type: "contract" or "quotation"
    trang_thai = "Hợp đồng" if doc_type == "contract" else "Báo giá"
    ten_doi_tac = data.get("TEN_DOI_TAC", "").strip()
    if not ten_doi_tac:
        return False

    conn = get_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        # Kiểm tra xem khách hàng đã tồn tại chưa
        cursor.execute("SELECT id, trang_thai FROM quan_ly_khach_hang WHERE ten_doi_tac = %s", (ten_doi_tac,))
        row = cursor.fetchone()
        
        current_time = datetime.now()
        
        if not row:
            # Tạo mới
            insert_query = """
                INSERT INTO quan_ly_khach_hang (
                    ten_doi_tac, dia_chi, nguoi_dai_dien, chuc_vu, sdt, mst, stk, trang_thai, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(insert_query, (
                ten_doi_tac,
                data.get('dia_chi', ''),
                data.get('NGUOI_DAI_DIEN', ''),
                data.get('chuc_vu', ''),
                data.get('sdt', ''),
                data.get('mst', ''),
                data.get('stk', ''),
                trang_thai,
                current_time,
                current_time
            ))
            print(f"[DB] Đã lưu thông tin khách hàng mới: {ten_doi_tac} (Trạng thái: {trang_thai})")
        else:
            # Cập nhật thông tin cũ (với hàm NULLIF để bỏ qua chuỗi rỗng)
            row_id = row[0]
            old_trang_thai = row[1]
            
            # Quy tắc chống hạ cấp trạng thái
            if old_trang_thai == "Hợp đồng" and trang_thai == "Báo giá":
                final_trang_thai = "Hợp đồng"
            else:
                final_trang_thai = trang_thai
                
            update_query = """
                UPDATE quan_ly_khach_hang
                SET dia_chi = COALESCE(NULLIF(%s, ''), dia_chi),
                    nguoi_dai_dien = COALESCE(NULLIF(%s, ''), nguoi_dai_dien),
                    chuc_vu = COALESCE(NULLIF(%s, ''), chuc_vu),
                    sdt = COALESCE(NULLIF(%s, ''), sdt),
                    mst = COALESCE(NULLIF(%s, ''), mst),
                    stk = COALESCE(NULLIF(%s, ''), stk),
                    trang_thai = %s,
                    updated_at = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (
                data.get('dia_chi', ''),
                data.get('NGUOI_DAI_DIEN', ''),
                data.get('chuc_vu', ''),
                data.get('sdt', ''),
                data.get('mst', ''),
                data.get('stk', ''),
                final_trang_thai,
                current_time,
                row_id
            ))
            print(f"[DB] Đã cập nhật khách hàng: {ten_doi_tac} (Trạng thái mới: {final_trang_thai})")
            
        return True
    except Exception as e:
        print(f"[DB] Lỗi upsert bảng quan_ly_khach_hang: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
