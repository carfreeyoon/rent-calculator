import streamlit as st
import streamlit.components.v1 as components
import re
import json
import base64

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
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


def encode_share_data(data):
    json_text = json.dumps(data, ensure_ascii=False)
    return base64.urlsafe_b64encode(json_text.encode("utf-8")).decode("utf-8")

def decode_share_data(encoded_text):
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
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    
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

    html.caprio-dark .td-highlight {
        background-color: #253b24 !important;
        color: #c9f5bf !important;
        font-weight: 800 !important;
    }

    html.caprio-dark .rent-highlight {
        background-color: #253b24 !important;
        color: #c9f5bf !important;
        font-weight: 800 !important;
    }

    /* 할부·렌트·리스 비교표 - class 기반 다크모드 */
    html.caprio-dark .compare-cat{
        background:#0b3873 !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-item{
        background:#22364d !important;
        color:#ffffff !important;
        font-weight:700 !important;
    }

    html.caprio-dark .compare-legal{
        background:#4f741a !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-summary-table td:not([style*="background:#0b3873"]):not([style*="background: #0b3873"]):not([style*="background:#6b8e23"]):not([style*="background: #6b8e23"]):not([style*="background:#ddebf7"]):not([style*="background: #ddebf7"]) {
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
    }


    /* 다크모드 - 할부·렌트·리스 비교표 셀 클래스 기반 최종 보정 */
    html.caprio-dark .compare-summary-table .compare-cat {
        background:#144b96 !important;
        background-color:#144b96 !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-summary-table .compare-legal {
        background:#6d9a2e !important;
        background-color:#6d9a2e !important;
        color:#ffffff !important;
        font-weight:900 !important;
    }

    html.caprio-dark .compare-summary-table .compare-item {
        background:#2b4461 !important;
        background-color:#2b4461 !important;
        color:#ffffff !important;
        font-weight:800 !important;
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
    encoded = encode_share_data(share_data)
    return f"https://carfreeoh-rentcalculator.streamlit.app/?view=client&q={encoded}"
    
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

    # ==========================================
    # [TOP MAIN] 타사 견적 파싱 구역
    # ==========================================
    if st.session_state.pending_quote_input is not None:
        st.session_state.raw_quote_input = st.session_state.pending_quote_input
        st.session_state.pending_quote_input = None

    raw_data = st.text_area(
        "📋 렌트 견적 복사 붙여넣기",
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
                    "share_url": make_share_url()
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
        <table class="common-table">
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
<td>O</td>
<td>X</td>
<td>O</td>
</tr>
<tr>
<td class="compare-item">차량 자산 인식</td>
<td>O</td>
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
<td>면책금 중심</td>
<td>감가·보험료 영향</td>
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
<td>X</td>
<td>O</td>
<td>X</td>
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
<br><span style="color:red; font-size:10px;">(경차, 승합차 제외)</span>
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
@media (max-width:768px){
    .guide-wrap{
        grid-template-columns:1fr;
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
<div class="reality-item">🛡️ <b>자산 가치 관리</b> : 사고주의 & 관리를 통해 감가를 최소화하는게 중요해요!</div>
<div class="reality-item">🏢 <b>법인 시 주의</b> : 판매 시 부가세 10%가 발생하니 미리 대비해야해요!</div>
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
<div class="reality-item">🚫 <b>보험·사고 기록</b> : 사고 시, 정해진 면책금으로 해결하고 개인 보험 이력에 남지 않아요.</div>
<div class="reality-item">🗓️ <b>관리 비용 최소화</b> : 보험·세금이 모두 월 이용료에 포함되며 추가 비용 부담이 없어요!</div>
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
<div class="reality-item">📉 <b>개인 보험요율 유지</b> : 개인의 낮다면? 보험료를 그대로 적용받아 수입차 운용 시 경제적이에요.</div>
<div class="reality-item">✨ <b>일반 번호판</b> : 자가용과 동일한 번호판을 유지해요.</div>
<div class="reality-item">💰 <b>효율적 비용 구성</b> : 자동차세 포함 + 초기비용 부담을 낮출 수 있어요.</div>
<div class="reality-item">💵 <b>세금 인상</b> : 재산세 등 세금 인상은 걱정하지 않으셔도 괜찮아요!</div>
</div>
</div>

</div>
""", unsafe_allow_html=True)
