import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="브랜디드 원가 계산기", layout="wide")

# 세션 상태 초기화 (데이터 구조 변경: 단가, 요척 컬럼 추가)
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
    # 레이아웃을 2단으로 나눠서 보기 좋게 배치
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        fabric_price = st.number_input("원단 단가 (yd)", value=None, placeholder="예: 8,000", step=100)
    with f_col2:
        fabric_yield = st.number_input("원단 요척 (yd)", value=None, placeholder="예: 1.5", step=0.1, format="%.1f")
    
    st.subheader("2. 안감 (Lining)")
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        lining_price = st.number_input("안감 단가 (yd)", value=None, placeholder="예: 3,000", step=100)
    with l_col2:
        lining_yield = st.number_input("안감 요척 (yd)", value=None, placeholder="예: 2.0", step=0.1, format="%.1f")

    st.subheader("3. 기타 비용")
    labor = st.number_input("공임 (봉제+재단)", value=None, placeholder="예: 55,000", step=100)
    trim = st.number_input("자재비 (단추,지퍼 등)", value=None, placeholder="예: 10,000", step=100)
    
    st.markdown("---")
    
    overhead_rate = st.slider("기타 부대비용 및 마진 (%)", 0, 50, 25)
    
    # --- 계산 로직 ---
    # None(빈칸)일 경우 0으로 처리
    c_f_price = fabric_price if fabric_price is not None else 0
    c_f_yield = fabric_yield if fabric_yield is not None else 0
    c_l_price = lining_price if lining_price is not None else 0
    c_l_yield = lining_yield if lining_yield is not None else 0
    c_labor = labor if labor is not None else 0
    c_trim = trim if trim is not None else 0

    # 원단/안감 총액 계산 (단가 * 요척)
    total_fabric_cost = c_f_price * c_f_yield
    total_lining_cost = c_l_price * c_l_yield
    
    # 전체 합계
    subtotal = total_fabric_cost + total_lining_cost + c_labor + c_trim
    total_with_overhead = subtotal * (1 + overhead_rate / 100)
    final_vat = total_with_overhead * 1.1
    
    # 저장 버튼
    if st.button("💾 히스토리 저장"):
        if item_name == "":
            st.warning("품목명을 입력해주세요!") 
        elif subtotal == 0:
            st.warning("금액을 입력해주세요!") 
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = {
                '일시': now,
                '품목명': item_name,
                '원단단가': c_f_price,
                '원단요척': c_f_yield,
                '원단합계': int(total_fabric_cost),
                '안감단가': c_l_price,
                '안감요척': c_l_yield,
                '안감합계': int(total_lining_cost),
                '공임': c_labor,
                '자재': c_trim,
                '합계': int(subtotal),
                '최종원가(VAT)': int(round(final_vat))
            }
            st.session_state.history = pd.concat([pd.DataFrame([new_data]), st.session_state.history], ignore_index=True)
            st.success("상세 내역이 저장되었습니다!")

# 2. 메인 화면 - 계산 결과 리포트
st.header("📊 실시간 견적서")

# 상단: 최종 금액 카드
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("순수 합계 (원가)", f"{int(subtotal):,}원")
m_col2.metric(f"관리비 포함 ({overhead_rate}%)", f"{int(total_with_overhead):,}원")
m_col3.metric("최종 원가 (VAT 포함)", f"{int(final_vat):,}원", delta_color="inverse")

st.markdown("---")

# 중단: 상세 비용 구조 (사용자가 입력한 값이 맞는지 확인용)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.info(f"**🧵 원단 합계**\n\n{int(total_fabric_cost):,}원\n\n({c_f_price:,}원 × {c_f_yield}yd)")
with c2:
    st.info(f"**🧥 안감 합계**\n\n{int(total_lining_cost):,}원\n\n({c_l_price:,}원 × {c_l_yield}yd)")
with c3:
    st.info(f"**✂️ 공임**\n\n{c_labor:,}원")
with c4:
    st.info(f"**🧶 자재**\n\n{c_trim:,}원")

st.markdown("---")

# 3. 히스토리 섹션
st.subheader("📜 상세 기록 (엑셀 다운로드)")
if not st.session_state.history.empty:
    st.dataframe(st.session_state.history, use_container_width=True)
    
    csv = st.session_state.history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 상세 내역 엑셀 다운로드",
        data=csv,
        file_name=f"cost_detail_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    if st.button("🗑️ 기록 초기화"):
        st.session_state.history = pd.DataFrame(columns=st.session_state.history.columns)
        st.rerun()
else:
    st.info("왼쪽 사이드바에 단가와 요척을 입력하면 상세 견적이 계산됩니다.")
