import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="브랜디드 원가 계산기", layout="wide")

# 세션 상태 초기화 (데이터를 브라우저 메모리에 유지)
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=['일시', '품목명', '원단값', '안감', '공임', '자재', '합계', '최종원가(VAT)']
    )

st.title("👕 의류 제작 원가 관리 시스템")

# 1. 입력 섹션 (사이드바)
with st.sidebar:
    st.header("📋 데이터 입력")
    # 품목명도 빈칸으로 시작
    item_name = st.text_input("품목명 (예: 26SS 트렌치코트)", value="") 
    
    # 금액 입력칸 초기값을 0으로 설정
    fabric = st.number_input("원단값", value=0, step=100)
    lining = st.number_input("안감", value=0, step=100)
    labor = st.number_input("공임", value=0, step=100)
    trim = st.number_input("자재비", value=0, step=100)
    
    st.markdown("---")
    
    # 오차율/마진 설정
    overhead_rate = st.slider("기타 부대비용 및 마진 (%)", 0, 50, 25)
    
    # 계산 로직
    subtotal = fabric + lining + labor + trim
    total_with_overhead = subtotal * (1 + overhead_rate / 100)
    final_vat = total_with_overhead * 1.1
    
    # 저장 버튼
    if st.button("💾 히스토리 저장"):
        if item_name == "":
            st.warning("품목명을 입력해주세요!") # 품목명 누락 방지
        elif subtotal == 0:
            st.warning("금액을 입력해주세요!") # 금액 0원 저장 방지
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = {
                '일시': now,
                '품목명': item_name,
                '원단값': fabric,
                '안감': lining,
                '공임': labor,
                '자재': trim,
                '합계': subtotal,
                '최종원가(VAT)': round(final_vat)
            }
            # 기존 데이터와 합치기
            st.session_state.history = pd.concat([pd.DataFrame([new_data]), st.session_state.history], ignore_index=True)
            st.success("히스토리에 추가되었습니다!")

# 2. 메인 화면 - 현재 계산 결과
col1, col2, col3 = st.columns(3)
col1.metric("순수 합계", f"{subtotal:,}원")
col2.metric(f"관리비 포함 ({overhead_rate}%)", f"{int(total_with_overhead):,}원")
col3.metric("최종 원가 (VAT 포함)", f"{int(final_vat):,}원", delta_color="inverse")

st.markdown("---")

# 3. 히스토리 섹션
st.subheader("📜 계산 히스토리")
if not st.session_state.history.empty:
    st.dataframe(st.session_state.history, use_container_width=True)
    
    csv = st.session_state.history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 히스토리 엑셀(CSV) 다운로드",
        data=csv,
        file_name=f"cost_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    if st.button("🗑️ 전체 기록 삭제"):
        st.session_state.history = pd.DataFrame(columns=st.session_state.history.columns)
        st.rerun()
else:
    st.info("왼쪽 사이드바에 값을 입력하고 '히스토리 저장'을 눌러주세요.")
