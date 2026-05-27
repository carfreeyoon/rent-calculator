import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 카프리오 전용 프리미엄 브리핑 CSS 스타일
st.markdown("""
    <style>
    .excel-header-blue { background-color: #0b3873; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 16px; border-radius: 4px; margin-bottom: 8px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 13px; border: 2px solid #a9d08e; border-radius: 4px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 13px; border: 2px solid #f4b084; border-radius: 4px; }
    .capture-box { border: 2px solid #0b3873; padding: 10px; border-radius: 6px; background-color: #ffffff; margin-bottom: 12px; }
    .stTable { margin-bottom: 0px !important; }
    div.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 기본 변수 초기화
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 0
residual_rent_pct = 58
cc_text = "1600CC이하"
car_shape = "하이브리드"  # 파싱된 텍스트가 담길 변수 기본값

# ==========================================
# [LEFT SIDEBAR] 영업자 순수 조건 설정 제어
# ==========================================
st.sidebar.header("⚙️ 영업자 조건 설정")
installment_prepaid = st.sidebar.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
installment_rate = st.sidebar.number_input("📈 신용별 할부 금리 (%)", value=5.0, step=0.1, format="%.1f")
insurance_annual = st.sidebar.number_input("🛡️ 고객 연 개인 보험료", value=1000000, step=100000, format="%d")

# ==========================================
# [TOP MAIN] 타사 견적 복사 붙여넣기 및 형태 자동 매칭
# ==========================================
raw_data = st.text_area(
    "📋 타사 렌트 견적 복사 붙여넣기 (형태 항목에 따라 취등록세/세금 전액 자동 연동)", 
    placeholder="차량명\t기아 카니발...\n차량가\t47,810,000\n개월수\t60\n월납입\t600,930\nCC\t1600CC이하\n형태\t하이브리드",
    height=120
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

# 디버깅 및 시각적 직관성을 위한 자동 매칭 인디케이터 표시
st.info(f"🔍 **견적 자동 인식 완료:** [형태: {car_shape}] | [배기량 구분: {cc_text}]")

# ==========================================
# [BACKEND LOGIC] 파싱된 '형태' 기준 엑셀 IFS/AND 수식 1:1 완벽 이식
# ==========================================

# 엑셀 셀 매칭 구조 가상 정의
# E15: 승합 여부 / E14: 경차 여부 / G14: 전기차 여부 / I14: 하이브리드 여부
e15 = "O" if "승합" in car_shape else ""
e14 = "O" if "경차" in car_shape else ""
g14 = "O" if "전기" in car_shape or "수소" in car_shape else ""
i14 = "O" if "하이브리드" in car_shape else ""

# 제공해주신 엑셀 수식 알고리즘 그대로 순차 조건문 처리
# =MAX(0, IFS(AND(E15<>"", G14<>"\"), (($C$6*0.05)-1400000), ...))
if e15 != "" and g14 != "":
    reg_tax_raw = (car_price * 0.05) - 1400000
elif e15 != "" and i14 != "":
    reg_tax_raw = (car_price * 0.05) - 400000
elif e15 != "":
    reg_tax_raw = car_price * 0.05
elif e14 != "":
    reg_tax_raw = (car_price * 0.04) - 750000
elif g14 != "":
    reg_tax_raw = (car_price * 0.07) - 1400000
elif i14 != "":
    reg_tax_raw = (car_price * 0.07) - 400000
else:
    reg_tax_raw = car_price * 0.07

# MAX(0, 연산결과) 적용
reg_tax = max(0, int(reg_tax_raw))

# 자동차세 자동 매칭 (CC 항목 기준)
if "1000" in cc_text: tax_annual = 104000
elif "1600" in cc_text: tax_annual = 291200
elif "2000" in cc_text: tax_annual = 520000
elif "2500" in cc_text: tax_annual = 650000
elif "3000" in cc_text: tax_annual = 780000
else: tax_annual = 130000  # 전기차 등 기본값

# 만기 중고차 예상 잔존율 매칭 (약정거리X이용기간 매트릭스)
res_matrix = {
    "1만Km": {24: 78, 36: 70, 48: 63, 60: 56},
    "1.5만Km": {24: 75, 36: 67, 48: 60, 60: 53},
    "2만Km": {24: 72, 36: 64, 48: 57, 60: 50},
    "3만Km": {24: 65, 36: 55, 48: 48, 60: 40}
}
residual_sell_pct = res_matrix.get(mileage, res_matrix["2만Km"]).get(months, 50)

# 금융 연산 파트
loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)) if r > 0 else int(loan_amount / months)

total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)
car_sell_value = int(car_price * (residual_sell_pct / 100))
rent_takeover_price = int(car_price * (residual_rent_pct / 100))

# ==========================================
# [📸 MAIN VISUAL AREA] 영업자 원클릭 캡처 브리핑 보드
# ==========================================
st.markdown("<hr style='border:1px solid #0b3873; margin-top:5px; margin-bottom:10px;'>", unsafe_allow_html=True)

# 캡처 구역 1: 견적 비용 상세 비교표
st.markdown('<div class="capture-box">', unsafe_allow_html=True)
view_col1, view_col2 = st.columns(2)

with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (반납형 견적)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}개월 / {mileage} / 차량가 {car_price:,}원)")
    
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins - car_sell_value + installment_prepaid
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    st.markdown(f"""
    | 세부 항목 | 일반 할부 견적 | 카프리오 장기렌트 |
    | :--- | :---: | :---: |
    | **초기 인도금/선납금** | {installment_prepaid:,} 원 | {rent_deposit:,} 원 |
    | **매월 순수 매각 납입금** | {inst_monthly_pay:,} 원 | {rent_monthly_pay:,} 원 |
    | **초기 취등록세 (자동인식)** | {reg_tax:,} 원 | **매달 분납 포함 (0원)** |
    | **보유 세금/보험료 (총액)** | {total_tax + total_ins:,} 원 | **매달 분납 포함 (0원)** |
    | **만기 시 중고차 매각정산** | -{car_sell_value:,} 원 | **감가 리스크 없이 반납** |
    | 🧾 **월 평균 환산 비용** | **{int(inst_total_cost_ret/months):,} 원** | **{int(rent_total_cost_ret/months):,} 원** |
    | 💰 **이용기간 총 투입 비용** | **{inst_total_cost_ret:,} 원** | **{rent_total_cost_ret:,} 원** |
    """)
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green" style="padding:6px; text-align:center;">🏆 카프리오 반납형 선택 시 할부 대비 {diff_ret:,} 원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:6px; text-align:center;">할부 매각 정산이 총 {abs(diff_ret):,} 원 더 우세합니다.</div>', unsafe_allow_html=True)

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (인수형 견적)</div>', unsafe_allow_html=True)
    st.caption(f"🚘 **{car_name}** ({months}개월 / 만기 완전 인수형 세팅 기준)")
    
    inst_total_cost_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_takeover_tax = int(rent_takeover_price * 0.07)
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    st.markdown(f"""
    | 세부 항목 | 일반 할부 (소유 유지) | 카프리오 완전 인수형 |
    | :--- | :---: | :---: |
    | **초기 인도금/선납금** | {installment_prepaid:,} 원 | {rent_deposit:,} 원 |
    | **매월 순수 계약 납입금** | {inst_monthly_pay:,} 원 | {rent_monthly_pay:,} 원 |
    | **초기 취등록세 비용** | {reg_tax:,} 원 | **계약 중 포함 (0원)** |
    | **보유 세금/보험료 (총액)** | {total_tax + total_ins:,} 원 | **계약 중 포함 (0원)** |
    | **만기 시점 내차 인수비용** | - (할부 만기 이전) | {rent_takeover_price:,} 원 |
    | **인수 전기 취등록세 (7%)** | - | {rent_takeover_tax:,} 원 |
    | 🧾 **월 평균 환산 비용** | **{int(inst_total_cost_ins/months):,} 원** | **{int(rent_total_cost_ins/months):,} 원** |
    | 💰 **인수까지 총 투입 비용** | **{inst_total_cost_ins:,} 원** | **{rent_total_cost_ins:,} 원** |
    """)
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green" style="padding:6px; text-align:center;">🏆 카프리오 인수형 선택 시 할부 대비 {diff_ins:,} 원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:6px; text-align:center;">할부 인수가 총 {abs(diff_ins):,} 원 더 우세합니다.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 캡처 구역 2: 신용 및 자산 리스크 비교표
st.markdown('<div class="capture-box">', unsafe_allow_html=True)
st.markdown('<div class="excel-header-blue" style="background-color: #264653; margin-bottom:4px;">할부 금융 vs 카프리오 프로그램 신용·리스크 종합 분석</div>', unsafe_allow_html=True)

st.markdown("""
| 분류 | 비교 평가 항목 | 일반 자동차 할부 금융 | 카프리오 대여 프로그램 |
| :---: | :--- | :--- | :--- |
| **재무/신용** | **금융 한도 자산 평가** | ⚠️ **차량가 전액 부채 인식** (DSR 감소, 신용 영향) | **임대 상품 처리** (부채 미인식, 대출 한도 유지) |
| | **회계 편의 및 세금** | ⚠️ **개인 재산 등록** (건보료 인상, 재산세 변동) | **비용 처리 깔끔** (자산 미등록, 인상 요인 없음) |
| | **월 납부 관리 구조** | 취등록세, 자동차세, 연 보험료 등 개별 **분할 납부** | **월 납입금 내 전액 포함** (부가세 포함 종합 완료) |
| **보험 관리** | **사고 발생 시 요율** | ⚠️ **사고 시 즉시 개인 보험료 할증** 및 장기 패널티 | **단체 요율 고정** (사고 횟수 무관 면책금 외 할증 무) |
| **리스크 관리**| **감가 및 정산 방어** | ⚠️ 중고 시세 폭락 및 사고 이력 감가 **본인 독박** | 만기 시 처분 리스크 없이 안전한 **반납 처리 권리** |
| **사업자** | **법인 비용 정산 세무** | ⚠️ 판매 정산 시 세무 복잡, **부가세 10% 추가 부담** | 법인 5년 내 비용 처리 종결, 세무 깔끔 |
""")
st.markdown('</div>', unsafe_allow_html=True)
