import streamlit as st
import re

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

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
    </style>
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
car_shape = "하이브리드"
installment_resale_pct = 50 # 할부 잔존가치(매각율) 기본값
rent_resale_pct = 58       # 렌트 고정 잔존가치(기본값 58%)

# ==========================================
# [SIDEBAR] 조건 설정 구역
# ==========================================
st.sidebar.header("📋 조건 설정")
is_corporate = st.sidebar.checkbox("🏢 법인 고객 여부", value=False)
installment_prepaid = st.sidebar.number_input("💵 할부 선납금", value=10000000, step=1000000)
installment_rate = st.sidebar.number_input("📈 할부 금리 (%)", value=5.0, step=0.1)
insurance_annual = st.sidebar.number_input("🛡️ 연 개인 보험료", value=1000000, step=100000)
st.sidebar.markdown("---")
installment_resale_pct = st.sidebar.number_input("📉 할부 잔존가치 (%)", value=installment_resale_pct, min_value=0, max_value=100, step=1)

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

    cc_match = re.search(r"([0-9,]+)cc", text)
    fuel_line = ""
    for line in lines_clean:
        if "출시" in line and "·" in line:
            fuel_line = line
            break

    if "전기" in fuel_line and not cc_match:
        cc_val = "전기차"
    elif cc_match:
        cc_num = int(only_num(cc_match.group(1)))
        if cc_num <= 1000:
            cc_val = "1000CC이하"
        elif cc_num <= 1600:
            cc_val = "1600CC이하"
        elif cc_num <= 2000:
            cc_val = "2000CC이하"
        elif cc_num <= 2500:
            cc_val = "2500CC이하"
        else:
            cc_val = "3000CC초과"
    else:
        cc_val = ""

    if "하이브리드" in car_name_val or "하이브리드" in fuel_line:
        shape_val = "하이브리드"
    elif "전기" in fuel_line and not cc_match:
        shape_val = "전기"
    elif "경차" in car_name_val:
        shape_val = "경차"
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
형태\t{shape_val}"""

# ==========================================
# [TOP MAIN] 타사 견적 파싱 구역
# ==========================================
raw_data = st.text_area("📋 타사 렌트 견적 복사 붙여넣기", placeholder="견적 텍스트를 입력하세요.", height=80)

if raw_data:
    parsed_data = auto_convert_quote(raw_data)
    lines = parsed_data.strip().split('\n')
    for line in lines:
        parts = line.split('\t') if '\t' in line else (line.split(':') if ':' in line else line.split())
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
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

st.sidebar.markdown(
    '<div style="font-size:14px; font-weight:400; color:#262730;">📉 렌트 고정 잔존가치 (%)</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(f"""
<div style="background-color:white; padding:9px 13px; border-radius:8px; font-size:14px; color:#111; height:38px; display:flex; align-items:center;">
{rent_resale_pct:g}
</div>
""", unsafe_allow_html=True)

# ==========================================
# [BACKEND] 연산 로직
# ==========================================
e15 = "O" if "승합" in car_shape else ""
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
corporate_discount = 0.9 if (is_corporate and car_shape != "경차" and car_shape != "승합") else 1.0
car_sell_value = int(car_price * (installment_resale_pct / 100) * corporate_discount)

# 렌트 고정 잔존가치 산출 (수정: 렌트 고정값 58% 사용)
rent_takeover_price = int(car_price * (rent_resale_pct / 100))

if e15 != "" and g14 != "": rent_takeover_tax_raw = (rent_takeover_price * 0.05) - 1400000
elif e15 != "" and i14 != "": rent_takeover_tax_raw = (rent_takeover_price * 0.05) - 400000
elif e15 != "": rent_takeover_tax_raw = rent_takeover_price * 0.05
elif e14 != "": rent_takeover_tax_raw = (rent_takeover_price * 0.04) - 750000
elif g14 != "": rent_takeover_tax_raw = (rent_takeover_price * 0.07) - 1400000
elif i14 != "": rent_takeover_tax_raw = (rent_takeover_price * 0.07) - 400000
else: rent_takeover_tax_raw = rent_takeover_price * 0.07

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

reg_general = "td-highlight" if car_shape == "일반" else ""
reg_light = "td-highlight" if "경차" in car_shape else ""
reg_ev = "td-highlight" if "전기" in car_shape or "수소" in car_shape else ""
reg_hybrid = "td-highlight" if "하이브리드" in car_shape else ""
reg_van = "td-highlight" if "승합" in car_shape else ""

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
                    <td class="font-bold" style="text-align:left; padding-left:10px;">{car_name}</td>
                    <td style="color:gray;">{car_option}</td>
                    <td class="font-bold" style="color:#111;">{car_price:,} 원</td>
                    <td>{months} 개월</td>
                    <td>{mileage}</td>
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
        <tr><td class="font-bold">월납입금<br><span style="color:red; font-size:10px;">(선납금 제외)</span></td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
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
        <tr><td class="font-bold">월납입금<br><span style="color:red; font-size:10px;">(선납금 제외)</span></td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
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
**■ 예상잔존가치(주행×개월수)** 
<span style="color:red; font-size:10px;">*가솔린 기준</span>
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
        <tr class="{reg_van}"><td>승합차</td><td>5%</td><td>-</td></tr>
    </table>
    """, unsafe_allow_html=True)


st.write("")
st.markdown('<div class="excel-header-gray" style="width:55%;">🚗 할부 · 렌트 비교표</div>', unsafe_allow_html=True)

st.markdown("""
<table class="matrix-table" style="width:55%; font-size:13px;">
<tr>
<th style="width:12%;">분류</th>
<th style="width:18%;">항목</th>
<th style="width:35%;">할부</th>
<th style="width:35%;">렌트</th>
</tr>
<tr>
<td style="background:#0b3873;color:white;font-weight:bold;">번호판</td>
<td style="background:#ddebf7;font-weight:bold;">번호판</td>
<td>일반번호판</td>
<td>하·허·호</td>
</tr>
<tr>
<td rowspan="2" style="background:#0b3873;color:white;font-weight:bold;">재무/신용</td>
<td style="background:#ddebf7;font-weight:bold;">금융·부채 영향</td>
<td>대출한도(DSR) 영향 / 세금 인상 O</td>
<td>영향 X</td>
</tr>
<tr>
<td style="background:#ddebf7;font-weight:bold;">차량 명의·자산</td>
<td>본인 명의·자산</td>
<td>렌트사 명의</td>
</tr>
<tr>
<td rowspan="2" style="background:#0b3873;color:white;font-weight:bold;">비용</td>
<td style="background:#ddebf7;font-weight:bold;">세금·보험 납부</td>
<td>취등록세·자동차세·보험 별도 납부</td>
<td>월납입 내 포함</td>
</tr>
<tr>
<td style="background:#ddebf7;font-weight:bold;">초기비용</td>
<td>차량가·취등록세 부담</td>
<td>선택 가능</td>
</tr>
<tr>
<td rowspan="2" style="background:#0b3873;color:white;font-weight:bold;">보험·사고</td>
<td style="background:#ddebf7;font-weight:bold;">보험·사고 처리</td>
<td>직접 가입·직접 처리</td>
<td>보험 포함·사고처리 지원</td>
</tr>
<tr>
<td style="background:#ddebf7;font-weight:bold;">사고 비용·리스크</td>
<td>수리비·감가 부담</td>
<td>면책금 중심</td>
</tr>
<tr>
<td style="background:#0b3873;color:white;font-weight:bold;">관리</td>
<td style="background:#ddebf7;font-weight:bold;">차량 관리</td>
<td>직접 관리</td>
<td>정비 포함 선택 가능</td>
</tr>
<tr>
<td rowspan="2" style="background:#6b8e23;color:white;font-weight:bold;">법인</td>
<td style="background:#ddebf7;font-weight:bold;">비용처리</td>
<td>최장 8년 소요</td>
<td>납입기간 내 100% 비용처리</td>
</tr>
<tr>
<td style="background:#ddebf7;font-weight:bold;">판매 시</td>
<td>경차·승합차 제외 판매 시 부가세 10% 부담</td>
<td>반납 처리</td>
</tr>
</table>
""", unsafe_allow_html=True)
