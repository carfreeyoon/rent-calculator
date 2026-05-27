import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 카프리오 전용 프리미엄 브리핑 CSS 스타일 (여백 최소화 및 모바일/패드 캡처 최적화)
st.markdown("""
    <style>
    .excel-header-blue { background-color: #0b3873; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 16px; border-radius: 4px; margin-bottom: 8px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 13px; border: 2px solid #a9d08e; border-radius: 4px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 13px; border: 2px solid #f4b084; border-radius: 4px; }
    
    /* 캡처박스 타이트하게 패딩 조정 */
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

# ==========================================
# [LEFT SIDEBAR] 영업자 조건 제어 컨트롤러 (화면 경제성 확보)
# ==========================================
st.sidebar.header("⚙️ 영업자 조건 설정")

# 1. 할부 금융 기본 입력
installment_prepaid = st.sidebar.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
installment_rate = st.sidebar.number_input("📈 신용별 할부 금리 (%)", value=5.0, step=0.1, format="%.1f")
insurance_annual = st.sidebar.number_input("🛡️ 고객 연 개인 보험료", value=1000000, step=100000, format="%d")

st.sidebar.markdown("---")
st.sidebar.subheader("🚗 엑셀 조건 매칭 (취등록세/세금)")

# 2. 엑셀 수식 완벽 연동을 위한 체크박스 세팅 (중첩 가능 구조)
is_isg_car = st.sidebar.checkbox("🏎️ 경차 요율 적용 (4%)", value=False)
is_van_car = st.sidebar.checkbox("🚌 승합차 요율 적용 (5%)", value=False)

st.sidebar.markdown("**💡 친환경 감가/감면 선택**")
eco_type = st.sidebar.radio("유종 및 배기량 분류 선택", ["일반 내연기관", "하이브리드 (40만 감면)", "전기/수소차 (140만 감면)"], index=1)

# 3. 자동차세 배기량 기준 선택
cc_type = st.sidebar.selectbox("엔진 배기량 기준 (연 자동차세 계산용)", ["1000cc 이하", "1600cc 이하", "2000cc 이하", "2500cc 이하", "3000cc 초과", "전기차 고정세"], index=1)

# ==========================================
# [TOP MAIN] 타사 견적 복사 붙여넣기 (컴팩트 뷰)
# ==========================================
raw_data = st.text_area(
    "📋 타사 렌트 견적 복사 붙여넣기 (텍스트 입력 시 데이터 자동 매칭)", 
    placeholder="차량명\t기아 카니발...\n차량가\t47,810,000\n개월수\t60\n월납입금\t600,930",
    height=90
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

# ==========================================
# [BACKEND LOGIC] 엑셀 수식(MAX, IFS, AND) 1:1 완벽 이식
# ==========================================

# 1. 취등록세 파트 (제공해주신 엑셀 IFS/AND 매트릭스 알고리즘 그대로 이식)
reg_rate = 0.07  # TRUE, ($C$6*0.07) 기본값
reg_discount = 0

if eco_type == "하이브리드 (40만 감면)":
    reg_discount = 400000
elif eco_type == "전기/수소차 (140만 감면)":
    reg_discount = 1400000

if is_van_car:  # E15 <> "" (승합차 체크 시)
    reg_rate = 0.05
    # AND(E15<>"", G14<>"") 또는 AND(E15<>"", I14<>"") 감면액 세팅은 위에서 처리된 요율 유지

elif is_isg_car:  # E14 <> "" (경차 체크 시)
    reg_rate = 0.04
    reg_discount = 750000  # 경차 한도 고정

# 최종 취등록세 연산 = MAX(0, (차량가 * 요율) - 감면액)
reg_tax = max(0, int(car_price * reg_rate) - reg_discount)

# 2. 연 자동차세 파트 (image_078383 데이터 기준 자동화)
if cc_type == "1000cc 이하": tax_annual = 104000
elif cc_type == "1600cc 이하": tax_annual = 291200
elif cc_type == "2000cc 이하": tax_annual = 520000
elif cc_type == "2500cc 이하": tax_annual = 650000
elif cc_type == "3000cc 초과": tax_annual = 780000
else: tax_annual = 130000  # 전기차

# 3. 주행거리별 만기 중고차 잔존율 매칭 (테이블 기준 자동 매칭)
res_matrix = {
    "1만Km": {24: 78, 36: 70, 48: 63, 60: 56},
    "1.5만Km": {24: 75, 36: 67, 48: 60, 60: 53},
    "2만Km": {24: 72, 36: 64, 48: 57, 60: 50},
    "3만Km": {24: 65, 36: 55, 48: 48, 60: 40}
}
residual_sell_pct = res_matrix.get(mileage, res_matrix["2만Km"]).get(months, 50)

# 할부 원리금 균등 금융 연산
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
    | **초기 취등록세 (수식반영)** | {reg_tax:,} 원 | **매달 분납 포함 (0원)** |
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
