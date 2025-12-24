import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="브랜디드 원가 계산기", layout="wide")

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=[
            '일시', '품목명', 
            '원단단가', '원단요척', '원단합계', 
            '안감단가', '안감요척', '안감합계', 
            '공임', '자재', '합계', '최종원가(VAT)'
        ]
    )

st.title("👕 의류 제작 원가 관리 시스템")

# 1. 입력 섹션 (사이드바)
with st.sidebar:
    st.header("📋 데이터 입력")
    item_name = st.text_input("품목명", value="", placeholder="예: 26SS 트렌치코트")
    
    st.subheader("1. 원단 (Fabric)")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        # (yd) -> (원)으로 수정
        fabric_price = st.number_input("원단 단가 (원)", value=None, placeholder="예: 8,000", step=100)
    with f_col2:
        fabric_yield = st.number_input("원단 요척 (yd)", value=None, placeholder="예: 1.5", step=0.1, format="%.1f")
    
    st.subheader("2. 안감 (Lining)")
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        # (yd) -> (원)으로 수정
        lining_price = st.number_input("안감 단가 (원)", value=None, placeholder="예: 3,000", step=100)
    with l_col2:
        lining_yield = st.number_input("안감 요척 (yd)", value=None, placeholder="예: 2.0", step=0.1, format="%.1f")

    st.subheader("3. 기타 비용")
    labor = st.number_input("공임 (봉제+재단)", value=None, placeholder="예: 55,000",
