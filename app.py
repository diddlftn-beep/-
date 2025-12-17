import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 0. 내 제품 리스트 (제품명, 원가, 정가, 할인율)
# ---------------------------------------------------------
# 구조: "제품명": {"cost": 원가, "price": 정가, "discount": 저장된할인율}
MY_DATABASE = {
    "25SS 옥스포드 셔츠": {"cost": 18000, "price": 49000, "discount": 10},
    "25SS 데님 팬츠": {"cost": 22000, "price": 69000, "discount": 15},
    # 엑셀 변환기로 만든 코드를 여기에 붙여넣으세요
}

# ---------------------------------------------------------
# 1. 버전 관리
# ---------------------------------------------------------
current_version = "v2.0"
update_history = [
    {"ver": "v2.0", "date": "24.12.17", "desc": "모드 분리: [직접 입력]과 [DB 불러오기]를 스위치로 완전 분리"},
    {"ver": "v1.9", "date": "24.12.17", "desc": "DB 구조 확장: 제품 선택 시 원가 및 정가 3개까지 완전 자동 입력"},
    {"ver": "v1.8", "date": "24.12.17", "desc": "편의기능 추가: 엑셀 데이터를 코드 포맷으로 자동 변환해주는 도구 탑재"},
]

st.set_page_config(page_title=f"브랜디드 수익성 계산기 {current_version}", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    /* 라디오 버튼 가로 정렬 */
    div.row-widget.stRadio > div { flex-direction: row; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 사이드바 (엑셀 변환기 v2)
# ---------------------------------------------------------
with st.sidebar:
    with st.expander("🛠️ 엑셀 데이터 변환기 (Click)", expanded=False):
        st.info("엑셀의 **[제품명 | 원가 | 정가 | 할인율]** 4개 열을 복사하세요.")
        raw_text = st.text_area("엑셀 데이터 붙여넣기", height=150)
        
        if raw_text:
            try:
                converted_lines = []
                lines = raw_text.strip().split('\n')
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        cost = parts[1].strip().replace(',', '')
                        price = parts[2].strip().replace(',', '') if len(parts) > 2 else "0"
                        dc = parts[3].strip().replace('%', '') if len(parts) > 3 else "0"
                        
                        converted_lines.append(f'"{name}": {{"cost": {cost}, "price": {price}, "discount": {dc}}},')
                
                result_code = "\n".join(converted_lines)
                st.code(result_code, language='python')
                st.caption("▲ 위 코드를 복사해서 MY_DATABASE 안에 붙여넣으세요.")
            except Exception:
                st.error("형식 오류. 엑셀 4개 열(이름/원가/정가/할인율)인지 확인하세요.")

    st.markdown("---")
    st.header(f"📜 업데이트 히스토리")
    st.caption(f"Current Version: **{current_version}**")
    for item in update_history:
        st.markdown(f"**[{item['ver']}]** ({item['date']})")
        st.write(f"- {item['desc']}")
        st.markdown("") 

# ---------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 할인율 선택 (직접 입력 모드용)
with st.container():
    st.write("🔻 **[직접 입력] 모드일 때 비교할 할인율**")
    selected_rates = st.multiselect(
        "할인율(%)", 
        options=range(0, 95, 5), 
        default=[] 
    )
    st.markdown("---")

# 제품 정보 입력 (탭 구분)
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
products = [] 

# --- 입력 처리 함수 ---
def render_input_tab(tab_idx):
    # 모드 선택 (라디오 버튼)
    mode = st.radio(
        f"입력 방식 선택 ({tab_idx})", 
        ["📝 직접 입력", "📂 DB 불러오기"], 
        key=f"mode_{tab_idx}",
        label_visibility="collapsed" # 라벨 숨김 (깔끔하게)
    )

    # 1. DB 불러오기 모드
    if mode == "📂 DB 불러오기":
        options = list(MY_DATABASE.keys())
        if not options:
            st.warning("데이터베이스가 비어있습니다. 코드에 제품을 추가해주세요.")
            return None
            
        selection = st.selectbox("저장된 제품 선택", options, key=f"sel_{tab_idx}")
        data = MY_DATABASE[selection]
        
        # 정보 보여주기 (읽기 전용)
        c1, c2, c3 = st.columns(3)
        c1.metric("원가", f"{data['cost']:,}원")
        c2.metric("정가", f"{data['price']:,}원")
        c3.metric("저장된 할인율", f"{data['discount']}%")
        
        # 결과 리스트에 추가할 형태로 리턴
        return {
            "type": "db",
            "name": selection,
            "cost": data['cost'],
            "prices": [data['price']], # 리스트 형태 유지
            "fixed_discount": data['discount'] # 고정 할인율
        }

    # 2. 직접 입력 모드
    else:
        p_name = st.text_input(f"제품명 ({tab_idx})", placeholder="예: 옥스포드 셔츠", key=f"name_{tab_idx}")
        p_cost = st.number_input(f"원가 ({tab_idx})", value=None, step=1000, format="%d", key=f"cost_{tab_idx}")
        
        c1, c2, c3 = st.columns(3)
        with c1: p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key=f"p1_{tab_idx}")
        with c2: p2 = st.number_input("정가 B
