"""
gdrive_helper.py — Upload DOCX lên Google Drive dùng OAuth2 user credentials.
File tính vào quota Drive cá nhân của người dùng (không phải Service Account).
"""
import io
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

base_dir = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_TOKEN_PATHS = [
    os.getenv("GDRIVE_TOKEN_PATH", ""),
    "/app/data/gdrive_auth/token.json",
    os.path.join(base_dir, "..", "assets", "token.json")
]

TOKEN_PATH = None
for path in POSSIBLE_TOKEN_PATHS:
    if path and os.path.exists(path):
        TOKEN_PATH = path
        break
if not TOKEN_PATH: # Fallback to default asset path if not found
    TOKEN_PATH = os.path.join(base_dir, "..", "assets", "token.json")

FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", "")


def _get_credentials() -> Credentials:
    """Load + refresh OAuth2 credentials từ token.json"""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(
            f"Không tìm thấy token: {TOKEN_PATH}\n"
            "Hãy chạy: python3 setup_gdrive_auth.py"
        )

    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[GDrive] Token hết hạn, đang refresh...")
            creds.refresh(Request())
            # Lưu lại token mới
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            print("[GDrive] Token đã được refresh và lưu lại.")
        else:
            raise RuntimeError(
                "Token không còn hợp lệ và không có refresh_token.\n"
                "Hãy chạy lại: python3 setup_gdrive_auth.py"
            )

    return creds


def _get_service():
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _set_public(service, file_id: str) -> None:
    """Cho phép anyone có link xem file"""
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()


def upload_docx_and_get_links(docx_path: str) -> dict:
    """
    Upload DOCX → Google Doc (convert) + PDF riêng.
    Cả 2 file đều public link, owner là tài khoản Google của người dùng.

    Returns:
        {
            "success": True,
            "google_doc_link": "https://docs.google.com/document/d/.../view",
            "pdf_link":        "https://drive.google.com/file/d/.../view",
        }
        hoặc {"success": False, "error": "..."}
    """
    if not FOLDER_ID:
        return {"success": False, "error": "GDRIVE_FOLDER_ID chưa cấu hình trong .env"}
    if not os.path.exists(docx_path):
        return {"success": False, "error": f"Không tìm thấy DOCX: {docx_path}"}

    try:
        service = _get_service()
        filename = os.path.splitext(os.path.basename(docx_path))[0]

        # ── Bước 1: Upload DOCX → convert thành Google Doc ─────────────────
        print(f"[GDrive] Upload: {filename} ...")
        doc_metadata = {
            "name": filename,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [FOLDER_ID],
        }
        media = MediaFileUpload(
            docx_path,
            mimetype=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
            resumable=False,
        )
        doc_file = service.files().create(
            body=doc_metadata,
            media_body=media,
            fields="id",
        ).execute()
        doc_id = doc_file["id"]
        print(f"[GDrive] Google Doc ID: {doc_id}")

        # ── Bước 2: Set public link cho Google Doc ──────────────────────────
        _set_public(service, doc_id)

        # ── Bước 3: Export Google Doc → PDF bytes ───────────────────────────
        print("[GDrive] Exporting PDF ...")
        req = service.files().export_media(
            fileId=doc_id,
            mimeType="application/pdf",
        )
        pdf_buf = io.BytesIO()
        downloader = MediaIoBaseDownload(pdf_buf, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        pdf_bytes = pdf_buf.getvalue()
        print(f"[GDrive] PDF size: {len(pdf_bytes):,} bytes")

        # ── Bước 4: Upload PDF lên cùng folder ─────────────────────────────
        pdf_metadata = {
            "name": filename + ".pdf",
            "mimeType": "application/pdf",
            "parents": [FOLDER_ID],
        }
        pdf_media = MediaIoBaseUpload(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            resumable=False,
        )
        pdf_file = service.files().create(
            body=pdf_metadata,
            media_body=pdf_media,
            fields="id",
        ).execute()
        pdf_id = pdf_file["id"]
        print(f"[GDrive] PDF ID: {pdf_id}")

        # ── Bước 5: Set public link cho PDF ────────────────────────────────
        _set_public(service, pdf_id)

        google_doc_link = f"https://docs.google.com/document/d/{doc_id}/view"
        pdf_link = f"https://drive.google.com/file/d/{pdf_id}/view"

        print(f"[GDrive] ✅ Xong!")
        print(f"[GDrive]   Doc : {google_doc_link}")
        print(f"[GDrive]   PDF : {pdf_link}")

        return {
            "success": True,
            "google_doc_link": google_doc_link,
            "pdf_link": pdf_link,
        }

    except Exception as e:
        print(f"[GDrive] ❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 gdrive_helper.py <path_to_docx>")
        sys.exit(1)
    result = upload_docx_and_get_links(sys.argv[1])
    if not result.get("success"):
        sys.exit(1)
    sys.exit(0)
