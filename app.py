import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 버전 관리 & 설정
# ---------------------------------------------------------
current_version = "v3.2 (Hybrid Discount)"
st.set_page_config(page_title=f"수익성 계산기 {current_version}", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    div.row-widget.stRadio > div { flex-direction: row; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 불러오기 (products.csv 파일 읽기)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    if not os.path.exists("products.csv"):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    try:
        df = pd.read_csv("products.csv")
        df.columns = df.columns.str.strip()
        for col in ['cost', 'price', 'discount']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"데이터 파일(products.csv) 오류: {e}")
        return pd.DataFrame()

df_products = load_data()

# ---------------------------------------------------------
# 3. 메인 화면
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 할인율 선택 (공통 적용)
with st.container():
    st.write("🔻 **비교하고 싶은 할인율을 선택하세요** (DB 불러오기 시에도 적용됨)")
    selected_rates = st.multiselect("할인율(%)", options=range(0, 95, 5), default=[])
    st.markdown("---")

# 탭 설정
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
products_to_calc = [] 

# --- 입력 처리 함수 ---
def render_input_tab(tab_idx):
    mode = st.radio(
        f"입력 방식 선택 ({tab_idx})", 
        ["📝 직접 입력", "📂 DB 불러오기"], 
        key=f"mode_{tab_idx}",
        label_visibility="collapsed"
    )

    if mode == "📂 DB 불러오기":
        if df_products.empty:
            st.warning("products.csv 파일이 없습니다.")
            return None
            
        options = df_products['name'].tolist()
        selection = st.selectbox("제품 검색 및 선택", options, key=f"sel_{tab_idx}")
        row = df_products[df_products['name'] == selection].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("원가", f"{row['cost']:,}원")
        c2.metric("정가", f"{row['price']:,}원")
        c3.metric("기본 할인율", f"{row['discount']}%") # 단순 표시용
        
        return {
            "type": "db",
            "name": selection,
            "cost": row['cost'],
            "prices": [row['price']],
            "fixed_discount": row['discount']
        }

    else:
        p_name = st.text_input(f"제품명 ({tab_idx})", placeholder="직접 입력", key=f"name_{tab_idx}")
        p_cost = st.number_input(f"원가 ({tab_idx})", value=None, step=1000, key=f"cost_{tab_idx}")
        
        c1, c2, c3 = st.columns(3)
        with c1: p1 = st.number_input("정가 A", value=None, step=1000, key=f"p1_{tab_idx}")
        with c2: p2 = st.number_input("정가 B", value=None, step=1000, key=f"p2_{tab_idx}")
        with c3: p3 = st.number_input("정가 C", value=None, step=1000, key=f"p3_{tab_idx}")
        
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

# 탭 렌더링
with tab1:
    r1 = render_input_tab(1)
    if r1: products_to_calc.append(r1)
with tab2:
    r2 = render_input_tab(2)
    if r2: products_to_calc.append(r2)
with tab3:
    r3 = render_input_tab(3)
    if r3: products_to_calc.append(r3)

# ---------------------------------------------------------
#
