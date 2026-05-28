import streamlit as st
import streamlit.components.v1 as components
import re
import json
import base64
import secrets
import string
import urllib.request
import urllib.parse
import urllib.error

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
APP_BASE_URL = "https://carfreeoh-rentcalculator.streamlit.app"
CAPRIO_LOGO_B64 = "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"
IS_CLIENT_VIEW = st.query_params.get("view") == "client" and bool(st.query_params.get("q"))

CHO = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
JUNG = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅙ","ㅚ","ㅛ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"]
JONG = ["","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]

KEY = {
    "ㄱ":"r","ㄲ":"R","ㄴ":"s","ㄷ":"e","ㄸ":"E","ㄹ":"f","ㅁ":"a","ㅂ":"q","ㅃ":"Q","ㅅ":"t","ㅆ":"T","ㅇ":"d","ㅈ":"w","ㅉ":"W","ㅊ":"c","ㅋ":"z","ㅌ":"x","ㅍ":"v","ㅎ":"g",
    "ㅏ":"k","ㅐ":"o","ㅑ":"i","ㅒ":"O","ㅓ":"j","ㅔ":"p","ㅕ":"u","ㅖ":"P","ㅗ":"h","ㅛ":"y","ㅜ":"n","ㅠ":"b","ㅡ":"m","ㅣ":"l",
    "ㅘ":"hk","ㅙ":"ho","ㅚ":"hl","ㅝ":"nj","ㅞ":"np","ㅟ":"nl","ㅢ":"ml",
    "ㄳ":"rt","ㄵ":"sw","ㄶ":"sg","ㄺ":"fr","ㄻ":"fa","ㄼ":"fq","ㄽ":"ft","ㄾ":"fx","ㄿ":"fv","ㅀ":"fg","ㅄ":"qt"
}

def hangul_to_eng(text):
    result = ""
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            base = code - 0xAC00
            cho = base // 588
            jung = (base % 588) // 28
            jong = base % 28
            result += KEY.get(CHO[cho], "")
            result += KEY.get(JUNG[jung], "")
            result += KEY.get(JONG[jong], "")
        else:
            result += ch
    return result.lower()


def is_short_code(value):
    value = str(value or "").strip()
    return bool(re.fullmatch(r"[A-Z0-9]{6,10}", value))


def generate_share_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def supabase_request(method, path, payload=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    url = f"{SUPABASE_URL}{path}"
    data = None
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Prefer"] = "return=minimal"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else True
    except Exception:
        return None


def save_share_data(data):
    for _ in range(5):
        code = generate_share_code()
        result = supabase_request(
            "POST",
            "/rest/v1/share_links",
            [{"code": code, "payload": data}]
        )
        if result is not None:
            return code
    return ""


def load_share_data(code):
    code = str(code or "").strip().upper()
    if not is_short_code(code):
        return {}

    result = supabase_request(
        "GET",
        f"/rest/v1/share_links?code=eq.{urllib.parse.quote(code)}&select=payload"
    )

    if isinstance(result, list) and result:
        return result[0].get("payload", {}) or {}
    return {}

def encode_share_data(data):
    json_text = json.dumps(data, ensure_ascii=False)
    return base64.urlsafe_b64encode(json_text.encode("utf-8")).decode("utf-8")

def decode_share_data(encoded_text):
    encoded_text = str(encoded_text or "").strip()

    if is_short_code(encoded_text):
        loaded_data = load_share_data(encoded_text)
        if loaded_data:
            return loaded_data

    try:
        padding = "=" * (-len(encoded_text) % 4)
        decoded = base64.urlsafe_b64decode((encoded_text + padding).encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}

if not IS_CLIENT_VIEW:
    if not APP_PASSWORD:
        st.warning("APP_PASSWORD가 설정되지 않았습니다.")
        st.stop()

    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False

    if not st.session_state.auth_ok:
        input_password = st.text_input(
            "",
            type="password",
            placeholder="비밀번호 입력"
        )

        if input_password:
            pw_input = input_password.strip().lower()
            pw_secret = APP_PASSWORD.strip().lower()
            pw_secret_eng = hangul_to_eng(pw_secret)

            if pw_input == pw_secret or pw_input == pw_secret_eng:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
                st.stop()
        else:
            st.stop()


# 레이아웃 완벽 정렬 및 불필요한 공백 제거용 CSS
st.markdown("""
    <style>
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* 상단 공통 조건 박스 및 테이블 */
    .common-info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .common-table { width: 100%; border-collapse: collapse; background-color: #ffffff; text-align: center; font-size: 13px; }
    .common-table th { background-color: #f1f3f5; color: #0b3873; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .common-table td { padding: 8px; border: 1px solid #dee2e6; color: #333333; }

    /* 메인 비교 테이블 */
    .excel-header-blue { background-color: #0b3873; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px; margin-bottom: 12px; }
    .excel-header-gray { background-color: #5a5a5a; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 10px; }
    .capture-box { border: 2px solid #0b3873; padding: 15px; border-radius: 6px; background-color: #ffffff; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 8px; text-align: center; margin-top: -7px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 8px; text-align: center; margin-top: -7px; }
    
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 8px; border: 1px solid #dee2e6; height: 40px; }
    
    /* 하단 검증 요율표 */
    .matrix-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-bottom: 10px; }
    .matrix-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 5px; border: 1px solid #dee2e6; }
    .matrix-table td { padding: 5px; border: 1px solid #dee2e6; }
    
    .td-highlight { background-color: #e2efda; color: #375623; font-weight: bold; }
    .bg-light { background-color: #f8f9fa; }
    .text-blue { color: #0b3873; font-weight: bold; }
    .font-bold { font-weight: bold; }

    /* 할부·렌트·리스 비교표 셀 색상 클래스 */
    .compare-cat { background:#0b3873; color:white; font-weight:bold; }
    .compare-legal { background:#6b8e23; color:white; font-weight:bold; }
    .compare-item { background:#ddebf7; font-weight:bold; }

    /* 고객용 비교 조건 설정표 */
    .rent-highlight {
        background-color: #e2efda !important;
        color: #375623 !important;
        font-weight: bold !important;
    }

    @media (max-width: 768px) {
        .client-condition-table,
        .client-condition-table thead,
        .client-condition-table tbody,
        .client-condition-table tr,
        .client-condition-table th,
        .client-condition-table td {
            display: block !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }

        .client-condition-table thead {
            display: none !important;
        }

        .client-condition-table tr {
            display: block !important;
        }

        .client-condition-table td {
            display: grid !important;
            grid-template-columns: 110px 1fr !important;
            align-items: center !important;
            text-align: left !important;
            padding: 8px !important;
            font-size: 13px !important;
            border-bottom: 1px solid #dee2e6 !important;
            word-break: keep-all !important;
        }

        .client-condition-table td::before {
            font-weight: 800 !important;
            color: #0b3873 !important;
            background: #f1f3f5 !important;
            padding: 8px !important;
            margin: -8px 8px -8px -8px !important;
        }

        .client-condition-table td:nth-child(1)::before { content: "법인 여부"; }
        .client-condition-table td:nth-child(2)::before { content: "할부 선납금"; }
        .client-condition-table td:nth-child(3)::before { content: "할부 금리"; }
        .client-condition-table td:nth-child(4)::before { content: "연 보험료"; }
        .client-condition-table td:nth-child(5)::before { content: "할부 잔존"; }
        .client-condition-table td:nth-child(6)::before { content: "렌트 잔존"; }
    }


    /* 실제 다크 테마에서만 적용되는 보정: 라이트 모드 영향 없음 */
    html.caprio-dark .common-info-box {
        background-color: #111821 !important;
        border-color: #2f3b4a !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .common-info-box div,
    html.caprio-dark .common-info-box b {
        color: #f3f6fb !important;
    }

    html.caprio-dark .common-info-box div[style*="color:#0b3873"],
    html.caprio-dark .common-info-box div[style*="color: #0b3873"] {
        color: #9fc7ff !important;
    }

    html.caprio-dark .common-table,
    html.caprio-dark .common-table tbody,
    html.caprio-dark .common-table tr {
        background-color: #0e141c !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .common-table th {
        background-color: #0b3873 !important;
        color: #ffffff !important;
        border-color: #354255 !important;
    }

    html.caprio-dark .common-table td {
        background-color: #0e141c !important;
        color: #f3f6fb !important;
        border-color: #354255 !important;
    }

    html.caprio-dark .common-table td.font-bold,
    html.caprio-dark .common-table td[style*="color:#111"],
    html.caprio-dark .common-table td[style*="color: #111"] {
        color: #ffffff !important;
    }

    html.caprio-dark .pure-table,
    html.caprio-dark .matrix-table {
        background-color: #0e141c !important;
        color: #f3f6fb !important;
        border-color: #354255 !important;
    }

    html.caprio-dark .pure-table th,
    html.caprio-dark .matrix-table th {
        background-color: #0b3873 !important;
        color: #ffffff !important;
        border-color: #46566d !important;
    }

    html.caprio-dark .pure-table td,
    html.caprio-dark .matrix-table td {
        background-color: #0e141c !important;
        color: #f3f6fb !important;
        border-color: #46566d !important;
    }

    html.caprio-dark .bg-light,
    html.caprio-dark tr.bg-light td {
        background-color: #151f2b !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .text-blue {
        color: #9fc7ff !important;
    }

    html.caprio-dark .matrix-table td.td-highlight,
    html.caprio-dark .matrix-table tr.td-highlight td {
        background-color: #173f1b !important;
        color: #d8ffd2 !important;
        font-weight: 900 !important;
    }

    html.caprio-dark .rent-highlight {
        background-color: #253b24 !important;
        color: #c9f5bf !important;
        font-weight: 800 !important;
    }

    /* 할부·렌트·리스 비교표 - class 기반 다크모드 */
    html.caprio-dark .compare-cat{
        background:#144b96 !important;
        background-color:#144b96 !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-item{
        background:#2b4461 !important;
        background-color:#2b4461 !important;
        color:#ffffff !important;
        font-weight:700 !important;
    }

    html.caprio-dark .compare-legal{
        background:#6d9a2e !important;
        background-color:#6d9a2e !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-summary-table td:not(.compare-cat):not(.compare-item):not(.compare-legal):not([style*="background:#0b3873"]):not([style*="background: #0b3873"]):not([style*="background:#6b8e23"]):not([style*="background: #6b8e23"]):not([style*="background:#ddebf7"]):not([style*="background: #ddebf7"]) {
        background-color: #0e141c !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .guide-card {
        background-color: #111821 !important;
        border-color: #2f3b4a !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .guide-title {
        color: #9fc7ff !important;
    }

    html.caprio-dark .guide-copy,
    html.caprio-dark .guide-subtitle,
    html.caprio-dark .guide-list,
    html.caprio-dark .guide-list li,
    html.caprio-dark .reality-item,
    html.caprio-dark .reality-item b {
        color: #f3f6fb !important;
    }

    html.caprio-dark .reality-box {
        background-color: #151f2b !important;
        border-color: #344255 !important;
        color: #f3f6fb !important;
    }

    html.caprio-dark .reality-title {
        color: #ffffff !important;
    }

    html.caprio-dark .excel-header-gray {
        background-color: #243142 !important;
        color: #ffffff !important;
        border: 1px solid #46566d !important;
    }

    html.caprio-dark .excel-green {
        background-color: #20391f !important;
        color: #d8ffd2 !important;
        border-color: #4f7f46 !important;
    }

    html.caprio-dark .excel-red {
        background-color: #3b2323 !important;
        color: #ffd0d0 !important;
        border-color: #7a4040 !important;
    }

    html.caprio-dark span[style*="color:red"],
    html.caprio-dark span[style*="color: red"],
    html.caprio-dark div[style*="color:red"],
    html.caprio-dark div[style*="color: red"] {
        color: #ff7777 !important;
        white-space: nowrap !important;
    }

    html.caprio-dark .readonly-sidebar-value {
        background-color: #101722 !important;
        border: 1px solid #46566d !important;
        color: #f3f6fb !important;
    }

    @media (max-width: 768px) {
        html.caprio-dark .common-table td::before,
        html.caprio-dark .client-condition-table td::before {
            background-color: #1b2a3c !important;
            color: #9fc7ff !important;
        }

        /* 모바일 - 인수형 상단 간격 */
        .compare-card {
            margin-top: 18px !important;
        }
    }


    /* 다크모드 - 할부·렌트·리스 비교표 셀 클래스 기반 최종 보정 */
    html.caprio-dark .compare-summary-table .compare-cat {
        background:#0b3873 !important;
        background-color:#0b3873 !important;
    }

    html.caprio-dark .compare-summary-table .compare-item {
        background:#23364d !important;
        background-color:#23364d !important;
    }

    html.caprio-dark .compare-summary-table .compare-legal {
        background:#7fb52b !important;
        background-color:#7fb52b !important;
    }

    
    /* 렌트 견적 라벨 잘림 방지 */
    div[data-testid="stTextArea"] label {
        padding-top: 8px !important;
        min-height: 32px !important;
        overflow: visible !important;
    }

    div[data-testid="stTextArea"] label p {
        margin-top: 0 !important;
        line-height: 1.5 !important;
        overflow: visible !important;
    }

    /* 모바일 - 반납형/인수형 비교표 사이 간격 */
    .mobile-compare-gap {
        display: none;
    }

    @media (max-width: 768px) {
        .mobile-compare-gap {
            display: block;
            height: 18px;
        }

        /* 모바일 - 할부·렌트·리스 비교표 가로폭 보정 */
        .compare-summary-table {
            width: 100% !important;
            table-layout: fixed !important;
            font-size: 11px !important;
        }

        .compare-summary-table th,
        .compare-summary-table td {
            writing-mode: horizontal-tb !important;
            white-space: normal !important;
            word-break: keep-all !important;
            overflow-wrap: normal !important;
            line-height: 1.35 !important;
            padding: 6px 4px !important;
        }

        .compare-summary-table th:nth-child(1),
        .compare-summary-table td:nth-child(1) {
            width: 13% !important;
        }

        .compare-summary-table th:nth-child(2),
        .compare-summary-table td:nth-child(2) {
            width: 24% !important;
        }

        .compare-summary-table th:nth-child(3),
        .compare-summary-table td:nth-child(3),
        .compare-summary-table th:nth-child(4),
        .compare-summary-table td:nth-child(4),
        .compare-summary-table th:nth-child(5),
        .compare-summary-table td:nth-child(5) {
            width: 21% !important;
        }
    }
    


    /* ==============================
       카프리오 브랜딩/모바일 UI 최종 보정
       ============================== */
    .caprio-top-brand {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 46px;
        z-index: 999998;
        pointer-events: none;
        display: flex;
        align-items: center;
        padding: 0 160px 0 46px;
        box-sizing: border-box;
        background: linear-gradient(90deg, rgba(7,13,24,0.96) 0%, rgba(9,18,33,0.88) 55%, rgba(7,13,24,0.74) 100%);
        border-bottom: 1px solid rgba(58,130,255,0.32);
        box-shadow: 0 8px 22px rgba(0,0,0,0.16);
    }

    .caprio-top-brand-inner {
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
        width: 100%;
    }

    .caprio-top-logo {
        height: 30px;
        width: auto;
        display: block;
        flex: 0 0 auto;
        filter: drop-shadow(0 0 7px rgba(40,111,255,0.45));
    }

    .caprio-top-divider {
        width: 1px;
        height: 18px;
        background: rgba(255,255,255,0.32);
        flex: 0 0 auto;
    }

    .caprio-top-slogan {
        font-size: 14px;
        line-height: 1;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        white-space: nowrap;
    }

    .caprio-top-slogan strong {
        color: #6fb6ff;
        font-weight: 900;
    }

    html:not(.caprio-dark) .caprio-top-brand {
        background: rgba(255,255,255,0.86);
        border-bottom: 1px solid rgba(20,75,150,0.12);
        box-shadow: 0 6px 18px rgba(15,50,90,0.10);
        backdrop-filter: blur(10px);
    }

    html:not(.caprio-dark) .caprio-top-divider {
        background: rgba(11,56,115,0.20);
    }

    html:not(.caprio-dark) .caprio-top-slogan {
        color: #172842;
    }

    html:not(.caprio-dark) .caprio-top-slogan strong {
        color: #0b70df;
    }

    .common-info-box {
        box-shadow: 0 8px 22px rgba(15,50,90,0.05);
    }

    .vehicle-table-mobile {
        display: none;
    }

    .vehicle-table-mobile th,
    .vehicle-table-mobile td {
        word-break: keep-all;
    }

    .vehicle-table-mobile .vehicle-mobile-primary th {
        background: #0b438c !important;
        color: #ffffff !important;
    }

    .vehicle-table-mobile .vehicle-mobile-secondary th {
        background: #14549f !important;
        color: #ffffff !important;
    }

    .excel-header-blue {
        background: linear-gradient(135deg, #083979 0%, #0c4f9f 58%, #062f66 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(21,89,166,0.55) !important;
        box-shadow: 0 7px 18px rgba(6,47,102,0.16);
        margin-top: 16px !important;
        margin-bottom: 12px !important;
    }

    .excel-header-gray {
        background: linear-gradient(135deg, #f1f8ff 0%, #e4f1ff 58%, #d9ebff 100%) !important;
        color: #073c7c !important;
        border: 1px solid #c8defa !important;
        box-shadow: 0 7px 18px rgba(30,99,171,0.10);
        margin-top: 26px !important;
        margin-bottom: 10px !important;
    }

    html.caprio-dark .common-info-box {
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }

    html.caprio-dark .vehicle-table-mobile .vehicle-mobile-primary th {
        background: #0b3873 !important;
        color: #ffffff !important;
    }

    html.caprio-dark .vehicle-table-mobile .vehicle-mobile-secondary th {
        background: #144b96 !important;
        color: #ffffff !important;
    }

    html.caprio-dark .excel-header-blue {
        background: linear-gradient(135deg, #0a2c5a 0%, #0b4b96 58%, #071d3b 100%) !important;
        color: #ffffff !important;
        border-color: #345b8a !important;
        box-shadow: 0 8px 22px rgba(0,0,0,0.24);
    }

    html.caprio-dark .excel-header-gray {
        background: linear-gradient(135deg, #20344c 0%, #162a42 58%, #111f31 100%) !important;
        color: #f3f6fb !important;
        border-color: #46566d !important;
        box-shadow: 0 8px 22px rgba(0,0,0,0.24);
    }

    @media (max-width: 768px) {
        .caprio-top-brand {
            height: 42px;
            padding: 0 92px 0 46px;
        }

        .caprio-top-logo {
            height: 26px;
        }

        .caprio-top-divider {
            height: 15px;
        }

        .caprio-top-slogan {
            font-size: 11px;
        }

        .common-info-box {
            padding: 14px !important;
            margin-bottom: 24px !important;
        }

        .vehicle-table-desktop {
            display: none !important;
        }

        .vehicle-table-mobile {
            display: table !important;
            width: 100% !important;
            table-layout: fixed !important;
            border-collapse: separate !important;
            border-spacing: 0 !important;
            overflow: hidden !important;
            border-radius: 8px !important;
            font-size: 12px !important;
        }

        .vehicle-table-mobile th {
            padding: 8px 4px !important;
            border: 1px solid #d7e0ec !important;
            font-size: 12px !important;
            line-height: 1.25 !important;
            text-align: center !important;
            font-weight: 900 !important;
        }

        .vehicle-table-mobile td {
            padding: 9px 5px !important;
            border: 1px solid #d7e0ec !important;
            font-size: 12px !important;
            line-height: 1.35 !important;
            text-align: center !important;
            font-weight: 800 !important;
            background: #ffffff !important;
            color: #111827 !important;
        }

        html.caprio-dark .vehicle-table-mobile th,
        html.caprio-dark .vehicle-table-mobile td {
            border-color: #46566d !important;
        }

        html.caprio-dark .vehicle-table-mobile td {
            background: #0e141c !important;
            color: #f3f6fb !important;
        }

        .excel-header-gray {
            width: 100% !important;
            margin-top: 30px !important;
            margin-bottom: 10px !important;
        }

        .excel-header-blue {
            width: 100% !important;
            margin-top: 20px !important;
            margin-bottom: 12px !important;
        }

        .common-info-box + .excel-header-gray,
        .excel-red + .excel-header-blue,
        .excel-green + .excel-header-blue,
        .excel-red + .excel-header-gray,
        .excel-green + .excel-header-gray {
            margin-top: 26px !important;
        }
    }

    </style>
""", unsafe_allow_html=True)

if IS_CLIENT_VIEW:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 실제 Streamlit 테마 배경을 감지해 다크모드일 때만 보정 클래스 부여
components.html("""
<script>
(function(){
    const doc = window.parent.document;
    function isDarkColor(color){
        const nums = color.match(/\d+/g);
        if(!nums || nums.length < 3) return false;
        const r = parseInt(nums[0]), g = parseInt(nums[1]), b = parseInt(nums[2]);
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness < 140;
    }
    function applyDarkClass(){
        const app = doc.querySelector('.stApp') || doc.body;
        const bg = window.parent.getComputedStyle(app).backgroundColor;
        const isDark = isDarkColor(bg);
        doc.documentElement.classList.toggle('caprio-dark', isDark);
        doc.body.classList.toggle('caprio-dark', isDark);
    }
    applyDarkClass();
    setInterval(applyDarkClass, 1000);
})();
</script>
""", height=0, width=0)

st.markdown(f"""
    <div class="caprio-top-brand">
        <div class="caprio-top-brand-inner">
            <img class="caprio-top-logo" src="data:image/png;base64,{CAPRIO_LOGO_B64}" alt="카프리오">
            <span class="caprio-top-divider"></span>
            <span class="caprio-top-slogan">카 라이프에 <strong>자유</strong>를 더하다</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# 초기 기본값 설정
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_option = "-"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 0
cc_text = "1600CC이하"
cc_raw_text = "1598cc"
fuel_text = "휘발유/전기"
passenger_count = 7
car_shape = "하이브리드"
installment_resale_pct = 50 # 할부 잔존가치(매각율) 기본값
rent_resale_pct = 58       # 렌트 고정 잔존가치(기본값 58%)

# 공유 링크로 접속한 경우 기본값 반영
shared_quote_data = {}
if st.query_params.get("q"):
    shared_quote_data = decode_share_data(st.query_params.get("q", ""))

if shared_quote_data:
    car_name = shared_quote_data.get("car_name", car_name)
    car_option = shared_quote_data.get("car_option", car_option)
    car_price = int(shared_quote_data.get("car_price", car_price))
    months = int(shared_quote_data.get("months", months))
    mileage = shared_quote_data.get("mileage", mileage)
    rent_monthly_pay = int(shared_quote_data.get("rent_monthly_pay", rent_monthly_pay))
    rent_deposit = int(shared_quote_data.get("rent_deposit", rent_deposit))
    cc_text = shared_quote_data.get("cc_text", cc_text)
    cc_raw_text = shared_quote_data.get("cc_raw_text", cc_raw_text)
    fuel_text = shared_quote_data.get("fuel_text", fuel_text)
    passenger_count = int(shared_quote_data.get("passenger_count", passenger_count))
    car_shape = shared_quote_data.get("car_shape", car_shape)
    installment_resale_pct = int(shared_quote_data.get("installment_resale_pct", installment_resale_pct))
    rent_resale_pct = float(shared_quote_data.get("rent_resale_pct", rent_resale_pct))

def make_share_url():
    share_data = {
        "car_name": car_name,
        "car_option": car_option,
        "car_price": car_price,
        "months": months,
        "mileage": mileage,
        "rent_monthly_pay": rent_monthly_pay,
        "rent_deposit": rent_deposit,
        "cc_text": cc_text,
        "cc_raw_text": cc_raw_text,
        "fuel_text": fuel_text,
        "passenger_count": passenger_count,
        "car_shape": car_shape,
        "installment_resale_pct": installment_resale_pct,
        "insurance_annual": insurance_annual if "insurance_annual" in globals() else 1000000,
        "installment_rate": installment_rate if "installment_rate" in globals() else 5.0,
        "installment_prepaid": installment_prepaid if "installment_prepaid" in globals() else 10000000,
        "is_corporate": is_corporate if "is_corporate" in globals() else False,
        "rent_resale_pct": rent_resale_pct
    }
    short_code = save_share_data(share_data)
    if short_code:
        return f"{APP_BASE_URL}/?view=client&q={short_code}"

    encoded = encode_share_data(share_data)
    return f"{APP_BASE_URL}/?view=client&q={encoded}"
    
# ==========================================
# [SIDEBAR] 조건 설정 구역
# ==========================================
if IS_CLIENT_VIEW:
    is_corporate = bool(shared_quote_data.get("is_corporate", False))
    installment_prepaid = int(shared_quote_data.get("installment_prepaid", 10000000))
    installment_rate = float(shared_quote_data.get("installment_rate", 5.0))
    insurance_annual = int(shared_quote_data.get("insurance_annual", 1000000))
else:
    # ==========================================
    # [SIDEBAR] 조건 설정 구역
    # ==========================================
    st.sidebar.header("📋 할부 조건설정")

    is_corporate = st.sidebar.checkbox("🏢 법인 고객 여부", value=False)

    installment_prepaid = int(
        st.sidebar.text_input(
            "💵 할부 선납금",
            value=f"{int(shared_quote_data.get('installment_prepaid', 10000000)):,}"
        ).replace(",", "")
    )

    installment_rate = st.sidebar.number_input(
        "📈 할부 금리 (%)",
        value=float(shared_quote_data.get("installment_rate", 5.0)),
        step=0.1
    )

    insurance_annual = int(
        st.sidebar.text_input(
            "🛡️ 연 개인 보험료",
            value=f"{int(shared_quote_data.get('insurance_annual', 1000000)):,}"
        ).replace(",", "")
    )

    st.sidebar.markdown("---")

    installment_resale_pct = st.sidebar.number_input(
        "📉 할부 잔존가치 (%)",
        value=installment_resale_pct,
        min_value=0,
        max_value=100,
        step=1
    )


def auto_convert_quote(raw_text):
    if "견적서" not in raw_text or "최종차량가격" not in raw_text:
        return raw_text

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines_raw = [line.strip() for line in text.split("\n")]
    lines_clean = [line for line in lines_raw if line]

    def only_num(v):
        return "".join(re.findall(r"\d+", v))

    def money_after(label):
        m = re.search(label + r"\s*[\t ]*([0-9,]+)원", text)
        return only_num(m.group(1)) if m else ""

    def percent_after(label):
        m = re.search(label + r"\s*[\t ]*([0-9.]+)%", text)
        return m.group(1) + "%" if m else ""

    def line_money_after(label):
        m = re.search(label + r"\s*[\t ]*[0-9.]+%\s*[\t ]*([0-9,]+)원", text)
        return only_num(m.group(1)) if m else "0"

    car_name_val = ""
    for i, line in enumerate(lines_clean):
        if line == "차종" and i + 1 < len(lines_clean):
            car_name_val = lines_clean[i + 1]
            break

    car_name_val = re.sub(r"\b20\d{2}년형\b", "", car_name_val)
    car_name_val = re.sub(r"디 올-뉴|디 올 뉴|더 뉴|올 뉴", "", car_name_val)
    car_name_val = re.sub(r"\([^)]*개별소비세[^)]*\)", "", car_name_val)
    car_name_val = re.sub(r"\([A-Z0-9 ]*(?:F/L|FL)[A-Z0-9 /]*\)", "", car_name_val)
    car_name_val = re.sub(r"\s+", " ", car_name_val).strip()

    option_val = ""
    if "옵션가격0원" not in text.replace(" ", ""):
        option_lines = []
        in_option = False
        for line in lines_clean:
            if line == "옵션":
                in_option = True
                continue
            if in_option and line.startswith("옵션가격"):
                break
            if in_option:
                option_lines.append(re.sub(r"\([0-9,]+원\)", "", line).strip())
        option_val = " / ".join([v for v in option_lines if v])

    car_price_val = money_after("최종차량가격")
    months_val = only_num(re.search(r"기간\s*[\t ]*([0-9]+)개월", text).group(1)) if re.search(r"기간\s*[\t ]*([0-9]+)개월", text) else ""
    mileage_match = re.search(r"약정거리\s*[\t ]*([0-9.]+만)km", text)
    mileage_val = mileage_match.group(1) + "Km" if mileage_match else ""
    monthly_val = money_after("월 납입금")
    prepaid_val = line_money_after("선수금")
    resale_val = percent_after(r"잔존가치\(인수\)")

    fuel_line = ""
    for line in lines_clean:
        if "출시" in line and "·" in line:
            fuel_line = line
            break

    fuel_parts = [p.strip() for p in fuel_line.split("·")]
    fuel_val = fuel_parts[1] if len(fuel_parts) >= 2 else ""
    
    cc_match = re.search(r"([0-9,]+)cc", fuel_line)
    cc_num = int(only_num(cc_match.group(1))) if cc_match else 0
    cc_raw_val = cc_match.group(1).replace(",", "") + "cc" if cc_match else ""

    passenger_match = re.search(r"([0-9]+)인승", car_name_val)
    passenger_val = int(passenger_match.group(1)) if passenger_match else 0

    if fuel_val == "전기" or fuel_val == "수소":
        cc_val = "전기차"
    elif cc_num <= 1000:
        cc_val = "1000CC이하"
    elif cc_num <= 1600:
        cc_val = "1600CC이하"
    elif cc_num <= 2000:
        cc_val = "2000CC이하"
    elif cc_num <= 2500:
        cc_val = "2500CC이하"
    else:
        cc_val = "3000CC초과"

    if fuel_val == "전기":
        shape_val = "전기"
    elif fuel_val == "수소":
        shape_val = "수소"
    elif cc_num > 0 and cc_num <= 1000:
        shape_val = "경차"
    elif "하이브리드" in car_name_val or fuel_val == "휘발유/전기":
        shape_val = "하이브리드"
    else:
        shape_val = "일반"

    return f"""차량명\t{car_name_val}
옵션\t{option_val}
차량가\t{car_price_val}
개월수\t{months_val}
약정거리\t{mileage_val}
월납입\t{monthly_val}
선납금\t{prepaid_val}
잔존(렌트)\t{resale_val}
CC\t{cc_val}
CC원문\t{cc_raw_val}
유종\t{fuel_val}
인승\t{passenger_val}
형태\t{shape_val}"""


# ==========================================
# [견적 이력 저장 / 견적 입력 / 사이드바 이력]
# ==========================================
raw_data = ""

if not IS_CLIENT_VIEW:
    if "quote_history" not in st.session_state:
        st.session_state.quote_history = []

    if "raw_quote_input" not in st.session_state:
        st.session_state.raw_quote_input = ""

    if "pending_quote_input" not in st.session_state:
        st.session_state.pending_quote_input = None

    if "pending_quick_edit" not in st.session_state:
        st.session_state.pending_quick_edit = None

    # ==========================================
    # [TOP MAIN] 타사 견적 파싱 구역
    # ==========================================
    if st.session_state.pending_quote_input is not None:
        st.session_state.raw_quote_input = st.session_state.pending_quote_input
        st.session_state.pending_quote_input = None

    raw_data = st.text_area(
        "📋 렌트 견적 붙여넣기",
        placeholder="견적 텍스트를 입력하세요.",
        height=80,
        key="raw_quote_input"
    )

    if raw_data:
        parsed_data = auto_convert_quote(raw_data)
        lines = parsed_data.strip().split('\n')
        for line in lines:
            parts = line.split('	') if '	' in line else (line.split(':') if ':' in line else line.split())
            if len(parts) >= 2:
                key = parts[0].strip()
                val = "".join(parts[1:]).strip()
                def clean_num(v): return int("".join(filter(str.isdigit, v))) if any(char.isdigit() for char in v) else 0
                
                if "차량명" in key: car_name = val
                elif "옵션" in key: car_option = val
                elif "차량가" in key: car_price = clean_num(val)
                elif "개월수" in key: months = clean_num(val)
                elif "약정거리" in key: mileage = val.replace(" ", "")
                elif "월납입" in key: rent_monthly_pay = clean_num(val)
                elif "선납금" in key or "보증금" in key: rent_deposit = clean_num(val)
                elif "잔존" in key: rent_resale_pct = float(val.replace("%", "").replace(" ", ""))
                elif key == "CC원문": cc_raw_text = val.replace(" ", "")
                elif key == "유종": fuel_text = val.replace(" ", "")
                elif key == "인승": passenger_count = clean_num(val)
                elif "CC" in key: cc_text = val.replace(" ", "")
                elif "형태" in key: car_shape = val.replace(" ", "")

    # ==========================================
    # [렌트 조건 빠른 수정]
    # ==========================================
    quick_edit_source_signature = raw_data.strip() if raw_data.strip() else f"{car_name}|{car_price}|{months}|{mileage}|{rent_monthly_pay}|{rent_resale_pct}"

    def quick_money_to_int(value):
        value_text = str(value).replace(",", "").strip()
        return int("".join(filter(str.isdigit, value_text))) if any(ch.isdigit() for ch in value_text) else 0

    def quick_pct_to_float(value, default_value):
        try:
            return float(str(value).replace("%", "").replace(",", "").strip())
        except Exception:
            return float(default_value)

    if st.session_state.get("quick_edit_source_signature") != quick_edit_source_signature:
        st.session_state.quick_rent_monthly_pay = f"{rent_monthly_pay:,}"
        st.session_state.quick_rent_resale_pct = f"{rent_resale_pct:g}"
        st.session_state.quick_months = int(months)
        st.session_state.quick_mileage = mileage
        st.session_state.quick_edit_applied = False
        st.session_state.quick_edit_source_signature = quick_edit_source_signature

    if st.session_state.pending_quick_edit is not None:
        pending_quick_edit = st.session_state.pending_quick_edit
        st.session_state.quick_rent_monthly_pay = f"{int(pending_quick_edit.get('rent_monthly_pay', rent_monthly_pay)):,}"
        st.session_state.quick_rent_resale_pct = f"{float(pending_quick_edit.get('rent_resale_pct', rent_resale_pct)):g}"
        st.session_state.quick_months = int(pending_quick_edit.get("months", months))
        st.session_state.quick_mileage = pending_quick_edit.get("mileage", mileage)
        st.session_state.quick_edit_applied = True
        st.session_state.pending_quick_edit = None

    quick_month_options = [24, 36, 48, 60]
    if int(st.session_state.quick_months) not in quick_month_options:
        quick_month_options.append(int(st.session_state.quick_months))
        quick_month_options = sorted(quick_month_options)

    quick_mileage_options = ["1만KM", "1.5만KM", "2만Km", "3만KM"]
    if st.session_state.quick_mileage not in quick_mileage_options:
        quick_mileage_options.append(st.session_state.quick_mileage)

    with st.form("quick_rent_edit_form"):
        st.markdown("#### 🛠️ 렌트 조건 빠른 수정")
        quick_col1, quick_col2, quick_col3, quick_col4, quick_col5 = st.columns([1.2, 1.1, 0.9, 1.0, 0.7])

        with quick_col1:
            st.text_input("월납입", key="quick_rent_monthly_pay")

        with quick_col2:
            st.text_input("렌트잔존(%)", key="quick_rent_resale_pct")

        with quick_col3:
            st.selectbox(
                "개월수",
                quick_month_options,
                key="quick_months"
            )

        with quick_col4:
            st.selectbox(
                "약정거리",
                quick_mileage_options,
                key="quick_mileage"
            )

        with quick_col5:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            quick_edit_submitted = st.form_submit_button("적용", use_container_width=True)

    if quick_edit_submitted:
        st.session_state.quick_edit_applied = True

    if st.session_state.get("quick_edit_applied"):
        rent_monthly_pay = quick_money_to_int(st.session_state.quick_rent_monthly_pay)
        rent_resale_pct = quick_pct_to_float(st.session_state.quick_rent_resale_pct, rent_resale_pct)
        months = int(st.session_state.quick_months)
        mileage = st.session_state.quick_mileage

    st.sidebar.markdown(
        '<div style="font-size:14px; font-weight:400; color:#262730;">📉 렌트 고정 잔존가치 (%)</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(f"""
    <div class="readonly-sidebar-value" style="background-color:white; padding:9px 13px; border-radius:8px; font-size:14px; color:#111; height:38px; display:flex; align-items:center;">
    {rent_resale_pct:g}
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # [견적 이력]
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🕘 견적 이력")

    if st.sidebar.button("➕ 현재 견적 저장"):

        if raw_data.strip() or car_name:

            short_car_name = (
                car_name[:15] + "..."
                if len(car_name) > 15
                else car_name
            )

            history_title = (
                f"{short_car_name}\n"
                f"월 {rent_monthly_pay:,}원｜{months}개월｜{mileage}"
            )

            st.session_state.quote_history.insert(
                0,
                {
                    "title": history_title,
                    "raw": raw_data,
                    "share_url": make_share_url(),
                    "quick_edit": {
                        "rent_monthly_pay": rent_monthly_pay,
                        "rent_resale_pct": rent_resale_pct,
                        "months": months,
                        "mileage": mileage
                    }
                }
            )

            st.session_state.quote_history = st.session_state.quote_history[:5]
            st.rerun()

    if st.session_state.quote_history:

        for idx, item in enumerate(st.session_state.quote_history):

            history_col1, history_col2 = st.sidebar.columns([0.74, 0.26], gap="small")

            with history_col1:
                if st.button(
                    f"📄 견적 {idx+1}",
                    key=f"history_{idx}",
                    help=item["title"],
                    use_container_width=True
                ):
                    st.session_state.pending_quote_input = item["raw"]
                    st.session_state.pending_quick_edit = item.get("quick_edit")
                    st.rerun()

            with history_col2:

                components.html(
                    f"""
                    <button
                        onclick="
                            navigator.clipboard.writeText({item['share_url']!r});
                            this.innerText='✅';
                            this.style.background='#dff3df';
                            this.style.border='1px solid #86c986';
                        "
                        style="
                            width:100%;
                            height:38px;
                            border-radius:8px;
                            border:1px solid #e3c86a;
                            background:#fff4c2;
                            cursor:pointer;
                            font-size:16px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                        "
                    >🔗</button>
                    """,
                    height=42
                )

        if st.sidebar.button("🗑️ 이력 전체 삭제"):
            st.session_state.quote_history = []
            st.session_state.raw_quote_input = ""
            st.rerun()

    else:
        st.sidebar.caption("저장된 견적이 없습니다.")

# ==========================================
# [BACKEND] 연산 로직
# ==========================================
e15 = "O" if passenger_count >= 9 else ""
e14 = "O" if "경차" in car_shape else ""
g14 = "O" if "전기" in car_shape or "수소" in car_shape else ""
i14 = "O" if "하이브리드" in car_shape else ""

if e15 != "" and g14 != "":
    reg_tax_raw = (car_price * 0.05) - 1400000
elif e15 != "":
    reg_tax_raw = car_price * 0.05
elif e14 != "":
    reg_tax_raw = (car_price * 0.04) - 750000
elif g14 != "":
    reg_tax_raw = (car_price * 0.07) - 1400000
else:
    reg_tax_raw = car_price * 0.07

reg_tax = max(0, int(reg_tax_raw))

if "전기" in cc_text:
    tax_annual = 130000
elif "1000" in cc_text:
    tax_annual = 104000
elif "1600" in cc_text:
    tax_annual = 291200
elif "2000" in cc_text:
    tax_annual = 520000
elif "2500" in cc_text:
    tax_annual = 650000
elif "3000" in cc_text:
    tax_annual = 780000
else:
    tax_annual = 130000

loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount / months)
installment_equal_pay = loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1) if r > 0 else loan_amount / months
installment_interest = int((installment_equal_pay * months) - loan_amount)

total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)

# 할부 잔존가치(매각) 산출
corporate_discount = 0.9 if (is_corporate and car_shape != "경차" and e15 == "") else 1.0
car_sell_value = int(car_price * (installment_resale_pct / 100) * corporate_discount)

# 렌트 고정 잔존가치 산출 (수정: 렌트 고정값 58% 사용)
rent_takeover_price = int(car_price * (rent_resale_pct / 100))

if e15 != "" and g14 != "":
    rent_takeover_tax_raw = (rent_takeover_price * 0.05) - 1400000
elif e15 != "":
    rent_takeover_tax_raw = rent_takeover_price * 0.05
elif e14 != "":
    rent_takeover_tax_raw = (rent_takeover_price * 0.04) - 750000
elif g14 != "":
    rent_takeover_tax_raw = (rent_takeover_price * 0.07) - 1400000
else:
    rent_takeover_tax_raw = rent_takeover_price * 0.07

rent_takeover_tax = max(0, int(rent_takeover_tax_raw))

resale_24_1 = "td-highlight" if mileage == "1만KM" and months == 24 else ""
resale_36_1 = "td-highlight" if mileage == "1만KM" and months == 36 else ""
resale_48_1 = "td-highlight" if mileage == "1만KM" and months == 48 else ""
resale_60_1 = "td-highlight" if mileage == "1만KM" and months == 60 else ""
resale_24_15 = "td-highlight" if mileage == "1.5만KM" and months == 24 else ""
resale_36_15 = "td-highlight" if mileage == "1.5만KM" and months == 36 else ""
resale_48_15 = "td-highlight" if mileage == "1.5만KM" and months == 48 else ""
resale_60_15 = "td-highlight" if mileage == "1.5만KM" and months == 60 else ""
resale_24_2 = "td-highlight" if mileage == "2만Km" and months == 24 else ""
resale_36_2 = "td-highlight" if mileage == "2만Km" and months == 36 else ""
resale_48_2 = "td-highlight" if mileage == "2만Km" and months == 48 else ""
resale_60_2 = "td-highlight" if mileage == "2만Km" and months == 60 else ""
resale_24_3 = "td-highlight" if mileage == "3만KM" and months == 24 else ""
resale_36_3 = "td-highlight" if mileage == "3만KM" and months == 36 else ""
resale_48_3 = "td-highlight" if mileage == "3만KM" and months == 48 else ""
resale_60_3 = "td-highlight" if mileage == "3만KM" and months == 60 else ""

rate_900_over = "td-highlight" if installment_rate >= 3.5 and installment_rate <= 4.8 else ""
rate_801_900 = "td-highlight" if installment_rate >= 4.9 and installment_rate <= 6.9 else ""
rate_701_800 = "td-highlight" if installment_rate >= 7.0 and installment_rate <= 8.9 else ""
rate_601_700 = "td-highlight" if installment_rate >= 9.0 and installment_rate <= 11.9 else ""
rate_600_under = "td-highlight" if installment_rate >= 12.0 and installment_rate <= 14.9 else ""

tax_1000 = "td-highlight" if "1000" in cc_text else ""
tax_1600 = "td-highlight" if "1600" in cc_text else ""
tax_2000 = "td-highlight" if "2000" in cc_text else ""
tax_2500 = "td-highlight" if "2500" in cc_text else ""
tax_3000 = "td-highlight" if "3000" in cc_text else ""
tax_ev = "td-highlight" if "전기" in cc_text else ""

reg_general = "td-highlight" if car_shape == "일반" and e15 == "" else ""
reg_light = "td-highlight" if "경차" in car_shape and e15 == "" else ""
reg_ev = "td-highlight" if ("전기" in car_shape or "수소" in car_shape) and e15 == "" else ""
reg_hybrid = "td-highlight" if "하이브리드" in car_shape and e15 == "" else ""
reg_van = "td-highlight" if e15 != "" else ""

tax_type_text = "승합차(9인승 이상)" if e15 != "" else car_shape

# ==========================================
# [공통 조건 구역]
# ==========================================
st.markdown(f"""
    <div class="common-info-box">
        <div style="font-size:15px; font-weight:bold; margin-bottom:10px; color:#0b3873;">🚘 비교 차량 공통 조건</div>
        <table class="common-table vehicle-table-desktop">
            <thead>
                <tr>
                    <th style="width: 35%;">차량명</th>
                    <th style="width: 25%;">옵션</th>
                    <th style="width: 16%;">차량가격</th>
                    <th style="width: 12%;">계약기간</th>
                    <th style="width: 12%;">약정거리</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="font-bold">{car_name}</td>
                    <td style="color:#111;">{car_option}</td>
                    <td class="font-bold" style="color:#111;">{car_price:,} 원</td>
                    <td>{months} 개월</td>
                    <td>{mileage}</td>
                </tr>
                <tr>
                    <th>유종</th>
                    <th>CC</th>
                    <th colspan="3"></th>
                </tr>
                <tr>
                    <td>{car_shape if fuel_text == "휘발유/전기" else fuel_text}</td>
                    <td>{cc_raw_text}</td>
                    <td colspan="3"></td>
                </tr>
            </tbody>
        </table>

        <table class="common-table vehicle-table-mobile">
            <tbody>
                <tr class="vehicle-mobile-primary">
                    <th>🚘 차량명</th>
                    <th>⚙️ 옵션</th>
                    <th>₩ 차량가</th>
                </tr>
                <tr>
                    <td>{car_name}</td>
                    <td>{car_option}</td>
                    <td>{car_price:,} 원</td>
                </tr>
                <tr class="vehicle-mobile-secondary">
                    <th>🗓️ 계약기간</th>
                    <th>🛣️ 약정거리</th>
                    <th>💧 유종</th>
                    <th>⚙️ CC</th>
                </tr>
                <tr>
                    <td>{months}개월</td>
                    <td>{mileage}</td>
                    <td>{car_shape if fuel_text == "휘발유/전기" else fuel_text}</td>
                    <td>{cc_raw_text}</td>
                </tr>
            </tbody>
        </table>
    </div>
""", unsafe_allow_html=True)


# 고객용 링크에서만 조건 설정표 노출
if IS_CLIENT_VIEW:
    st.markdown(f"""
        <div class="common-info-box" style="margin-top:-8px; margin-bottom:20px;">
            <div style="font-size:15px; font-weight:bold; margin-bottom:10px; color:#0b3873;">
                📋 할부 조건 설정
            </div>
            <table class="common-table client-condition-table">
                <thead>
                    <tr>
                        <th>법인 여부</th>
                        <th>할부 선납금</th>
                        <th>할부 금리</th>
                        <th>연 보험료</th>
                        <th>할부 잔존가치</th>
                        <th class="rent-highlight">렌트 잔존가치</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{"O" if is_corporate else "X"}</td>
                        <td>{installment_prepaid:,} 원</td>
                        <td>{installment_rate:g}%</td>
                        <td>{insurance_annual:,} 원</td>
                        <td>{installment_resale_pct:g}%</td>
                        <td class="rent-highlight">{rent_resale_pct:g}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# [📊 MAIN VISUAL] 대칭형 비교 테이블
# ==========================================
view_col1, view_col2 = st.columns(2)

# 1. 반납형 테이블
with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (반납형)</div>', unsafe_allow_html=True)
    
    inst_total_cost_ret = installment_prepaid + (inst_monthly_pay * months) + installment_interest + reg_tax + total_tax + total_ins - car_sell_value
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    html_ret = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">세부 항목</th><th style="width:33%;">일반 할부</th><th style="width:33%;">장기렌트(반납형)</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">(월)납입금<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(선납금 제외)</span></td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">할부이자</td><td>{installment_interest:,} 원</td><td>-</td></tr>
        <tr><td class="font-bold">취등록세</td><td>{reg_tax:,} 원</td><td rowspan="5" class="bg-light text-blue" style="vertical-align:middle;">월 렌트료에<br>전부 포함</td></tr>
        <tr><td class="font-bold">자동차세</td><td>{total_tax:,} 원</td></tr>
        <tr><td class="font-bold">보험료</td><td>{total_ins:,} 원</td></tr>
        <tr><td class="font-bold">만기 차량 매각</td><td>-{car_sell_value:,} 원</td></tr>
        <tr><td class="font-bold">-</td><td>-</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 환산 비용</td><td>{int(inst_total_cost_ret/months):,} 원</td><td>{int(rent_total_cost_ret/months):,} 원</td></tr>
        <tr class="bg-light font-bold" style="background-color:#e9ecef;"><td>💰 총 투입 비용</td><td>{inst_total_cost_ret:,} 원</td><td>{rent_total_cost_ret:,} 원</td></tr>
    </table>
    """
    st.markdown(html_ret, unsafe_allow_html=True)
    
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green">🏆 장기렌트 선택 시 할부 대비 {diff_ret:,}원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 이용이 {abs(diff_ret):,}원 더 유리합니다.</div>', unsafe_allow_html=True)

    st.markdown('<div class="mobile-compare-gap"></div>', unsafe_allow_html=True)

# 2. 인수형 테이블
with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (인수형)</div>', unsafe_allow_html=True)
    
    inst_total_cost_ins = installment_prepaid + (inst_monthly_pay * months) + installment_interest + reg_tax + total_tax + total_ins
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    html_ins = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">세부 항목</th><th style="width:33%;">일반 할부</th><th style="width:33%;">장기렌트(인수형)</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">(월)납입금<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(선납금 제외)</span></td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">할부이자</td><td>{installment_interest:,} 원</td><td>-</td></tr>
        <tr><td class="font-bold">취등록세</td><td>{reg_tax:,} 원</td><td rowspan="3" class="bg-light text-blue" style="vertical-align:middle;">월 렌트료에<br>전부 포함</td></tr>
        <tr><td class="font-bold">자동차세</td><td>{total_tax:,} 원</td></tr>
        <tr><td class="font-bold">보험료</td><td>{total_ins:,} 원</td></tr>
        <tr><td class="font-bold">만기 인수금</td><td>-</td><td>{rent_takeover_price:,} 원</td></tr>
        <tr><td class="font-bold">인수 시 취등록세</td><td>-</td><td>{rent_takeover_tax:,} 원</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 환산 비용</td><td>{int(inst_total_cost_ins/months):,} 원</td><td>{int(rent_total_cost_ins/months):,} 원</td></tr>
        <tr class="bg-light font-bold" style="background-color:#e9ecef;"><td>💰 총 투입 비용</td><td>{inst_total_cost_ins:,} 원</td><td>{rent_total_cost_ins:,} 원</td></tr>
    </table>
    """
    st.markdown(html_ins, unsafe_allow_html=True)
    
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green">🏆 장기렌트 선택 시 할부 대비 {diff_ins:,}원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 인수가 총 {abs(diff_ins):,}원 더 유리합니다.</div>', unsafe_allow_html=True)

# ==========================================
# [📊 BOTTOM] 검증 요율표 구역
# ==========================================
st.write("")
st.markdown('<div class="excel-header-gray">💻 내부 데이터 산출 요율 검증표</div>', unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown('''
**■ 잔존가치 예상표** 
<span style="color:#ff7a7a; font-size:10px;">*가솔린 무사고 기준</span>
''', unsafe_allow_html=True)

    st.markdown(f"""
    <table class="matrix-table">
        <tr><th>구분</th><th>24개월</th><th>36개월</th><th>48개월</th><th>60개월</th></tr>
        <tr><td>1만KM</td><td class="{resale_24_1}">78%</td><td class="{resale_36_1}">70%</td><td class="{resale_48_1}">63%</td><td class="{resale_60_1}">56%</td></tr>
        <tr><td>1.5만KM</td><td class="{resale_24_15}">75%</td><td class="{resale_36_15}">67%</td><td class="{resale_48_15}">60%</td><td class="{resale_60_15}">53%</td></tr>
        <tr><td>2만KM</td><td class="{resale_24_2}">72%</td><td class="{resale_36_2}">64%</td><td class="{resale_48_2}">57%</td><td class="{resale_60_2}">50%</td></tr>
        <tr><td>3만KM</td><td class="{resale_24_3}">65%</td><td class="{resale_36_3}">55%</td><td class="{resale_48_3}">48%</td><td class="{resale_60_3}">40%</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="margin-top:-22px; margin-left:0px;">
            <span style="color:#ff7a7a; font-size:11px; font-weight:600;">
                * 차량별 상이 · 시세 확인 필수
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


with m_col2:
    st.markdown("**■ 신용별 할부이자**")
    st.markdown(f"""
    <table class="matrix-table">
        <tr><th>구분</th><th>할부이자</th></tr>
        <tr class="{rate_900_over}"><td>900점 초과</td><td>3.5 ~ 4.8%</td></tr>
        <tr class="{rate_801_900}"><td>801 ~ 900점</td><td>4.9 ~ 6.9%</td></tr>
        <tr class="{rate_701_800}"><td>701 ~ 800점</td><td>7.0 ~ 8.9%</td></tr>
        <tr class="{rate_601_700}"><td>601 ~ 700점</td><td>9.0 ~ 11.9%</td></tr>
        <tr class="{rate_600_under}"><td>600점 이하</td><td>12.0 ~ 14.9%</td></tr>
    </table>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown("**■ 자동차세 (연간)**")
    st.markdown(f"""
    <table class="matrix-table">
        <tr><th>구분</th><th>연간 비용</th></tr>
        <tr class="{tax_1000}"><td>1000CC 이하</td><td>₩ 104,000</td></tr>
        <tr class="{tax_1600}"><td>1600CC 이하</td><td>₩ 291,200</td></tr>
        <tr class="{tax_2000}"><td>2000CC 이하</td><td>₩ 520,000</td></tr>
        <tr class="{tax_2500}"><td>2500CC 이하</td><td>₩ 650,000</td></tr>
        <tr class="{tax_3000}"><td>3000CC 초과</td><td>₩ 780,000</td></tr>
        <tr class="{tax_ev}"><td>전기차</td><td>₩ 130,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown("**■ 취등록세 감면율**")
    st.markdown(f"""
    <table class="matrix-table">
        <tr><th>구분</th><th>세율</th><th>감면 한도</th></tr>
        <tr class="{reg_general}"><td>일반</td><td>7%</td><td>-</td></tr>
        <tr class="{reg_light}"><td>경차</td><td>4%</td><td>75만 원</td></tr>
        <tr class="{reg_ev}"><td>전기/수소차</td><td>7%</td><td>140만 원</td></tr>
        <tr class="{reg_hybrid}"><td>하이브리드</td><td>7%</td><td>-</td></tr>
        <tr class="{reg_van}">
            <td>
                승합차
                <div style="color:red; font-size:10px; line-height:1; margin-top:-4px;">(9인승 이상 포함)</div>
            </td>
            <td>5%</td>
            <td>-</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)



# ==========================================
# [할부 · 렌트 · 리스 비교표]
# ==========================================
st.write("")
st.markdown('<div class="excel-header-gray" style="width:55%;">🚗 할부 · 렌트 · 리스 비교표</div>', unsafe_allow_html=True)

st.markdown("""
<table class="matrix-table compare-summary-table" style="width:55%; font-size:13px;">
<tr>
<th style="width:12%;">분류</th>
<th style="width:18%;">항목</th>
<th style="width:23%;">할부</th>
<th style="width:23%;">렌트</th>
<th style="width:24%;">리스</th>
</tr>

<tr>
<td class="compare-cat">번호판</td>
<td class="compare-item">일반번호판</td>
<td>O</td>
<td>X</td>
<td>O</td>
</tr>

<tr>
<td rowspan="2" class="compare-cat">재무/신용</td>
<td class="compare-item">금융·부채 영향</td>
<td>
O
<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(대출한도 영향)</span>
</td>
<td>X</td>
<td>
△
<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(대출한도 영향)</span>
</td>
</tr>
<tr>
<td class="compare-item">차량 자산 인식</td>
<td>
O
<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(재산세 등 인상)</span>
</td>
<td>X</td>
<td>X</td>
</tr>

<tr>
<td rowspan="2" class="compare-cat">비용</td>
<td class="compare-item">세금·보험 납부</td>
<td>별도 납부</td>
<td>월납입 포함</td>
<td>보험 별도</td>
</tr>
<tr>
<td class="compare-item">초기비용</td>
<td>차량가·취등록세 부담</td>
<td>선택 가능</td>
<td>선택 가능</td>
</tr>

<tr>
<td rowspan="3" class="compare-cat">보험·사고</td>
<td class="compare-item">보험 포함</td>
<td>X</td>
<td>O</td>
<td>X</td>
</tr>
<tr>
<td class="compare-item">보험·사고 처리</td>
<td>직접 가입·처리</td>
<td>보험 포함·지원</td>
<td>직접 가입·처리</td>
</tr>
<tr>
<td class="compare-item">사고 비용·리스크</td>
<td>수리비·감가 부담</td>
<td>면책금 처리</td>
<td>수리비·감가 부담</td>
</tr>

<tr>
<td rowspan="2" class="compare-cat">이력 관리</td>
<td class="compare-item">보험경력 인정</td>
<td>O</td>
<td>O</td>
<td>O</td>
</tr>
<tr>
<td class="compare-item">사고이력·보험할증</td>
<td>O</td>
<td>X</td>
<td>O</td>
</tr>

<tr>
<td class="compare-cat">관리</td>
<td class="compare-item">정비 선택 가능</td>
<td>O</td>
<td>O</td>
<td>O</td>
</tr>

<tr>
<td rowspan="2" class="compare-legal">법인</td>
<td class="compare-item">비용처리</td>
<td>O (최장 8년)</td>
<td>O (납입기간 내)</td>
<td>O (납입기간 내)</td>
</tr>
<tr>
<td class="compare-item">판매 시</td>
<td>
부가세 10% 발생
<br><span style="color:red; font-size:10px; display:block; margin-top:-2px; line-height:1;">(경차, 승합차 제외)</span>
</td>
<td>인수·반납 자유</td>
<td>인수·반납 자유</td>
</tr>
</table>
""", unsafe_allow_html=True)












# ==========================================
# [나에게 맞는 방식 선택 가이드]
# ==========================================
st.write("")
st.markdown('<div class="excel-header-gray">🚗 나에게 맞는 방식 선택 가이드</div>', unsafe_allow_html=True)

st.markdown("""
<style>
.guide-wrap{
    width:100%;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:18px;
    margin-top:12px;
}
.guide-card{
    width:100%;
    background:#ffffff;
    border:1px solid #d9e2ec;
    border-radius:8px;
    padding:18px;
    box-sizing:border-box;
}
.guide-title{
    font-size:23px;
    font-weight:800;
    color:#0b3873;
    margin-bottom:6px;
}
.guide-copy{
    font-size:18px;
    font-weight:700;
    color:#333;
    margin-bottom:12px;
    line-height:1.5;
}
.guide-subtitle{
    font-size:15px;
    font-weight:800;
    margin-bottom:6px;
}
.guide-list{
    font-size:14px;
    line-height:1.9;
    padding-left:20px;
    margin:0 0 12px 0;
}
.reality-box{
    background:#f4f6f8;
    border:1px solid #d9dee5;
    border-radius:6px;
    padding:12px;
}
.reality-title{
    font-size:18px;
    font-weight:800;
    margin-bottom:6px;
}
.reality-item{
    font-size:15px;
    line-height:1.7;
    margin-bottom:5px;
}
.match-card{
    margin-top:14px;
    border-radius:14px;
    padding:15px 16px;
    display:grid;
    grid-template-columns:76px 1fr;
    gap:14px;
    align-items:center;
    box-sizing:border-box;
    border:1px solid rgba(0,0,0,0.08);
}
.match-icon{
    width:68px;
    height:68px;
    border-radius:999px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:33px;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,0.3);
}
.match-title{
    font-size:18px;
    font-weight:900;
    margin-bottom:8px;
}
.match-list{
    margin:0;
    padding:0;
    list-style:none;
    font-size:14px;
    line-height:1.72;
}
.match-list li{
    margin-bottom:2px;
}
.match-title,
.match-list li{
    color:#333333;
}
.match-result{
    margin-top:9px;
    padding-top:8px;
    border-top:1px dashed rgba(255,255,255,0.35);
    font-size:16px;
    font-weight:900;
}
.match-installment{
    background:linear-gradient(135deg,#eaf4ff 0%,#f7fbff 100%);
    border-color:#b9d8ff;
}
.match-installment .match-icon{
    background:linear-gradient(135deg,#79b8ff,#2478dc);
}
.match-installment .match-result{
    color:#0b4f9c;
}
.match-rent{
    background:linear-gradient(135deg,#e8fff4 0%,#f7fffb 100%);
    border-color:#aee8cc;
}
.match-rent .match-icon{
    background:linear-gradient(135deg,#6fe7b2,#12a86f);
}
.match-rent .match-result{
    color:#08784f;
}
.match-lease{
    background:linear-gradient(135deg,#f0ebff 0%,#fbf9ff 100%);
    border-color:#cfc1ff;
}
.match-lease .match-icon{
    background:linear-gradient(135deg,#a68cff,#5d3fd3);
}
.match-lease .match-result{
    color:#5a35c9;
}
html.caprio-dark .match-card{
    border-color:#344255;
    box-shadow:0 8px 22px rgba(0,0,0,0.18);
}
html.caprio-dark .match-installment{
    background:linear-gradient(135deg,#0f3564 0%,#102337 100%);
    border-color:#2f6eac;
}
html.caprio-dark .match-rent{
    background:linear-gradient(135deg,#0c4a3d 0%,#102b26 100%);
    border-color:#1a846b;
}
html.caprio-dark .match-lease{
    background:linear-gradient(135deg,#2d256c 0%,#181d42 100%);
    border-color:#6555c8;
}
html.caprio-dark .match-title,
html.caprio-dark .match-list li{
    color:#ffffff !important;
}
html.caprio-dark .match-installment .match-result{
    color:#9fc7ff !important;
}
html.caprio-dark .match-rent .match-result{
    color:#76f0bd !important;
}
html.caprio-dark .match-lease .match-result{
    color:#b9a7ff !important;
}
@media (max-width:768px){
    .guide-wrap{
        grid-template-columns:1fr;
    }
    .match-card{
        display:block;
        padding:14px;
        margin-top:12px;
    }
    .match-icon{
        display:none;
    }
    .match-title{
        font-size:16px;
        margin-bottom:8px;
    }
    .match-list{
        font-size:13px;
        line-height:1.65;
    }
    .match-result{
        font-size:15px;
    }
}
</style>

<div class="guide-wrap">

<div class="guide-card">
<div class="guide-title">💳 [소유형] 할부 구매</div>
<div class="guide-copy">내 차라는 확실한 자산, 오래도록 변함없이 타고 싶다면?</div>
<div class="guide-subtitle">✅ 할부 체크리스트</div>
<ol class="guide-list">
<li>5~10년 이상 장기 보유할 목적이 확실해요.</li>
<li>취등록세와 같은 초기 목돈을 지출할 여력이 있어요.</li>
<li>명의가 개인 또는 법인 소유인 온전한 자산을 원해요.</li>
</ol>
<div class="reality-box">
<div class="reality-title">💡 현실 체크</div>
<div class="reality-item">📉 <b>집 대출 한도 축소</b> : 내 명의로 할부 대출이 잡히기 때문에, 추후 주택담보대출 한도가 줄어들 수 있어요.</div>
<div class="reality-item">💸 <b>부대 비용 발생</b> : 자동차세·취등록세·보험료 등 지속적인 비용이 발생해요.</div>
<div class="reality-item">🛡️ <b>자산 가치 관리</b> : 사고주의 & 관리를 통해 감가를 최소화하는게 중요해요.</div>
<div class="reality-item">🏢 <b>법인 시 주의</b> : 판매 시 부가세 10%가 발생하니 미리 대비해야해요!</div>
</div>
<div class="match-card match-installment">
<div class="match-icon">💳</div>
<div>
<div class="match-title">🔥 할부는 이런 경우 고민없이!</div>
<ul class="match-list">
<li>✔ 차량가의 30% 이상 초기비용 부담이 가능하고</li>
<li>✔ 5년 이상 장기 보유 예정이며</li>
<li>✔ 사고·감가 리스크가 크게 부담되지 않고</li>
<li>✔ 대출한도 영향이 중요하지 않다면</li>
</ul>
<div class="match-result">→ 할부가 잘 맞아요.</div>
</div>
</div>
</div>

<div class="guide-card">
<div class="guide-title">🚗 [재테크형] 장기렌트</div>
<div class="guide-copy">대출 한도 보호와 차량 관리의 효율성을 동시에!</div>
<div class="guide-subtitle">✅ 렌트 체크리스트</div>
<ol class="guide-list">
<li>추후 주택 마련 등을 위해 대출 한도를 확보해야 해요.</li>
<li>3~5년마다 새로운 차량으로 교체하는 주기를 선호해요.</li>
<li>정비·세금·사고처리 등 번거로운 일은 맡기고 싶어요.</li>
</ol>
<div class="reality-box">
<div class="reality-title">💡 현실 체크</div>
<div class="reality-item">🔓 <b>대출 한도 영향 없음</b> : 렌트사 명의라 개인 대출 한도에 영향이 없어요.</div>
<div class="reality-item">💵 <b>세금 할증 없음</b> : 재산세 등 세금 인상은 걱정하지 않으셔도 괜찮아요.</div>
<div class="reality-item">🚫 <b>보험·사고 기록</b> : 사고 시, 정해진 면책금으로 해결하고 개인 보험 이력에 남지 않아요.</div>
<div class="reality-item">🗓️ <b>관리 비용 최소화</b> : 보험·세금이 모두 월 이용료에 포함되며 추가 비용 부담이 없어요!</div>
</div>
<div class="match-card match-rent">
<div class="match-icon">🚗</div>
<div>
<div class="match-title">🔥 렌트는 이런 경우 고민없이!</div>
<ul class="match-list">
<li>✔ DSR·대출한도 보호가 중요하고</li>
<li>✔ 보험료가 높거나 사고이력이 부담되며</li>
<li>✔ 5년 이하 운행 또는 주기적 신차 교체를 선호하고</li>
<li>✔ 사고·세금·보험 처리를 간편하게 맡기고 싶다면</li>
</ul>
<div class="match-result">→ 장기렌트가 잘 맞아요.</div>
</div>
</div>
</div>

<div class="guide-card">
<div class="guide-title">✨ [이미지형] 리스</div>
<div class="guide-copy">품격은 일반 번호판으로, 초기 비용은 리스로 합리적으로!</div>
<div class="guide-subtitle">✅ 리스 체크리스트</div>
<ol class="guide-list">
<li>취등록세 초기 목돈 지출이 부담스러워요.</li>
<li>하·허·호 대신 일반 번호판을 원해요.</li>
<li>렌트보다 자차와 유사한 만족감을 원해요.</li>
</ol>
<div class="reality-box">
<div class="reality-title">💡 현실 체크</div>
<div class="reality-item">📉 <b>개인 보험요율 유지</b> : 무사고 경력이 길고 보험료가 낮다면 유리할 수 있어요.</div>
<div class="reality-item">✨ <b>일반 번호판</b> : 자가용과 동일한 번호판을 유지해요.</div>
<div class="reality-item">💰 <b>효율적 비용 구성</b> : 자동차세 포함 + 초기비용 부담을 낮출 수 있어요.</div>
<div class="reality-item">💵 <b>세금 인상</b> : 재산세 등 세금 인상은 걱정하지 않으셔도 괜찮아요!</div>
</div>
<div class="match-card match-lease">
<div class="match-icon">✨</div>
<div>
<div class="match-title">🔥 리스는 이런 경우 고민없이!</div>
<ul class="match-list">
<li>✔ 초기비용은 줄이고 싶고</li>
<li>✔ 무사고 경력이 길어 보험료가 낮으며</li>
<li>✔ 할부보다 대출 영향은 줄이고 싶다면</li>
</ul>
<div class="match-result">→ 리스가 잘 맞아요.</div>
</div>
</div>
</div>

</div>
""", unsafe_allow_html=True)
