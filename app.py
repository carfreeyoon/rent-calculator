import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 불필요한 라인 제거 및 완벽 고정형 CSS 스타일
st.markdown("""
    <style>
    /* 상하단 여백 최소화 */
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* 타이틀 및 컨테이너 박스 */
    .excel-header-blue { background-color: #0b3873; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px; margin-bottom: 10px; }
    .capture-box { border: 2px solid #0b3873; padding: 12px; border-radius: 6px; background-color: #ffffff; margin-bottom: 10px; }
    
    /* 결과 배너 */
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 6px; text-align: center; margin-top: 10px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 6px; text-align: center; margin-top: 10px; }
    
    /* 절대 깨지지 않는 순수 HTML 테이블 스타일 */
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #f2f2f2; font-weight: bold; padding: 6px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 6px; border: 1px solid #dee2e6; height: 32px; }
    .bg-light { background-color: #f8f9fa; }
    .font-bold { font-weight: bold; }
    .text-blue { color: #0b3873; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 기본 데이터 변수 초기 세팅
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 0
residual_rent_pct = 58  # 기본 렌트 잔존가치
cc_text = "1600CC이하"
car_shape = "하이브리드"

# ==========================================
# [LEFT SIDEBAR] 할부 및 렌트 잔가 조건 설정
# ==========================================
st.sidebar.header("📋 할부 조건 설정")
installment_prepaid = st.sidebar.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
installment_rate = st.sidebar.number_input("📈 신용별 할부 금리 (%)", value=5.0, step=0.1, format="%.1f")
insurance_annual = st.sidebar.number_input("🛡️ 고객 연 개인 보험료", value=1000000, step=100000, format="%d")

# 누락되었던 렌트 잔존가치 수동 조절 창 추가 (텍스트 파싱과 연동)
residual_rent_pct = st.sidebar.number_input("📉 할 잔존가치 (%)", value=residual_rent_pct, min_value=0, max_value=100, step=1)

# ==========================================
# [TOP MAIN] 타사 견적 파싱 구역
# ==========================================
raw_data = st.text_area(
    "📋 타사 렌트 견적 복사 붙여넣기", 
    placeholder="여기에 견적 텍스트를 복사 붙여넣기 하세요.",
    height=80
)

if raw_data:
    lines = raw_data.strip().split('\n')
    for line in lines:
        parts = line.split('\t') if '\t' in line else (line.split(':') if ':' in line else line.split())
        if len(parts) >= 2:
            key = parts[0].strip()
            val = "".join(parts[1:]).strip()
            def clean_num(v): return int("".join(filter(str.isdigit, v))) if any(char.isdigit() for char in v) else 0
            
            if "차량명" in key: car_name = val
            elif "차량가" in key: car_price = clean_num(val)
            elif "개월수" in key: months = clean_num(val)
            elif "약정거리" in key: mileage = val.replace(" ", "")
            elif "월납입" in key: rent_monthly_pay = clean_num(val)
            elif "선납금" in key or "보증금" in key: rent_deposit = clean_num(val)
            elif "잔존" in key: residual_rent_pct = clean_num(val)  # 파싱 시 사이드바 값도 자동 변경됨
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

# ==========================================
# [BACKEND LOGIC] 내부 엑셀 매트릭스 연산
# ==========================================
e15 = "O" if "승합" in car_shape else ""
e14 = "O" if "경차" in car_shape else ""
g14 = "O" if "전기" in car_shape or "수소" in car_shape else ""
i14 = "O" if "하이브리드" in car_shape else ""

if e15 != "" and g14 != "": reg_tax_raw = (car_price * 0.05) - 1400000
elif e15 != "" and i14 != "": reg_tax_raw = (car_price * 0.05) - 400000
elif e15 != "": reg_tax_raw = car_price * 0.05
elif e14 != "": reg_tax_raw = (car_price * 0.04) - 750000
elif g14 != "": reg_tax_raw = (car_price * 0.07) - 1400000
elif i14 != "": reg_tax_raw = (car_price * 0.07) - 400000
else: reg_tax_raw = car_price * 0.07

reg_tax = max(0, int(reg_tax_raw))

if "1000" in cc_text: tax_annual = 104000
elif "1600" in cc_text: tax_annual = 291200
elif "2000" in cc_text: tax_annual = 520000
elif "2500" in cc_text: tax_annual = 650000
elif "3000" in cc_text: tax_annual = 780000
else: tax_annual = 130000

res_matrix = {
    "1만Km": {24: 78, 36: 70, 48: 63, 60: 56},
    "1.5만Km": {24: 75, 36: 67, 48: 60, 60: 53},
    "2만Km": {24: 72, 36: 64, 48: 57, 60: 50},
    "3만Km": {24: 65, 36: 55, 48: 48, 60: 40}
}
residual_sell_pct = res_matrix.get(mileage, res_matrix["2만Km"]).get(months, 50)

loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)) if r > 0 else int(loan_amount / months)

total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)
car_sell_value = int(car_price * (residual_sell_pct / 100))
rent_takeover_price = int(car_price * (residual_rent_pct / 100))

# ==========================================
# [📸 MAIN VISUAL BOARD] 양대 비교 테이블 출력 (공백 박스 제거 완료)
# ==========================================
view_col1, view_col2 = st.columns(2)

# 1. 반납형 테이블 구역
with view_col1:
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    st.markdown('<div class="excel-header-blue">렌트 (반납형)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}m / {mileage} / 차량가 {car_price:,})")
    
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins - car_sell_value + installment_prepaid
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    html_ret = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">구분</th><th style="width:33%;">할부</th><th style="width:33%;">렌트</th></tr>
        <tr><td>초기 인도금</td><td>{installment_prepaid:,}</td><td>{rent_deposit:,}</td></tr>
        <tr><td>매월 납입금</td><td>{inst_monthly_pay:,}</td><td>{rent_monthly_pay:,}</td></tr>
        <tr><td>초기 취등록세</td><td>{reg_tax:,}</td><td rowspan="4" class="bg-light text-blue">월 렌트료<br>전부 포함</td></tr>
        <tr><td>자동차세 (총액)</td><td>{total_tax:,}</td></tr>
        <tr><td>보험료 (총액)</td><td>{total_ins:,}</td></tr>
        <tr><td>만기 중고차 정산</td><td>-{car_sell_value:,}</td></tr>
        <tr class="bg-light font-bold"><td>월 평균 환산</td><td>{int(inst_total_cost_ret/months):,}</td><td>{int(rent_total_cost_ret/months):,}</td></tr>
        <tr class="bg-light font-bold"><td>총 투입 비용</td><td>{inst_total_cost_ret:,}</td><td>{rent_total_cost_ret:,}</td></tr>
    </table>
    """
    st.markdown(html_ret, unsafe_allow_html=True)
    
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green">🏆 할부 대비 {diff_ret:,} 절감</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 정산이 {abs(diff_ret):,} 우세</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 인수형 테이블 구역
with view_col2:
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    st.markdown('<div class="excel-header-blue">렌트 (인수형)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}m / 만기 완전 인수 기준)")
    
    inst_total_cost_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_takeover_tax = int(rent_takeover_price * 0.07)
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    html_ins = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">구분</th><th style="width:33%;">할부</th><th style="width:33%;">렌트</th></tr>
        <tr><td>초기 인도금</td><td>{installment_prepaid:,}</td><td>{rent_deposit:,}</td></tr>
        <tr><td>매월 납입금</td><td>{inst_monthly_pay:,}</td><td>{rent_monthly_pay:,}</td></tr>
        <tr><td>초기 취등록세</td><td>{reg_tax:,}</td><td rowspan="3" class="bg-light text-blue">월 렌트료<br>전부 포함</td></tr>
        <tr><td>자동차세 (총액)</td><td>{total_tax:,}</td></tr>
        <tr><td>보험료 (총액)</td><td>{total_ins:,}</td></tr>
        <tr><td>만기 인수금</td><td>-</td><td>{rent_takeover_price:,}</td></tr>
        <tr><td>인수 취등록세 (7%)</td><td>-</td><td>{rent_takeover_tax:,}</td></tr>
        <tr class="bg-light font-bold"><td>월 평균 환산</td><td>{int(inst_total_cost_ins/months):,}</td><td>{int(rent_total_cost_ins/months):,}</td></tr>
        <tr class="bg-light font-bold"><td>총 투입 비용</td><td>{inst_total_cost_ins:,}</td><td>{rent_total_cost_ins:,}</td></tr>
    </table>
    """
    st.markdown(html_ins, unsafe_allow_html=True)
    
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green">🏆 할부 대비 {diff_ins:,} 절감</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 인수가 {abs(diff_ins):,} 우세</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 신용/리스크 종합분석 (텍스트 간소화 버전)
st.markdown('<div class="capture-box">', unsafe_allow_html=True)
st.markdown('<div class="excel-header-blue" style="background-color: #264653; margin-bottom:8px;">할부 vs 렌트 리스크 분석</div>', unsafe_allow_html=True)

st.markdown("""
| 분류 | 평가 항목 | 일반 자동차 할부 금융 | 카프리오 대여 프로그램 |
| :---: | :--- | :--- | :--- |
| **재무** | **금융 한도** | ⚠️ 차량가 전액 부채 인식 (DSR 감소) | 임대 상품 처리 (대출 한도 유지) |
| | **세금 변동** | ⚠️ 개인 재산 등록 (건보료, 재산세 인상) | 자산 미등록 (인상 요인 없음) |
| **보험** | **사고 할증** | ⚠️ 사고 시 즉시 개인 보험료 할증 | 단체 요율 고정 (요율 변동 없음) |
| **리스크**| **감가 방어** | ⚠️ 중고 시세 하락, 사고 감가 본인 부담 | 처분 리스크 없이 안전하게 반납 |
| **사업자**| **비용 처리** | 최장 8년 소요, 매각 시 세무 복잡 | 5년 내 비용 처리 종결, 세무 깔끔 |
""")
st.markdown('</div>', unsafe_allow_html=True)
