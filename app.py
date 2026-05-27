import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 카프리오 전용 고급스러운 엑셀 비주얼 스타일
st.markdown("""
    <style>
    .excel-header-blue { background-color: #0b3873; color: white; padding: 12px; text-align: center; font-weight: bold; font-size: 22px; border-radius: 4px; margin-bottom: 15px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 16px; border: 2px solid #a9d08e; border-radius: 4px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 16px; border: 2px solid #f4b084; border-radius: 4px; }
    .section-title { font-size: 18px; font-weight: bold; color: #0b3873; margin-top: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [TOP] 영업자 데이터 입력 및 실시간 변수 조정 구역
# ==========================================
st.title("⚙️ 카프리오 영업자 세팅 관리자")
st.caption("견적을 복사해 넣은 뒤, 노란색 수기 항목(할부 조건)을 고객 맞춤형으로 조정해 보세요.")

# 왼쪽/오른쪽으로 나누어 입력 효율 극대화
input_col1, input_col2 = st.columns([1.2, 1])

with input_col1:
    st.markdown('<div class="section-title">1. 타사 렌트 견적 붙여넣기 (텍스트 복사용)</div>', unsafe_allow_html=True)
    raw_data = st.text_area(
        "여기에 견적서 텍스트를 그대로 붙여넣으세요", 
        placeholder="차량명\t기아 카니발...\n차량가\t47,810,000\n개월수\t60\n월납입금\t600,930",
        height=180
    )

# 기본 데이터베이스 세팅 (기본값)
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 10000000  # 렌트용 선납/보증
residual_rent_pct = 58   # 렌트 잔존가치

# 렌트 견적 자동 추출 (붙여넣기 시 작동)
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
            elif "약정거리" in key: mileage = val
            elif "월납입" in key: rent_monthly_pay = clean_num(val)
            elif "선납금" in key or "보증금" in key: rent_deposit = clean_num(val)
            elif "잔존" in key: residual_rent_pct = clean_num(val)

with input_col2:
    st.markdown('<div class="section-title">2. ⭐ 할부 조건 수기 입력 (고객 맞춤형 상담용)</div>', unsafe_allow_html=True)
    
    # 엑셀 시트에서 노란색으로 강조되었던 수기 입력 필수 항목 4가지
    installment_prepaid = st.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
    installment_rate = st.number_input("📈 할부 금리 (%)", value=5.2, step=0.1, format="%.1f")
    residual_sell_pct = st.slider("📉 만기 시 중고차 예상 잔존가치 (%)", min_value=10, max_value=80, value=50, step=5)
    insurance_annual = st.number_input("🛡️ 고객 연 개인 보험료 (원)", value=1000000, step=100000, format="%d")
    
    # 기본 고정 세금 항목 수기 입력
    tax_annual = st.number_input("🚗 연 자동차세 (원)", value=291200, step=10000, format="%d")

# --- 내부 금융 시뮬레이션 계산 수식 ---
reg_tax = int(car_price * 0.07)  # 취등록세 7%

# 할부 원리금 균등상환 계산 (차량가 - 할부 선납금 기준 대출금 산정)
loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
if r > 0:
    inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1))
else:
    inst_monthly_pay = int(loan_amount / months)

# 계약기간 총 합산 비용 연산
total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)
car_sell_value = int(car_price * (residual_sell_pct / 100))  # 할부 만기 내차 처분 시 중고차값
rent_takeover_price = int(car_price * (residual_rent_pct / 100))  # 렌트 만기 인수금

# ==========================================
# [BOTTOM] 고객 브리핑용 실제 연산 시트 구역
# ==========================================
st.markdown("<br><br><br><hr style='border:2px solid #0b3873;'>", unsafe_allow_html=True)
st.subheader("📱 카프리오 상담 브리핑 대시보드")
st.caption("💡 상담 시 여기부터 스크롤을 내려 고객에게 패드나 스마트폰으로 보여주시면 됩니다.")

view_col1, view_col2 = st.columns(2)

# ---- 왼쪽: 반납형 비교 ----
with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (반납형)</div>', unsafe_allow_html=True)
    st.write(f"📊 **모델명:** {car_name}")
    st.write(f"⏱️ **이용기간:** {months}개월 | 🛣️ **약정거리:** {mileage} | 💰 **차량가격:** {car_price:,}원")
    
    # 총비용 연산 (반납형)
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins - car_sell_value + installment_prepaid
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    st.markdown(f"""
    | 비교 항목 | 일반 할부 (수기 조건 반영) | 카프리오 장기렌트 |
    | :--- | :---: | :---: |
    | **초기 선납금** | {installment_prepaid:,} 원 | {rent_deposit:,} 원 |
    | **순수 월 납입금** | {inst_monthly_pay:,} 원 | {rent_monthly_pay:,} 원 |
    | **초기 취등록세 (7%)** | {reg_tax:,} 원 | **포함 (0원)** |
    | **보유 자동차세 (총액)** | {total_tax:,} 원 | **포함 (0원)** |
    | **유지 보험료 (총액)** | {total_ins:,} 원 | **포함 (0원)** |
    | **만기 시 중고차 처리** | -{car_sell_value:,} 원 (매각 손익 반영) | **처분 리스크 없이 반납** |
    | 🧾 **월 평균 환산 비용** | **{int(inst_total_cost_ret/months):,} 원** | **{int(rent_total_cost_ret/months):,} 원** |
    | 💰 **만기까지 총비용** | **{inst_total_cost_ret:,} 원** | **{rent_total_cost_ret:,} 원** |
    """)
    
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green" style="padding:12px; text-align:center;">🏆 카프리오 반납형 선택 시 할부 대비 {diff_ret:,} 원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:12px; text-align:center;">본 조건은 할부 반납 수치가 총 {abs(diff_ret):,} 원 더 낮습니다.</div>', unsafe_allow_html=True)

# ---- 오른쪽: 인수형 비교 ----
with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (인수형)</div>', unsafe_allow_html=True)
    st.write(f"📊 **모델명:** {car_name}")
    st.write(f"⏱️ **이용기간:** {months}개월 | 💸 **만기 렌트 인수금:** {rent_takeover_price:,}원")
    
    # 총비용 연산 (인수형)
    inst_total_cost_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_takeover_tax = int(rent_takeover_price * 0.07)
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    st.markdown(f"""
    | 비교 항목 | 일반 할부 (소유 유지) | 카프리오 완전 인수 |
    | :--- | :---: | :---: |
    | **초기 선납금** | {installment_prepaid:,} 원 | {rent_deposit:,} 원 |
    | **순수 월 납입금** | {inst_monthly_pay:,} 원 | {rent_monthly_pay:,} 원 |
    | **초기 취등록세** | {reg_tax:,} 원 | **포함 (0원)** |
    | **보유 세금/보험료** | {total_tax + total_ins:,} 원 | **포함 (0원)** |
    | **만기 인수 가격** | - (자동 소유권) | {rent_takeover_price:,} 원 |
    | **인수시 취등록세** | - | {rent_takeover_tax:,} 원 |
    | 🧾 **월 평균 환산 비용** | **{int(inst_total_cost_ins/months):,} 원** | **{int(rent_total_cost_ins/months):,} 원** |
    | 💰 **만기까지 총비용** | **{inst_total_cost_ins:,} 원** | **{rent_total_cost_ins:,} 원** |
    """)
    
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green" style="padding:12px; text-align:center;">🏆 카프리오 인수형 선택 시 할부 대비 {diff_ins:,} 원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:12px; text-align:center;">본 조건은 할부 유지가 총 {abs(diff_ins):,} 원 더 낮습니다.</div>', unsafe_allow_html=True)

st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("카프리오(Capri-o) 영업자 내부 브리핑 지원 시스템 v2.5")
