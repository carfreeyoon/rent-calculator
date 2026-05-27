import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 레이아웃 완벽 정렬 및 불필요한 공백 제거용 CSS
st.markdown("""
    <style>
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .common-info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .common-table { width: 100%; border-collapse: collapse; background-color: #ffffff; text-align: center; font-size: 13px; }
    .common-table th { background-color: #f1f3f5; color: #0b3873; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .common-table td { padding: 8px; border: 1px solid #dee2e6; color: #333333; }
    .excel-header-blue { background-color: #0b3873; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px 4px 0 0; }
    .excel-header-gray { background-color: #5a5a5a; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 10px; }
    .capture-box { border: 2px solid #0b3873; padding: 15px; border-radius: 0 0 6px 6px; background-color: #ffffff; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 8px; border: 1px solid #dee2e6; height: 40px; }
    .matrix-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-bottom: 10px; }
    .matrix-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 5px; border: 1px solid #dee2e6; }
    .matrix-table td { padding: 5px; border: 1px solid #dee2e6; }
    .td-highlight { background-color: #e2efda; font-weight: bold; }
    .bg-light { background-color: #f8f9fa; }
    .text-blue { color: #0b3873; font-weight: bold; }
    .font-bold { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 초기값 설정
car_name = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스"
car_option = "-"
car_price = 47810000
months = 60
mileage = "2만Km"
rent_monthly_pay = 600930
rent_deposit = 0
rent_takeover_pct = 58 # 인수형 잔존가치(고정값/렌트사 기준)
cc_text = "1600CC이하"
car_shape = "하이브리드"

# 사이드바
st.sidebar.header("📋 조건 설정")
is_corporate = st.sidebar.checkbox("🏢 법인 고객 여부", value=False)
installment_prepaid = st.sidebar.number_input("💵 할부 선납금", value=10000000, step=1000000)
installment_rate = st.sidebar.number_input("📈 할부 금리 (%)", value=5.0, step=0.1)
insurance_annual = st.sidebar.number_input("🛡️ 연 개인 보험료", value=1000000, step=100000)
# 변경된 부분: 할부 만기 매각율로 명칭 변경 및 분리
installment_resale_pct = st.sidebar.number_input("📉 할부 만기 매각 예상률 (%)", value=58, min_value=0, max_value=100, step=1)

raw_data = st.text_area("📋 타사 렌트 견적 복사 붙여넣기", placeholder="견적 텍스트를 입력하세요.", height=80)
if raw_data:
    lines = raw_data.strip().split('\n')
    for line in lines:
        parts = line.split('\t') if '\t' in line else (line.split(':') if ':' in line else line.split())
        if len(parts) >= 2:
            key = parts[0].strip(); val = "".join(parts[1:]).strip()
            def clean_num(v): return int("".join(filter(str.isdigit, v))) if any(char.isdigit() for char in v) else 0
            if "차량명" in key: car_name = val
            elif "옵션" in key: car_option = val
            elif "차량가" in key: car_price = clean_num(val)
            elif "개월수" in key: months = clean_num(val)
            elif "약정거리" in key: mileage = val.replace(" ", "")
            elif "월납입" in key: rent_monthly_pay = clean_num(val)
            elif "선납금" in key or "보증금" in key: rent_deposit = clean_num(val)
            elif "잔존" in key: rent_takeover_pct = clean_num(val)
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

# 연산 로직
reg_tax = max(0, int((car_price * 0.05) - 400000 if '하이브리드' in car_shape else (car_price * 0.07)))
tax_annual = 291200 if "1600" in cc_text else 520000
loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)) if r > 0 else int(loan_amount / months)

total_ins = int((insurance_annual / 12) * months); total_tax = int((tax_annual / 12) * months)
corporate_discount = 0.9 if (is_corporate and car_shape not in ["경차", "승합"]) else 1.0
# 할부 매각액 계산: 사용자 입력값 사용
car_sell_value = int(car_price * (installment_resale_pct / 100) * corporate_discount)
# 인수형 계산: 사이드바 입력값과 별도로 렌트 데이터값 사용
rent_takeover_price = int(car_price * (rent_takeover_pct / 100))
rent_takeover_tax = int(rent_takeover_price * 0.07)

# UI 출력
st.markdown(f"""
    <div class="common-info-box">
        <div style="font-size:15px; font-weight:bold; margin-bottom:10px; color:#0b3873;">🚘 비교 차량 공통 조건</div>
        <table class="common-table">
            <thead><tr><th>차량명</th><th>옵션</th><th>차량가격</th><th>계약기간</th><th>약정거리</th></tr></thead>
            <tbody><tr><td class="font-bold" style="text-align:left; padding-left:10px;">{car_name}</td><td>{car_option}</td><td class="font-bold" style="color:#0b3873;">{car_price:,} 원</td><td>{months} 개월</td><td>{mileage}</td></tr></tbody>
        </table>
    </div>
""", unsafe_allow_html=True)

view_col1, view_col2 = st.columns(2)
with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (반납형)</div>', unsafe_allow_html=True)
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    inst_total = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid - car_sell_value
    rent_total = (rent_monthly_pay * months) + rent_deposit
    diff = inst_total - rent_total
    st.markdown(f"""<table class="pure-table">
        <tr><th>세부 항목</th><th>일반 할부</th><th>카프리오 장기렌트</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">취등록세/세금</td><td>{reg_tax + total_tax + total_ins:,} 원</td><td rowspan="3" class="bg-light text-blue" style="vertical-align:middle;">월 렌트료에<br>전부 포함</td></tr>
        <tr><td class="font-bold">만기 차량 매각</td><td>-{car_sell_value:,} 원</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 비용</td><td>{int(inst_total/months):,} 원</td><td>{int(rent_total/months):,} 원</td></tr>
        <tr class="bg-light font-bold"><td>💰 총 투입 비용</td><td>{inst_total:,} 원</td><td>{rent_total:,} 원</td></tr>
    </table>""", unsafe_allow_html=True)
    st.markdown(f'<div class="{"excel-green" if diff > 0 else "excel-red"}">{"🏆 카프리오 절감액: " + format(diff, ",") + "원" if diff > 0 else "할부 유리: " + format(abs(diff), ",") + "원"}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (인수형)</div>', unsafe_allow_html=True)
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    inst_total_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_total_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_ins - rent_total_ins
    st.markdown(f"""<table class="pure-table">
        <tr><th>세부 항목</th><th>일반 할부</th><th>카프리오 완전 인수형</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">만기 인수금</td><td>-</td><td>{rent_takeover_price:,} 원</td></tr>
        <tr><td class="font-bold">인수 취등록세</td><td>-</td><td>{rent_takeover_tax:,} 원</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 비용</td><td>{int(inst_total_ins/months):,} 원</td><td>{int(rent_total_ins/months):,} 원</td></tr>
        <tr class="bg-light font-bold"><td>💰 총 투입 비용</td><td>{inst_total_ins:,} 원</td><td>{rent_total_ins:,} 원</td></tr>
    </table>""", unsafe_allow_html=True)
    st.markdown(f'<div class="{"excel-green" if diff_ins > 0 else "excel-red"}">{"🏆 카프리오 절감액: " + format(diff_ins, ",") + "원" if diff_ins > 0 else "할부 유리: " + format(abs(diff_ins), ",") + "원"}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
