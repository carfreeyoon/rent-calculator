import streamlit as st

# 페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="카프리오 견적 계산기", layout="centered")
st.title("🚗 카프리오 할부 vs 렌트 비교 계산기 (2026)")
st.write("영업자용 간편 웹 계산기입니다.")

st.markdown("---")

# [입력 구역]
st.subheader("📌 차량 정보 입력")

# 1. 차량가 및 선납금
col1, col2 = st.columns(2)
with col1:
    car_price = st.number_input("차량 가격 (원)", min_value=0, value=55000000, step=100000)
with col2:
    prepaid_money = st.number_input("선납금 / 보증금 (원)", min_value=0, value=0, step=100000)

# 2. 할부 기간 및 금리
col3, col4 = st.columns(2)
with col3:
    months = st.selectbox("이용 기간 (개월)", [24, 36, 48, 60], index=2)
with col4:
    interest_rate = st.number_input("할부 금리 (%)", min_value=0.0, value=5.5, step=0.1)

# 3. 차종 선택 (자동차세 계산용)
car_type = st.selectbox(
    "차종 / 배기량 선택",
    ["1000cc 이하", "1600cc 이하", "2000cc 이하", "2500cc 이하", "3000cc 초과", "⚡ 전기차"]
)

# 4. 9인승 승합 여부 토글 (부가세 환급)
is_9seater = st.checkbox("💡 법인/사업자 9인승 승합차 혜택 적용 (부가세 환급)")

st.markdown("---")

# [로직 계산 구역]
# 9인승 부가세 환급 적용 시 실질 차량가 다운
if is_9seater:
    actual_car_price = car_price / 1.1
    st.info(f"✨ 9인승 부가세 환급 적용으로 실질 차량가가 {actual_car_price:,.0f}원으로 계산됩니다.")
else:
    actual_car_price = car_price

# 원금 계산 (엑셀의 C6 - G9 로직)
principal = actual_car_price - prepaid_money

# CUMIPMT NUM 오류 방지 로직 (원금이 0 이하일 때 예외 처리)
if principal <= 0:
    monthly_interest = 0.0
    monthly_principal = 0.0
    monthly_installment = 0.0
else:
    # 월리금균등상환 계산법 (엑셀 CUMIPMT 기반의 월평균 이자 산출식)
    r = (interest_rate / 100) / 12
    # 월상환액 = [원금 * r * (1+r)^n] / [(1+r)^n - 1]
    monthly_installment = (principal * r * ((1 + r) ** months)) / (((1 + r) ** months) - 1)
    # 월평균 원금 및 이자 쪼개기
    monthly_principal = principal / months
    monthly_interest = monthly_installment - monthly_principal

# 2026 자동차세 계산 로직 (지방세 포함)
tax_dict = {
    "1000cc 이하": 104000,
    "1600cc 이하": 291200,
    "2000cc 이하": 520000,
    "2500cc 이하": 650000,
    "3000cc 초과": 780000, # 3000cc 기준 최소치
    "⚡ 전기차": 130000
}
annual_car_tax = tax_dict[car_type]

# 취등록세 계산 (7%)
registration_tax = actual_car_price * 0.07

# [결과 출력 구역]
st.subheader("📊 견적 결과 요약")

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric("월 순수 할부금 (원금+이자)", f"{monthly_installment:,.0f} 원")
    st.write(f"└ 월 원금: {monthly_principal:,.0f} 원")
    st.write(f"└ 월평균 이자: {monthly_interest:,.0f} 원")

with col_res2:
    st.metric("초기 취등록세 (7%)", f"{registration_tax:,.0f} 원")
    if car_type == "⚡ 전기차":
        st.metric("연간 자동차세 (고정)", f"{annual_car_tax:,.0f} 원")
    elif car_type == "3000cc 초과":
        st.metric("연간 자동차세 (최소)", f"{annual_car_tax:,.0f} 원", help="3000cc 초과 차량은 배기량에 따라 늘어납니다.")
    else:
        st.metric("연간 자동차세", f"{annual_car_tax:,.0f} 원")

st.markdown("---")
st.caption("카프리오(Capri-o) 영업자 내부 참고용 계산기 프로토타입")