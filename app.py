import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 카프리오 전용 프리미엄 브리핑 CSS 스타일
st.markdown("""
    <style>
    .excel-header-blue { background-color: #0b3873; color: white; padding: 12px; text-align: center; font-weight: bold; font-size: 22px; border-radius: 4px; margin-bottom: 15px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 16px; border: 2px solid #a9d08e; border-radius: 4px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 16px; border: 2px solid #f4b084; border-radius: 4px; }
    .section-title { font-size: 18px; font-weight: bold; color: #0b3873; margin-top: 10px; margin-bottom: 10px; }
    
    /* 캡처 시 깔끔하게 떨어지도록 테이블 스타일 조정 */
    .capture-box { border: 2px solid #0b3873; padding: 20px; border-radius: 8px; background-color: #ffffff; margin-bottom: 30px; }
    .info-tag { background-color: #f2f2f2; padding: 5px 10px; border-radius: 4px; font-size: 14px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [TOP] 영업자 전용 데이터 입력 및 세팅 세션
# ==========================================
st.title("⚙️ 카프리오 영업자 세팅 관리자")
st.caption("견적 텍스트를 넣고 하단의 고객 브리핑 레이아웃을 캡처하여 전달하세요.")

input_col1, input_col2 = st.columns([1.2, 1])

with input_col1:
    st.markdown('<div class="section-title">1. 타사 렌트 견적 복사 붙여넣기</div>', unsafe_allow_html=True)
    raw_data = st.text_area(
        "견적서 텍스트 영역", 
        placeholder="차량명\t기아 카니발...\n차량가\t47,810,000\n개월수\t60\n월납입금\t600,930",
        height=180
    )

# 기본값 데이터베이스 세팅
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 10000000
residual_rent_pct = 58
fuel_type = "하이브리드"  # 일반, 경차, 전기/수소차, 하이브리드, 승합차
cc_input = 1600

# 텍스트 데이터 파싱 연동
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

# --- 자동 매칭 데이터베이스 백엔드 로직 (image_078383 데이터 기준) ---
# 1. 잔존가치(판매 시) 자동 매칭
res_matrix = {
    "1만Km": {24: 78, 36: 70, 48: 63, 60: 56},
    "1.5만Km": {24: 75, 36: 67, 48: 60, 60: 53},
    "2만Km": {24: 72, 36: 64, 48: 57, 60: 50},
    "3만Km": {24: 65, 36: 55, 48: 48, 60: 40}
}
default_res_pct = res_matrix.get(mileage, res_matrix["2만Km"]).get(months, 50)

# 2. CC당 자동차세 계산식 기본 매칭
if cc_input <= 1000: cc_cost = 104
elif cc_input <= 1600: cc_cost = 182
elif cc_input <= 2000: cc_cost = 260
elif cc_input <= 2500: cc_cost = 260
else: cc_cost = 260
default_tax_annual = cc_input * cc_cost if fuel_type != "전기/수소차" else 130000

with input_col2:
    st.markdown('<div class="section-title">2. ⭐ 할부 조건 수기 및 요율 검증</div>', unsafe_allow_html=True)
    installment_prepaid = st.number_input("💵 할부 선납금 (인도금)", value=10000000, step=1000000, format="%d")
    installment_rate = st.number_input("📈 신용별 할부 금리 (%)", value=5.0, step=0.1, format="%.1f")
    residual_sell_pct = st.slider("📉 만기 중고차 예상 잔존율 (%) - 표 기준 자동세팅", min_value=10, max_value=80, value=default_res_pct, step=1)
    insurance_annual = st.number_input("🛡️ 고객 연 개인 보험료 (원)", value=1000000, step=100000, format="%d")
    
    c_tax1, c_tax2 = st.columns(2)
    with c_tax1:
        fuel_type = st.selectbox("유종/형태별 취등록세 구분", ["일반", "경차", "전기/수소차", "하이브리드", "승합차"], index=["일반", "경차", "전기/수소차", "하이브리드", "승합차"].index(fuel_type))
    with c_tax2:
        tax_annual = st.number_input("🚗 연 자동차세 (원)", value=int(default_tax_annual), step=10000, format="%d")

# --- 취등록세 세율 및 감면 한도 연산 (image_078383 4번째 표 기준) ---
base_reg_rate = 0.07
discount = 0
if fuel_type == "경차":
    base_reg_rate = 0.04
    discount = 750000
elif fuel_type == "전기/수소차":
    discount = 1400000
elif fuel_type == "하이브리드":
    discount = 400000
elif fuel_type == "승합차":
    base_reg_rate = 0.05

calculated_reg_tax = int(car_price * base_reg_rate) - discount
reg_tax = max(0, calculated_reg_tax) # 0원 이하로 안 떨어지게 방어

# 할부 금융 원리금 계산
loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
if r > 0:
    inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1))
else:
    inst_monthly_pay = int(loan_amount / months)

total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)
car_sell_value = int(car_price * (residual_sell_pct / 100))
rent_takeover_price = int(car_price * (residual_rent_pct / 100))

# ==========================================
# [BOTTOM 1] 캡처 구역 1: 견적 금액 산출서
# ==========================================
st.markdown("<br><br><br><hr style='border:2px solid #0b3873;'>", unsafe_allow_html=True)
st.subheader("📸 캡처 구역 1: 카프리오 금융 견적 비교서")
st.caption("💡 영업 매니저님들은 이 구역을 박스째로 깔끔하게 캡처하여 고객에게 전송하세요.")

st.markdown('<div class="capture-box">', unsafe_allow_html=True)
view_col1, view_col2 = st.columns(2)

with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (반납형 견적)</div>', unsafe_allow_html=True)
    st.write(f"📊 **모델명:** {car_name}")
    st.write(f"⏱️ **이용조건:** {months}개월 / {mileage} 약정 / 차량가 {car_price:,}원")
    
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins - car_sell_value + installment_prepaid
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    st.markdown(f"""
    | 세부 항목 | 일반 할부 견적 | 카프리오 장기렌트 |
    | :--- | :---: | :---: |
    | **초기 인도금/선납금** | {installment_prepaid:,} 원 | {rent_deposit:,} 원 |
    | **매월 순수 매각 납입금** | {inst_monthly_pay:,} 원 | {rent_monthly_pay:,} 원 |
    | **초기 취등록세 (감면반영)** | {reg_tax:,} 원 | **매달 분납 포함 (0원)** |
    | **보유 기간 자동차세 (총액)** | {total_tax:,} 원 | **매달 분납 포함 (0원)** |
    | **이용 기간 자동차보험료** | {total_ins:,} 원 | **매달 분납 포함 (0원)** |
    | **만기 시 중고차 매각정산** | -{car_sell_value:,} 원 (매각성공 가정) | **감가 감수 없이 반납 완료** |
    | 🧾 **월 평균 환산 전체비용** | **{int(inst_total_cost_ret/months):,} 원** | **{int(rent_total_cost_ret/months):,} 원** |
    | 💰 **이용기간 총 투입 비용** | **{inst_total_cost_ret:,} 원** | **{rent_total_cost_ret:,} 원** |
    """)
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green" style="padding:12px; text-align:center;">🏆 카프리오 반납형 선택 시 일반 할부 대비 {diff_ret:,} 원 더 이득!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:12px; text-align:center;">본 수치는 할부 매각 정산이 총 {abs(diff_ret):,} 원 더 우세합니다.</div>', unsafe_allow_html=True)

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 프로그램 (인수형 견적)</div>', unsafe_allow_html=True)
    st.write(f"📊 **모델명:** {car_name}")
    st.write(f"⏱️ **이용조건:** {months}개월 / 만기 인수형 설정 기준")
    
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
    | **만기 시점 내차 인수비용** | - (할부 종료 시 자동이전) | {rent_takeover_price:,} 원 |
    | **인수 이전 취등록세 (7%)** | - | {rent_takeover_tax:,} 원 |
    | 🧾 **월 평균 환산 전체비용** | **{int(inst_total_cost_ins/months):,} 원** | **{int(rent_total_cost_ins/months):,} 원** |
    | 💰 **인수까지 총 투입 비용** | **{inst_total_cost_ins:,} 원** | **{rent_total_cost_ins:,} 원** |
    """)
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green" style="padding:12px; text-align:center;">🏆 카프리오 인수형 선택 시 일반 할부 대비 {diff_ins:,} 원 더 이득!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red" style="padding:12px; text-align:center;">본 수치는 할부 인수가 총 {abs(diff_ins):,} 원 더 우세합니다.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# [BOTTOM 2] 캡처 구역 2: 신용 및 자산 리스크 비교표
# ==========================================
st.subheader("📸 캡처 구역 2: 재무 신용 및 감가 리스크 종합 비교표")
st.caption("💡 차량 정밀 제어 및 자산 부채 평가 기준입니다. 금액 비교표와 함께 세트로 캡처해 보내세요.")

st.markdown('<div class="capture-box">', unsafe_allow_html=True)
st.markdown('<div class="excel-header-blue" style="background-color: #264653;">할부 상품 vs 카프리오 프로그램 리스크 비교분석</div>', unsafe_allow_html=True)

st.markdown("""
| 분류 | 비교 평가 항목 | 일반 자동차 할부 금융 | 카프리오 대여 프로그램 |
| :---: | :--- | :--- | :--- |
| **재무/신용** | **금융 한도 자산 평가** | ⚠️ **차량가 전액 부채 인식** (DSR 직격탄, 타 대출 한도 감소) |  **임대 상품 처리** (부채 미인식, 대출 한도 영향 無) |
| | **회계 편의성 및 세금** | ⚠️ **개인 재산 등록** (건보료 인상, 재산세 상승 원인) |  **비용 처리 깔끔** (개인 자산 미등록, 인상 요인 無) |
| | **월 납부 방식 구조** | 취등록세, 자동차세, 연간 보험료 등 개별 **별도 납부** | **월 납입금 내 전액 녹아있음** (부가세 포함 완전 케어) |
| **보험 관리** | **자동차 보험료 산정** | 매년 무사고/사고 경력 요율별로 개인 차등 변동 납부 | **단체 요율 고정 적용** (보험료 대폭 절감 효과) |
| | **사고 발생 시 할증** | ⚠️ **사고 시 즉시 보험료 할증** 및 이후 3년간 패널티 유지 |  **몇 번의 사고가 나도 면책금 외 요율 할증 無** |
| **리스크 관리**| **감가 및 면책 제도** | ⚠️ **수리비 전액 본인 부담** 및 사고 이력 감가 리스크 노출 | 면책금(약 30만 원) 지불 시 추가 수리비 및 감가 책임 0원 |
| | **중고차 감가 방어** | ⚠️ 사고 이력이나 시장 트렌드 변화 시 **자산 가치 하락 독박** | 만기 시 처분 리스크 없이 안전하게 **반납 처리 권리 보유** |
| **법인/개인** | **비용 처리 속도** | 법인/개인사업자 매각 정산 시 최장 8년 소요 | **5년 이내 전액 전산 비용 처리** 깔끔하게 완료 |
| **사업자** | **판매 정산 시 세무** | ⚠️ 경차/승합차 제외, 판매 시 **부가세 10% 추가 부담** | 만기 시 세무 리스크 없이 **단순 반납 처리로 종결** |
""")
st.markdown('</div>', unsafe_allow_html=True)

st.caption("카프리오(Capri-o) 영업자 내부 브리핑 지원 시스템 v3.0 (수식 및 정형 지표 싱크 완료)")
