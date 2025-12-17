import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 0. 내 제품 리스트 (상위 30개 탑재 완료)
# ---------------------------------------------------------
# 구조: "제품명": {"cost": 원가, "price": 정가(없으면 0), "discount": 할인율(없으면 0)}
MY_DATABASE = {
    "[DESK] THOMAS MASON OFFICE SHIRT": {"cost": 85892, "price": 0, "discount": 0},
    "[DESK] BASIC STEEL TIE [NAVY]": {"cost": 15992, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [BLACK]": {"cost": 42850, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL MOCK-NECK KNIT [CHARCOAL]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [CHARCOAL]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [DARK NAVY]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [DEEP BROWN]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [MELANGE GRAY]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [SILVER BLUE]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED BLACK]": {"cost": 59290, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED CHARCOAL]": {"cost": 72566, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED NAVY]": {"cost": 88629, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [LIGHT BEIGE]": {"cost": 61974, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED BEIGE]": {"cost": 54329, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED BLACK]": {"cost": 42561, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED CHARCOAL]": {"cost": 51480, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED KHAKI]": {"cost": 57475, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED NAVY]": {"cost": 51480, "price": 0, "discount": 0},
    "[DESK] OFFICE HALF SHIRT [LIGHT BLUE]": {"cost": 29576, "price": 0, "discount": 0},
    "[DESK] OFFICE HALF SHIRT [LIGHT GRAY]": {"cost": 29576, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [DEEP CHARCOAL]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [FOG]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [GRAPHITE]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [GRAY]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [ICE BLUE]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [INK NAVY]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [WHITE]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] STRIPE SHIRT [BLACK]": {"cost": 35450, "price": 0, "discount": 0},
    "[DESK] ONE TUCK CHINO SHORTS [WASHED BEIGE]": {"cost": 39384, "price": 0, "discount": 0},
    "[DESK] ONE TUCK CHINO SHORTS [WASHED CHARCOAL]": {"cost": 39384, "price": 0, "discount": 0},
    # 나머지 데이터는 사이드바의 '엑셀 변환기'를 이용해 추가하세요!
}

# ---------------------------------------------------------
# 1. 버전 관리
# ---------------------------------------------------------
current_version = "v2.1"
update_history = [
    {"ver": "v2.1", "date": "24.12.17", "desc": "긴급 수정: 코드 잘림 현상 복구 및 2열(제품명/원가) 데이터 자동 변환 기능 추가"},
    {"ver": "v2.0", "date": "24.12.17", "desc": "모드 분리: [직접 입력]과 [DB 불러오기]를 스위치로 완전 분리"},
    {"ver": "v1.9", "date": "24.12.17", "desc": "DB 구조 확장: 제품 선택 시 원가 및 정가 3개까지 완전 자동 입력"},
]

st.set_page_config(page_title=f"브랜디드 수익성 계산기 {current_version}", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    div.row-widget.stRadio > div { flex-direction: row; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 사이드바 (엑셀 변환기 v2.1 - 2열 데이터 지원)
# ---------------------------------------------------------
with st.sidebar:
    with st.expander("🛠️ 엑셀 데이터 변환기 (Click)", expanded=True):
        st.info("엑셀의 **[제품명 | 원가]** 2개 열만 복사해도 됩니다. (나머지는 0으로 채워짐)")
        raw_text = st.text_area("엑셀 데이터 붙여넣기", height=150)
        
        if raw_text:
            try:
                converted_lines = []
                lines = raw_text.strip().split('\n')
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2: # 최소 2개 열(이름, 원가)만 있으면 OK
                        name = parts[0].strip()
                        cost = parts[1].strip().replace(',', '')
                        
                        # 정가, 할인율이 없으면 0으로 처리
                        price = parts[2].strip().replace(',', '') if len(parts) > 2 else "0"
                        dc = parts[3].strip().replace('%', '') if len(parts) > 3 else "0"
                        
                        converted_lines.append(f'"{name}": {{"cost": {cost}, "price": {price}, "discount": {dc}}},')
                
                result_code = "\n".join(converted_lines)
                st.code(result_code, language='python')
                st.caption("▲ 위 코드를 복사해서 MY_DATABASE 안에 붙여넣으세요.")
            except Exception:
                st.error("형식 오류. 엑셀 데이터를 확인하세요.")

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
    mode = st.radio(
        f"입력 방식 선택 ({tab_idx})", 
        ["📝 직접 입력", "📂 DB 불러오기"], 
        key=f"mode_{tab_idx}",
        label_visibility="collapsed"
    )

    if mode == "📂 DB 불러오기":
        options = list(MY_DATABASE.keys())
        if not options:
            st.warning("데이터베이스가 비어있습니다. 코드에 제품을 추가해주세요.")
            return None
            
        selection = st.selectbox("저장된 제품 선택", options, key=f"sel_{tab_idx}")
        data = MY_DATABASE[selection]
        
        # 불러온 데이터 보여주기
        c1, c2, c3 = st.columns(3)
        c1.metric("원가", f"{data['cost']:,}원")
        
        # 정가가 0원이면(데이터에 없으면) 직접 입력하게 유도
        if data['price'] == 0:
            st.caption("⚠️ 저장된 정가가 없습니다. 아래에 정가를 입력해주세요.")
            p_input = st.number_input(f"정가 입력 ({selection})", step=1000, key=f"db_p_{tab_idx}")
            current_price = p_input
        else:
            c2.metric("정가", f"{data['price']:,}원")
            current_price = data['price']

        c3.metric("저장된 할인율", f"{data['discount']}%")
        
        # 결과 리턴
        if current_price > 0:
            return {
                "type": "db",
                "name": selection,
                "cost": data['cost'],
                "prices": [current_price],
                "fixed_discount": data['discount']
            }
        else:
            return None

    else:
        # 직접 입력 모드
        p_name = st.text_input(f"제품명 ({tab_idx})", placeholder="예: 옥스포드 셔츠", key=f"name_{tab_idx}")
        p_cost = st.number_input(f"원가 ({tab_idx})", value=None, step=1000, format="%d", key=f"cost_{tab_idx}")
        
        c1, c2, c3 = st.columns(3)
        with c1: p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key=f"p1_{tab_idx}")
        with c2: p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key=f"p2_{tab_idx}")
        with c3: p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key=f"p3_{tab_idx}")
        
        if p_cost is not None:
            valid_prices = [p for p in [p1, p2, p3] if p is not None]
            if valid_prices:
                return {
                    "type": "manual",
                    "name": p_name if p_name else f"제품{tab_idx}",
                    "cost": p_cost,
                    "prices": valid_prices,
                    "fixed_discount": None
                }
    return None

# --- 탭별 렌더링 ---
with tab1:
    res1 = render_input_tab(
