import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. 버전 관리 데이터 (여기에 내용을 추가하면 사이드바에 자동 반영됨)
# ---------------------------------------------------------
current_version = "v1.5"
update_history = [
    {"ver": "v1.5", "date": "24.12.17", "desc": "설명 텍스트 오류(물결표시) 수정, 버전 히스토리 탭 추가"},
    {"ver": "v1.4", "date": "24.12.17", "desc": "제품명 기준 정렬 시 할인율 오름차순 자동 정렬 적용"},
    {"ver": "v1.3", "date": "24.12.17", "desc": "표 항목 순서 변경 및 가운데 정렬 디자인 적용"},
    {"ver": "v1.2", "date": "24.12.17", "desc": "마진율 구간별 색상 자동 적용 (파랑~빨강)"},
    {"ver": "v1.1", "date": "24.12.17", "desc": "제품 3개 비교 탭 및 할인율 선택 기능 추가"},
    {"ver": "v1.0", "date": "24.12.17", "desc": "초기 런칭 (수익성 계산 로직 구현)"},
]

# 페이지 설정
st.set_page_config(page_title=f"브랜디드 수익성 계산기 {current_version}", layout="wide")

# 스타일 조정 (가운데 정렬 + 폰트)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    /* 표 헤더 및 데이터 가운데 정렬 */
    th { text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 사이드바 (업데이트 히스토리 표시)
# ---------------------------------------------------------
with st.sidebar:
    st.header(f"📜 업데이트 히스토리")
    st.caption(f"Current Version: **{current_version}**")
    st.markdown("---")
    
    # 히스토리 리스트 반복 출력
    for item in update_history:
        st.markdown(f"**[{item['ver']}]** ({item['date']})")
        st.write(f"- {item['desc']}")
        st.markdown("") # 공백

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 할인율 선택 기능
with st.container():
    st.write("🔻 **보고 싶은 할인율을 선택하세요**")
    selected_rates = st.multiselect(
        "할인율(%)", 
        options=range(0, 95, 5), 
        default=[] 
    )
    st.markdown("---")

# 제품 정보 입력 (탭 구분)
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])

products = [] 

with tab1:
    p1_name = st.text_input("제품명 (1)", placeholder="예: 옥스포드 셔츠", key="n1")
    p1_cost = st.number_input("원가 (1)", value=None, step=1000, format="%d", key="c1")
    col1, col2, col3 = st.columns(3)
    with col1: p1_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="p1_1")
    with col2: p1_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="p1_2")
    with col3: p1_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="p1_3")
    
    if p1_cost is not None:
        valid_prices = [p for p in [p1_p1, p1_p2, p1_p3] if p is not None]
        if valid_prices:
            products.append({"name": p1_name if p1_name else "제품1", "cost": p1_cost, "prices": valid_prices})

with tab2:
    p2_name = st.text_input("제품명 (2)", placeholder="예: 데님 팬츠", key="n2")
    p2_cost = st.number_input("원가 (2)", value=None, step=1000, format="%d", key="c2")
    col1, col2, col3 = st.columns(3)
    with col1: p2_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="p2_1")
    with col2: p2_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="p2_2")
    with col3: p2_p3 = st
