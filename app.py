import streamlit as st

st.set_page_config(page_title="카프리오 비교 프로그램", layout="wide")

# CSS: 정교한 레이아웃 및 공백 제거
st.markdown("""
    <style>
    div.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* 상단 공통 조건 박스 */
    .common-info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .common-table { width: 100%; border-collapse: collapse; background-color: #ffffff; text-align: center; font-size: 13px; }
    .common-table th { background-color: #f1f3f5; color: #0b3873; font-weight: bold; padding: 8px; border: 1px solid #dee2e6; }
    .common-table td { padding: 8px; border: 1px solid #dee2e6; color: #333333; }

    /* 메인 비교 테이블 - min-height 제거로 공백 해결 */
    .excel-header-blue { background-color: #0b3873; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 15px; border-radius: 4px 4px 0 0; margin-bottom: 0px; }
    .excel-header-gray { background-color: #5a5a5a; color: white; padding: 6px; text-align: center; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 10px; }
    .capture-box { border: 2px solid #0b3873; padding: 15px; border-radius: 0 0 6px 6px; background-color: #ffffff; }
    
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

# [이하 로직은 기존 코드와 동일하게 유지하세요]
# ... (변수 설정, 사이드바, 파싱, 연산 로직 부분) ...

# 1. 상단 공통 조건 표 (요청하신 대로 옵션 포함)
st.markdown(f"""
    <div class="common-info-box">
        <div style="font-size:15px; font-weight:bold; margin-bottom:10px; color:#0b3873;">🚘 비교 차량 공통 조건</div>
        <table class="common-table">
            <thead>
                <tr>
                    <th>차량명</th><th>옵션</th><th>차량가격</th><th>계약기간</th><th>약정거리</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="font-bold">{car_name}</td>
                    <td style="color:gray;">{car_option}</td>
                    <td class="font-bold" style="color:#0b3873;">{car_price:,} 원</td>
                    <td>{months} 개월</td>
                    <td>{mileage}</td>
                </tr>
            </tbody>
        </table>
    </div>
""", unsafe_allow_html=True)

# 2. 대칭형 비교 테이블 (min-height가 제거된 capture-box 사용)
view_col1, view_col2 = st.columns(2)

with view_col1:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (반납형)</div>', unsafe_allow_html=True)
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    # [여기에 기존 html_ret 테이블 코드 삽입]
    st.markdown('</div>', unsafe_allow_html=True)
    # [결과 메시지]

with view_col2:
    st.markdown('<div class="excel-header-blue">카프리오 비교 프로그램 (인수형)</div>', unsafe_allow_html=True)
    st.markdown('<div class="capture-box">', unsafe_allow_html=True)
    # [여기에 기존 html_ins 테이블 코드 삽입]
    st.markdown('</div>', unsafe_allow_html=True)
    # [결과 메시지]
