import streamlit as st

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
    .capture-box { border: 2px solid #0b3873; padding: 15px; border-radius: 6px; background-color: #ffffff; min-height: 440px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 8px; text-align: center; margin-top: 15px; }
    
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 8px; border: 1px solid #dee2e6; height: 40px; }
    
    /* 하단 검증 요율표 */
    .matrix-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-bottom: 10px; }
    .matrix-table th { background-color: #0b3873; color: white; font-weight: bold; padding: 5px; border: 1px solid #dee2e6; }
    .matrix-table td { padding: 5px; border: 1px solid #dee2e6; }
    
    .td-highlight { background-color: #e2efda; font-weight: bold; }
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

# ==========================================
# [SIDEBAR] 조건 설정 구역
# ==========================================
st.sidebar.header("📋 조건 설정")
is_corporate = st.sidebar.checkbox("🏢 법인 고객 여부", value=False)
installment_prepaid = st.sidebar.number_input("💵 할부 선납금", value=10000000, step=1000000)
installment_rate = st.sidebar.number_input("📈 할부 금리 (%)", value=5.0, step=0.1)
insurance_annual = st.sidebar.number_input("🛡️ 연 개인 보험료", value=1000000, step=100000)
installment_resale_pct = st.sidebar.number_input("📉 할부 잔존가치 (%)", value=installment_resale_pct, min_value=0, max_value=100, step=1)

# ==========================================
# [TOP MAIN] 타사 견적 파싱 구역
# ==========================================
raw_data = st.text_area("📋 타사 렌트 견적 복사 붙여넣기", placeholder="견적 텍스트를 입력하세요.", height=80)

if raw_data:
    lines = raw_data.strip().split('\n')
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
            elif "CC" in key: cc_text = val.replace(" ", "")
            elif "형태" in key: car_shape = val.replace(" ", "")

# ==========================================
# [BACKEND] 연산 로직
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

loan_amount = car_price - installment_prepaid
r = (installment_rate / 100) / 12
inst_monthly_pay = int(loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)) if r > 0 else int(loan_amount / months)

total_ins = int((insurance_annual / 12) * months)
total_tax = int((tax_annual / 12) * months)

corporate_discount = 0.9 if (is_corporate and car_shape != "경차" and car_shape != "승합") else 1.0
car_sell_value = int(car_price * (installment_resale_pct / 100) * corporate_discount)

# 렌트 만기 인수금 (기존 로직: 차량가의 40%로 가정)
rent_takeover_price = int(car_price * 0.40)
rent_takeover_tax = int(rent_takeover_price * 0.07)

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
                    <td class="font-bold" style="color:#0b3873;">{car_price:,} 원</td>
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
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (반납형)</div>', unsafe_allow_html=True)
    
    inst_total_cost_ret = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid - car_sell_value
    rent_total_cost_ret = (rent_monthly_pay * months) + rent_deposit
    diff_ret = inst_total_cost_ret - rent_total_cost_ret
    
    html_ret = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">세부 항목</th><th style="width:33%;">일반 할부</th><th style="width:33%;">장기렌트(반납형)</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">취등록세</td><td>{reg_tax:,} 원</td><td rowspan="4" class="bg-light text-blue" style="vertical-align:middle;">월 렌트료에<br>전부 포함</td></tr>
        <tr><td class="font-bold">자동차세/보험료</td><td>{total_tax + total_ins:,} 원</td></tr>
        <tr><td class="font-bold">만기 차량 매각</td><td>-{car_sell_value:,} 원</td></tr>
        <tr><td class="font-bold">-</td><td>-</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 환산 비용</td><td>{int(inst_total_cost_ret/months):,} 원</td><td>{int(rent_total_cost_ret/months):,} 원</td></tr>
        <tr class="bg-light font-bold" style="background-color:#e9ecef;"><td>💰 총 투입 비용</td><td>{inst_total_cost_ret:,} 원</td><td>{rent_total_cost_ret:,} 원</td></tr>
    </table>
    """
    st.markdown(html_ret, unsafe_allow_html=True)
    
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green">🏆 카프리오 반납형 선택 시 할부 대비 {diff_ret:,}원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 이용이 {abs(diff_ret):,}원 더 유리합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 인수형 테이블
with view_col2:
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (인수형)</div>', unsafe_allow_html=True)
    
    inst_total_cost_ins = (inst_monthly_pay * months) + reg_tax + total_tax + total_ins + installment_prepaid
    rent_total_cost_ins = (rent_monthly_pay * months) + rent_takeover_price + rent_takeover_tax + rent_deposit
    diff_ins = inst_total_cost_ins - rent_total_cost_ins

    html_ins = f"""
    <table class="pure-table">
        <tr><th style="width:34%;">세부 항목</th><th style="width:33%;">일반 할부</th><th style="width:33%;">장기렌트(인수형)</th></tr>
        <tr><td class="font-bold">선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
        <tr><td class="font-bold">월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
        <tr><td class="font-bold">취등록세</td><td>{reg_tax:,} 원</td><td rowspan="2" class="bg-light text-blue" style="vertical-align:middle;">월 렌트료에<br>전부 포함</td></tr>
        <tr><td class="font-bold">자동차세/보험료</td><td>{total_tax + total_ins:,} 원</td></tr>
        <tr><td class="font-bold">만기 인수금</td><td>-</td><td>{rent_takeover_price:,} 원</td></tr>
        <tr><td class="font-bold">인수 시 취등록세</td><td>-</td><td>{rent_takeover_tax:,} 원</td></tr>
        <tr class="bg-light font-bold"><td>📊 월 평균 환산 비용</td><td>{int(inst_total_cost_ins/months):,} 원</td><td>{int(rent_total_cost_ins/months):,} 원</td></tr>
        <tr class="bg-light font-bold" style="background-color:#e9ecef;"><td>💰 총 투입 비용</td><td>{inst_total_cost_ins:,} 원</td><td>{rent_total_cost_ins:,} 원</td></tr>
    </table>
    """
    st.markdown(html_ins, unsafe_allow_html=True)
    
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green">🏆 카프리오 인수형 선택 시 할부 대비 {diff_ins:,}원 절감!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="excel-red">할부 인수가 총 {abs(diff_ins):,}원 더 유리합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# [📊 BOTTOM] 검증 요율표 구역
# ==========================================
st.write("")
st.markdown('<div class="excel-header-gray">💻 내부 데이터 산출 요율 검증표</div>', unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown("**■ 잔존가치 (매각 요율표)**")
    st.markdown("""
    <table class="matrix-table">
        <tr><th>구분</th><th>24개월</th><th>36개월</th><th>48개월</th><th>60개월</th></tr>
        <tr><td>1만KM</td><td>78%</td><td>70%</td><td>63%</td><td>56%</td></tr>
        <tr><td>1.5만KM</td><td>75%</td><td>67%</td><td>60%</td><td>53%</td></tr>
        <tr><td>2만KM</td><td>72%</td><td>64%</td><td>57%</td><td>50%</td></tr>
        <tr><td>3만KM</td><td>65%</td><td>55%</td><td>48%</td><td>40%</td></tr>
    </table>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown("**■ 신용별 할부이자**")
    st.markdown("""
    <table class="matrix-table">
        <tr><th>구분</th><th>할부이자</th></tr>
        <tr><td>500점 이하</td><td>10.5 ~ 14.9%</td></tr>
        <tr><td>500 ~ 700점</td><td>7.5 ~ 9.9%</td></tr>
        <tr><td>700 ~ 900점</td><td>5.0 ~ 6.9%</td></tr>
        <tr><td>900점 이상</td><td>3.5 ~ 4.8%</td></tr>
    </table>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown("**■ 자동차세 (연간)**")
    st.markdown("""
    <table class="matrix-table">
        <tr><th>구분</th><th>CC당 비용</th><th>연간 비용</th></tr>
        <tr><td>1000CC 이하</td><td>104원</td><td>₩ 104,000</td></tr>
        <tr><td>1600CC 이하</td><td>182원</td><td>₩ 291,200</td></tr>
        <tr><td>2000CC 이하</td><td>260원</td><td>₩ 520,000</td></tr>
        <tr><td>2500CC 이하</td><td>260원</td><td>₩ 650,000</td></tr>
        <tr><td>3000CC 초과</td><td>260원</td><td>₩ 780,000</td></tr>
    </table>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown("**■ 취등록세 감면율**")
    st.markdown("""
    <table class="matrix-table">
        <tr><th>구분</th><th>세율</th><th>감면 한도</th></tr>
        <tr><td>일반</td><td>7%</td><td>-</td></tr>
        <tr><td>경차</td><td>4%</td><td>75만 원</td></tr>
        <tr><td>전기/수소차</td><td>7%</td><td>140만 원</td></tr>
        <tr><td>하이브리드</td><td>7%</td><td>40만 원</td></tr>
        <tr><td>승합차</td><td>5%</td><td>-</td></tr>
    </table>
    """, unsafe_allow_html=True)
