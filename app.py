import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# 레이아웃 정렬 및 CSS
st.markdown("""
    <style>
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .common-info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .common-table { width: 100%; border-collapse: collapse; background-color: #ffffff; text-align: center; font-size: 13px; }
    .common-table th { background-color: #f1f3f5; color: #0b3873; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .common-table td { padding: 8px; border: 1px solid #dee2e6; color: #333333; }
    .excel-header-blue { background-color: #0b3873; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px; margin-bottom: 12px; }
    .excel-header-gray { background-color: #5a5a5a; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 10px; }
    .capture-box { border: 2px solid #0b3873; padding: 15px; border-radius: 6px; background-color: #ffffff; min-height: 440px; }
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 8px; border: 1px solid #dee2e6; height: 40px; }
    .matrix-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-bottom: 10px; }
    .matrix-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 5px; border: 1px solid #dee2e6; }
    .matrix-table td { padding: 5px; border: 1px solid #dee2e6; }
    .td-highlight { background-color: #fff3bf !important; font-weight: bold; }
    .bg-light { background-color: #f8f9fa; }
    .text-blue { color: #0b3873; font-weight: bold; }
    .font-bold { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 초기값 및 파싱 (이전과 동일)
car_name, car_option, car_price, months, mileage = "기아 카니발 가솔린 1.6 터보 하이브리드 2WD 7인승 노블레스", "-", 47810000, 60, "2만Km"
rent_monthly_pay, rent_deposit, cc_text, car_shape = 600930, 0, "1600CC이하", "하이브리드"
installment_resale_pct = 50

st.sidebar.header("📋 조건 설정")
is_corporate = st.sidebar.checkbox("🏢 법인 고객 여부", value=False)
installment_prepaid = st.sidebar.number_input("💵 할부 선납금", value=10000000, step=1000000)
installment_rate = st.sidebar.number_input("📈 할부 금리 (%)", value=5.0, step=0.1)
insurance_annual = st.sidebar.number_input("🛡️ 연 개인 보험료", value=1000000, step=100000)
installment_resale_pct = st.sidebar.number_input("📉 할부 잔존가치 (%)", value=installment_resale_pct, min_value=0, max_value=100, step=1)

raw_data = st.text_area("📋 타사 렌트 견적 복사 붙여넣기", placeholder="견적 텍스트를 입력하세요.", height=80)
if raw_data:
    lines = raw_data.strip().split('\n')
    for line in lines:
        parts = line.split('\t') if '\t' in line else (line.split(':') if ':' in line else line.split())
        if len(parts) >= 2:
            key, val = parts[0].strip(), "".join(parts[1:]).strip()
            def clean_num(v): return int("".join(filter(str.isdigit, v))) if any(char.isdigit() for char in v) else 0
            if "차량명" in key: car_name = val
            elif "옵션" in key: car_option = val
            elif "차량가" in key: car_price = clean_num(val)
            elif "개월수" in key: months = clean_num(val)
            elif "약정거리" in key: mileage = val.replace(" ", "")
            elif "월납입" in key: rent_monthly_pay = clean_num(val)
            elif "선납금" in key or "보증금" in key: rent_deposit = clean_num(val)
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

# 로직 및 UI
e15, e14, g14, i14 = ("O" if "승합" in car_shape else ""), ("O" if "경차" in car_shape else ""), ("O" if "전기" in car_shape or "수소" in car_shape else ""), ("O" if "하이브리드" in car_shape else "")
reg_tax = max(0, int((car_price * 0.05 - 1400000) if (e15 and g14) else (car_price * 0.05 - 400000) if (e15 and i14) else (car_price * 0.05) if e15 else (car_price * 0.04 - 750000) if e14 else (car_price * 0.07 - 1400000) if g14 else (car_price * 0.07 - 400000) if i14 else car_price * 0.07))
tax_annual = 130000 if "전기" in car_shape else 104000 if "1000" in cc_text else 291200 if "1600" in cc_text else 520000 if "2000" in cc_text else 650000 if "2500" in cc_text else 780000 if "3000" in cc_text else 130000
loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)) if r > 0 else int(loan_amount / months)

st.markdown(f'<div class="common-info-box"><table class="common-table"><thead><tr><th>차량명</th><th>차량가격</th><th>계약기간</th><th>약정거리</th></tr></thead><tbody><tr><td class="font-bold">{car_name}</td><td class="font-bold text-blue">{car_price:,} 원</td><td>{months} 개월</td><td>{mileage}</td></tr></tbody></table></div>', unsafe_allow_html=True)

# 메인 테이블 생략 (내용 동일)
# ... 요율표 부분에 하이라이트 함수 적용 ...
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

# 잔존가치 표
with m_col1:
    h = lambda m, k: "td-highlight" if str(months) in m and k in mileage else ""
    st.markdown(f"""<table class="matrix-table"><tr><th>구분</th><th>24</th><th>36</th><th>48</th><th>60</th></tr>
    <tr><td>1만</td><td class="{h('24','1만')}">78%</td><td class="{h('36','1만')}">70%</td><td class="{h('48','1만')}">63%</td><td class="{h('60','1만')}">56%</td></tr>
    <tr><td>1.5만</td><td class="{h('24','1.5만')}">75%</td><td class="{h('36','1.5만')}">67%</td><td class="{h('48','1.5만')}">60%</td><td class="{h('60','1.5만')}">53%</td></tr>
    <tr><td>2만</td><td class="{h('24','2만')}">72%</td><td class="{h('36','2만')}">64%</td><td class="{h('48','2만')}">57%</td><td class="{h('60','2만')}">50%</td></tr>
    <tr><td>3만</td><td class="{h('24','3만')}">65%</td><td class="{h('36','3만')}">55%</td><td class="{h('48','3만')}">48%</td><td class="{h('60','3만')}">40%</td></tr></table>""", unsafe_allow_html=True)

# 자동차세 표
with m_col3:
    c = lambda val: "td-highlight" if val in cc_text or (val == "전기차" and "전기" in car_shape) else ""
    st.markdown(f"""<table class="matrix-table">
    <tr><td class="{c('1000')}">1000cc이하</td><td>₩104,000</td></tr>
    <tr><td class="{c('1600')}">1600cc이하</td><td>₩291,200</td></tr>
    <tr><td class="{c('2000')}">2000cc이하</td><td>₩520,000</td></tr>
    <tr><td class="{c('2500')}">2500cc이하</td><td>₩650,000</td></tr>
    <tr><td class="{c('3000')}">3000cc초과</td><td>₩780,000</td></tr>
    <tr><td class="{c('전기차')}">전기차</td><td>₩130,000</td></tr></table>""", unsafe_allow_html=True)

# 취등록세 표
with m_col4:
    t = lambda val: "td-highlight" if val in car_shape else ""
    st.markdown(f"""<table class="matrix-table">
    <tr><td class="{t('경차')}">경차(4%)</td><td>75만감면</td></tr>
    <tr><td class="{t('전기')}">전기/수소(7%)</td><td>140만감면</td></tr>
    <tr><td class="{t('하이브리드')}">하이브리드(7%)</td><td>40만감면</td></tr>
    <tr><td class="{t('승합')}">승합차(5%)</td><td>-</td></tr>
    <tr><td class="{'' if any(x in car_shape for x in ['경차','전기','하이브리드','승합']) else 'td-highlight'}">일반(7%)</td><td>-</td></tr></table>""", unsafe_allow_html=True)
