import json
import os
from html import escape


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "assets", "config.json")
    
    # Fallback mặc định nếu không có file config
    defaults = {
        "company": {
            "name": "CÔNG TY TNHH SANDEN INTERCOOL VIỆT NAM",
            "office": "Văn phòng HCM / HCM Office: Tầng 5 - Tòa nhà Nam Việt - Số 261 Hoàng Văn Thụ - Phường Tân Sơn Hòa, Tp.HCM",
            "phone": "Điện thoại / Phone: 028-6276-6012",
            "tax_code": "Mã số thuế / Tax code: 0313167222"
        },
        "quotation": {
            "title": "BẢNG BÁO GIÁ",
            "intro": (
                "Lời đầu tiên, Công Ty TNHH Sanden Intercool (Việt Nam) xin gửi đến Quý khách hàng "
                "lời chào trân trọng và lời cảm ơn chân thành vì sự quan tâm sản phẩm của chúng tôi. "
                "Chúng tôi xin trân trọng báo giá sản phẩm quý khách quan tâm như sau:"
            ),
            "notes_title": "LƯU Ý:",
            "notes": [
                "Hàng mới 100%",
                "Giá trên đã bao gồm VAT 10%",
                "Phương thức giao hàng: Giá trên đã bao gồm phí vận chuyển giao tận nơi tại {{dia_chi}} hoặc địa điểm theo thỏa thuận mà không phát sinh chi phí.",
                "Thời gian nhận hàng: 1 - 3 ngày kể từ khi nhận được thanh toán",
                "Báo giá có hiệu lực: trong 07 ngày kể từ ngày báo giá.",
                "Phương thức thanh toán: Thanh toán bằng hình thức chuyển khoản. Thanh toán trước 100% giá trị đơn hàng khi xác nhận đơn hàng.",
                "Thời gian bảo hành:",
                "Bảo hành 24 tháng theo chính sách Bảo hành chính hãng tính từ khi ký Biên bản Bàn giao - Nghiệm thu."
            ],
            "closing": "Trân trọng !",
            "signature_left": "XÁC NHẬN CỦA KHÁCH HÀNG",
            "signature_right": "CTY TNHH SANDEN INTERCOOL VIỆT NAM"
        },
        "contract": {
            "seller": {
                "line1_name": "BÊN B (BÊN BÁN): CÔNG TY TNHH SANDEN INTERCOOL VIỆT NAM",
                "line2_account": "Tài khoản số: 580 508 202 058 tại Ngân Hàng Thương Mại Cổ Phần Á Châu – PGD Tân Định – TP.HCM",
                "line3_address": "Địa chỉ: Tầng 5 - Tòa nhà Nam Việt - Số 261 Hoàng Văn Thụ - Phường Tân Sơn Hòa, Tp.HCM",
                "line4_phone": "Điện thoại: 028-6276-6012",
                "line5_tax_code": "Mã số thuế: 0313167222",
                "line6_rep": "Đại diện là: Ông LÊ TRƯỜNG SƠN",
                "line7_position": "Chức vụ: Giám đốc"
            },
            "payment_terms": "- Đợt 1: Bên Mua tạm ứng cho Bên Bán 100% giá trị hợp đồng, tương đương số tiền: {{tong_cong}} VNĐ (Bằng chữ: {{tien_bang_chu}}) trong vòng 03 ngày làm việc sau khi hai bên ký kết",
            "delivery_location": "Địa điểm giao hàng: {{dia_chi}} hoặc có thỏa thuận khác mà không phát sinh chi phí."
        }
    }

    if not os.path.exists(config_path):
        return defaults

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            # Merge user_config into defaults (deep merge simple level)
            for section in defaults:
                if section in user_config:
                    if isinstance(defaults[section], dict) and isinstance(user_config[section], dict):
                        defaults[section].update(user_config[section])
                    else:
                        defaults[section] = user_config[section]
    except Exception as err:
        print(f"Lỗi đọc config.json, sử dụng mặc định: {err}")
    
    return defaults


# Tải cấu hình
_CONFIG = load_config()

# Các hằng số (Exposed for other modules)
COMPANY_NAME = _CONFIG["company"]["name"]
COMPANY_OFFICE = _CONFIG["company"]["office"]
COMPANY_PHONE = _CONFIG["company"]["phone"]
COMPANY_TAX_CODE = _CONFIG["company"]["tax_code"]

QUOTATION_TITLE = _CONFIG["quotation"]["title"]
QUOTATION_INTRO = _CONFIG["quotation"]["intro"]
QUOTATION_NOTES_TITLE = _CONFIG["quotation"]["notes_title"]
QUOTATION_SIGNATURE_LEFT = _CONFIG["quotation"]["signature_left"]
QUOTATION_SIGNATURE_RIGHT = _CONFIG["quotation"]["signature_right"]
QUOTATION_CLOSING = _CONFIG["quotation"]["closing"]

CONTRACT_SELLER = _CONFIG["contract"]["seller"]
CONTRACT_PAYMENT_TERMS = _CONFIG["contract"]["payment_terms"]
CONTRACT_DELIVERY_LOCATION = _CONFIG["contract"]["delivery_location"]


def build_quotation_content(values):
    partner_name = values.get("TEN_DOI_TAC", "").strip()
    address = values.get("dia_chi", "").strip()
    current_date = values.get("NGAY_HIEN_TAI", "").strip()

    # Xử lý các notes để thay thế placeholder {{dia_chi}}
    raw_notes = _CONFIG["quotation"]["notes"]
    processed_notes = [n.replace("{{dia_chi}}", address) for n in raw_notes]

    return {
        "header_lines": [
            COMPANY_NAME,
            COMPANY_OFFICE,
            COMPANY_PHONE,
            COMPANY_TAX_CODE,
        ],
        "title": QUOTATION_TITLE,
        "greeting": f"Kính gửi: Quý khách hàng {partner_name}".strip(),
        "intro": QUOTATION_INTRO,
        "notes_title": QUOTATION_NOTES_TITLE,
        "notes": processed_notes,
        "closing": QUOTATION_CLOSING,
        "date_line": f"Tp. HCM, Ngày {current_date}".strip(),
        "signature_left": QUOTATION_SIGNATURE_LEFT,
        "signature_right": QUOTATION_SIGNATURE_RIGHT,
    }


def build_quotation_placeholder_content():
    return build_quotation_content(
        {
            "TEN_DOI_TAC": "{{TEN_DOI_TAC}}",
            "dia_chi": "{{dia_chi}}",
            "NGAY_HIEN_TAI": "{{NGAY_HIEN_TAI}}",
        }
    )


def build_item_description(item):
    product_name = str(item.get("san_pham", "") or "").strip()
    model = str(item.get("model", "") or "").strip()
    if product_name and model:
        return f"{product_name} - {model}"
    return product_name or model


def html_text(value):
    return escape(str(value or ""))
