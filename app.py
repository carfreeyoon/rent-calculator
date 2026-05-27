import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# CSS 정의
st.markdown("""
    <style>
    .common-info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; margin-bottom: 25px; }
    .common-table { width: 100%; border-collapse: collapse; background-color: #ffffff; text-align: center; font-size: 13px; }
    .common-table th { background-color: #f1f3f5; color: #0b3873; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .common-table td { padding: 8px; border: 1px solid #dee2e6; color: #333333; }
    .excel-header-blue { background-color: #0b3873; color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 6px 6px 0 0; }
    .compare-container { border: 2px solid #0b3873; border-radius: 6px; background-color: #ffffff; padding: 15px; margin-bottom: 20px; }
    .pure-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    .pure-table th { background-color: #f1f3f5; color: #333333; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .pure-table td { padding: 8px; border: 1px solid #dee2e6; height: 38px; }
    .excel-green { background-color: #e2efda; color: #375623; font-weight: bold; font-size: 14px; border: 1px solid #a9d08e; border-radius: 4px; padding: 8px; text-align: center; }
    .excel-red { background-color: #fce4d6; color: #c65911; font-weight: bold; font-size: 14px; border: 1px solid #f4b084; border-radius: 4px; padding: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# (상단 로직 생략 - 이전과 동일)
# ... [연산 로직 및 변수 계산 부분 유지] ...

# 수정된 출력 섹션
st.markdown(f"""
    <div class='common-info-box'>
        <div style='font-size:15px; font-weight:bold; margin-bottom:10px; color:#0b3873;'>🚘 비교 차량 공통 조건</div>
        <table class='common-table'>
            <tr>
                <th>차량명</th><th>옵션</th><th>차량가격</th><th>계약기간</th><th>약정거리</th>
            </tr>
            <tr>
                <td>{car_name}</td><td>{car_option}</td><td>{car_price:,} 원</td><td>{months} 개월</td><td>{mileage}</td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

view_col1, view_col2 = st.columns(2)

with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (반납형)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class='compare-container'>
        <table class='pure-table'>
            <tr><th>세부 항목</th><th>일반 할부</th><th>장기렌트</th></tr>
            <tr><td>선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
            <tr><td>월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
            <tr><td>취등록세</td><td>{reg_tax:,} 원</td><td rowspan='4'>렌트료 포함</td></tr>
            <tr><td>자동차세/보험료</td><td>{total_tax + total_ins:,} 원</td></tr>
            <tr><td>만기 차량 매각</td><td>-{car_sell_value:,} 원</td></tr>
            <tr><td>-</td><td>-</td></tr>
            <tr><td><b>총 투입 비용</b></td><td><b>{inst_total_cost_ret:,} 원</b></td><td><b>{rent_total_cost_ret:,} 원</b></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    if diff_ret > 0:
        st.markdown(f'<div class="excel-green">🏆 카프리오 반납형 선택 시 {diff_ret:,}원 절감!</div>', unsafe_allow_html=True)

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (인수형)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class='compare-container'>
        <table class='pure-table'>
            <tr><th>세부 항목</th><th>일반 할부</th><th>완전 인수형</th></tr>
            <tr><td>선납금</td><td>{installment_prepaid:,} 원</td><td>{rent_deposit:,} 원</td></tr>
            <tr><td>월납입금</td><td>{inst_monthly_pay:,} 원</td><td>{rent_monthly_pay:,} 원</td></tr>
            <tr><td>취등록세</td><td>{reg_tax:,} 원</td><td rowspan='2'>렌트료 포함</td></tr>
            <tr><td>자동차세/보험료</td><td>{total_tax + total_ins:,} 원</td></tr>
            <tr><td>만기 인수금</td><td>-</td><td>{rent_takeover_price:,} 원</td></tr>
            <tr><td>인수 시 취등록세</td><td>-</td><td>{rent_takeover_tax:,} 원</td></tr>
            <tr><td><b>총 투입 비용</b></td><td><b>{inst_total_cost_ins:,} 원</b></td><td><b>{rent_total_cost_ins:,} 원</b></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    if diff_ins > 0:
        st.markdown(f'<div class="excel-green">🏆 카프리오 인수형 선택 시 {diff_ins:,}원 절감!</div>', unsafe_allow_html=True)
