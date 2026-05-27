import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 불필요한 여백 최소화 및 모바일/패드 캡처 최적화 타이트 CSS
st.markdown("""
    <style>
    .excel-header-blue { background-color: #0b3873; color: white; padding: 4px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px; margin-bottom: 6px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 13px; border: 2px solid #a9d08e; border-radius: 4px; padding: 4px; text-align: center; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 13px; border: 2px solid #f4b084; border-radius: 4px; padding: 4px; text-align: center; }
    .capture-box { border: 2px solid #0b3873; padding: 8px; border-radius: 6px; background-color: #ffffff; margin-bottom: 8px; }
    .stTable { margin-bottom: 0px !important; }
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* 렌트 통합 항목용 강조 스타일 */
    .rent-included { background-color: #f8f9fa; font-weight: bold; color: #0b3873; text-align: center; vertical-align: middle; display: flex; align-items: center; justify-content: center; height: 100%; min-height: 110px; border: 1px solid #dee2e6; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# 기본 데이터 변수 세팅
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 0
residual_rent_pct = 58
cc_text = "1600CC이하"
car_shape = "하이브리드"

# ==========================================
# [LEFT SIDEBAR] 할부 조건 입력창 변경
# ==========================================
st.sidebar.header("📋 할부 조건 설정")
installment_prepaid = st.sidebar.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
installment_rate = st.sidebar.number_input("📈 신용별 할부 금리 (%)", value=5.0, step=0.1, format="%.1f")
insurance_annual = st.sidebar.number_input("🛡️ 고객 연 개인 보험료", value=1000000, step=100000, format="%d")

# ==========================================
# [TOP MAIN] 타사 견적 파싱
# ==========================================
raw_data = st.text_area(
    "📋 타사 렌트 견적 복사 붙여넣기", 
    placeholder="여기에 타사 견적 텍스트를 복사 붙여넣기 하세요.",
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
            elif "잔존" in key: residual_rent_pct = clean_num(val)
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

# ==========================================
# [BACKEND LOGIC] 엑셀 매트릭스 연산
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
# [📸 MAIN VISUAL BOARD] 텍스트 다이어트 캡처 영역
# ==========================================
st.markdown("<hr style='border:1px solid #0b3873; margin-top:2px; margin-bottom:8px;'>", unsafe_allow_html=True)

st.markdown('<div class="capture-box">', unsafe_allow_html=True)
view_col1, view_col2 = st.columns(2)

with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (반납형)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}개월 / {mileage} / 차량가 {car_price:,})")
    
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins - car_sell_value + installment_prepaid
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    sub_col1, sub_col2, sub_col3 = st.columns([1.2, 1, 1])
    with sub_col1:
        st.markdown("""
        | 세부 항목 |
        | :--- |
        | 초기 인도금 |
        | 매월 납입금 |
        | 초기 취등록세 |
        | 자동차세 (총액) |
        | 보험료 (총액) |
        | 만기 중고차 정산 |
        | **월 평균 환산** |
        | **총 투입 비용** |
        """)
    with sub_col2:
        st.markdown(f"""
        | 할부 |
        | :---: |
        | {installment_prepaid:,} |
        | {inst_monthly_pay:,} |
        | {reg_tax:,} |
        | {total_tax:,} |
        | {total_ins:,} |
        | -{car_sell_value:,} |
        | **{int(inst_total_cost_ret/months):,}** |
        | **{inst_total_cost_ret:,}** |
        """)
    with sub_col3:
        st.markdown(f"""
        | 렌트 |
        | :---: |
        | {rent_deposit:,} |
        | {rent_monthly_pay:,} |
        """)
        # 취등록세/세금/보험료/만기정산 구간 셀 병합 효과 구현
        st.markdown('<div class="rent-included">월 렌트료에<br>전부 포함</div>', unsafe_allow_html=True)
        st.markdown(f"""
        | |
        | :---: |
        | **{int(rent_total_cost_ret/months):,}** |
        | **{rent_total_cost_ret:,}** |
        """)
        
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green">🏆 할부 대비 {diff_ret:,} 절감</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 정산이 {abs(diff_ret):,} 우세</div>', unsafe_allow_html=True)

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (인수형)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}개월 / 만기 완전 인수 기준)")
    
    inst_total_cost_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_takeover_tax = int(rent_takeover_price * 0.07)
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    sub_col4, sub_col5, sub_col6 = st.columns([1.2, 1, 1])
    with sub_col4:
        st.markdown("""
        | 세부 항목 |
        | :--- |
        | 초기 인도금 |
        | 매월 납입금 |
        | 초기 취등록세 |
        | 자동차세 (총액) |
        | 보험료 (총액) |
        | 만기 인수금 |
        | 인수 취등록세 (7%) |
        | **월 평균 환산** |
        | **총 투입 비용** |
        """)
    with sub_col5:
        st.markdown(f"""
        | 할부 |
        | :---: |
        | {installment_prepaid:,} |
        | {inst_monthly_pay:,} |
        | {reg_tax:,} |
        | {total_tax:,} |
        | {total_ins:,} |
        | - |
        | - |
        | **{int(inst_total_cost_ins/months):,}** |
        | **{inst_total_cost_ins:,}** |
        """)
    with sub_col6:
        st.markdown(f"""
        | 렌트 |
        | :---: |
        | {rent_deposit:,} |
        | {rent_monthly_pay:,} |
        """)
        # 계약 기간 중 포함 항목 셀 병합 효과
        st.markdown('<div class="rent-included" style="min-height:90px;">월 렌트료에<br>전부 포함</div>', unsafe_allow_html=True)
        st.markdown(f"""
        | |
        | :---: |
        | {rent_takeover_price:,} |
        | {rent_takeover_tax:,} |
        | **{int(rent_total_cost_ins/months):,}** |
        | **{rent_total_cost_ins:,}** |
        """)
        
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green">🏆 할부 대비 {diff_ins:,} 절감</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 인수가 {abs(diff_ins):,} 우세</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 📸 신용/리스크 종합분석 (텍스트 최소화 버전)
st.markdown('<div class="capture-box">', unsafe_allow_html=True)
st.markdown('<div class="excel-header-blue" style="background-color: #264653; margin-bottom:4px;">할부 금융 vs 카프리오 리스크 분석</div>', unsafe_allow_html=True)

st.markdown("""
| 분류 | 평가 항목 | 일반 자동차 할부 금융 | 카프리오 대여 프로그램 |
| :---: | :--- | :--- | :--- |
| **재무** | **금융 한도** | ⚠️ 차량가 전액 부채 인식 (DSR 감소) | 임대 상품 처리 (부채 미인식, 대출 한도 유지) |
| | **세금 변동** | ⚠️ 개인 재산 등록 (건보료, 재산세 인상) | 자산 미등록 (인상 요인 없음) |
| **보험** | **사고 할증** | ⚠️ 사고 시 즉시 개인 보험료 할증 | 단체 요율 고정 (사고 횟수 무관 요율 변동 없음) |
| **리스크**| **감가 방어** | ⚠️ 중고 시세 하락 및 사고 감가 본인 부담 | 만기 처분 리스크 없이 안전하게 반납 가능 |
| **사업자**| **비용 처리** | 최장 8년 소요, 매각 정산 시 세무 복잡 | 5년 내 비용 처리 종결, 세무 깔끔 |
""")
st.markdown('</div>', unsafe_allow_html=True)
