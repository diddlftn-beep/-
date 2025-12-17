import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정 (사이드바 강제 확장 설정 추가)
# ---------------------------------------------------------
current_version = "v5.3 (Sidebar Fixed)"
st.set_page_config(
    page_title=f"수익성 분석기 {current_version}", 
    layout="wide",
    initial_sidebar_state="expanded"  # 👈 [중요] 사이드바를 항상 펼쳐둠
)

# ---------------------------------------------------------
# 2. 🔒 보안 구역
# ---------------------------------------------------------
def check_password():
    """비밀번호 확인 및 로그인 처리"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # --- 로그인 화면 ---
    st.markdown("## 🔒 관계자 외 접근 금지")
    st.info("보안을 위해 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호", type="password", key="password_input")

    if password_input:
        if password_input == st.secrets["password"]:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

    return False

if not check_password():
    st.stop()

# =========================================================
# 🔓 로그인 성공 후 실행되는 영역
# =========================================================

# ---------------------------------------------------------
# 3. 로그아웃 버튼 (사이드바 + 메인 상단 동시 배치)
# ---------------------------------------------------------
def logout():
    st.session_state.password_correct = False
    st.rerun()

# [1] 사이드바에 로그아웃 버튼 배치
with st.sidebar:
    st.title("⚙️ 설정")
    st.write(f"현재 버전: {current_version}")
    st.write("---")
    if st.button("🔒 로그아웃 (사이드바)", key='logout_sidebar'):
        logout()

# [2] 메인 화면 우측 상단에도 로그아웃 버튼 배치 (혹시 사이드바 안 보일까봐)
col_main_title, col_logout = st.columns([8, 2])
with col_main_title:
    st.title(f"📊 멀티 수익성 분석기")
with col_logout:
    st.write("") # 줄바꿈용
    st.write("") 
    if st.button("🔒 로그아웃", key='logout_main'):
        logout()

st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

st.markdown("""
    <style>
    /* 버튼 스타일 통일 */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 데이터 불러오기
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "products.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()
        rename_map = {'상품명': 'name', '원가': 'cost', '판매가': 'price', '정가': 'price', '할인율': 'discount'}
        df = df.rename(columns=rename_map)
        
        required = ['name', 'cost', 'price', 'discount']
        for c in required:
            if c not in df.columns: return pd.DataFrame()

        for c in ['cost', 'price', 'discount']:
            df[c] = df[c].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame()

df_products = load_data()

# ---------------------------------------------------------
# 5. 입력 및 계산 UI
# ---------------------------------------------------------
with st.container():
    st.write("🔻 **추가로 비교할 할인율을 선택하세요**")
    selected_rates = st.multiselect("할인율(%)", options=range(0, 95, 5), default=[])
    st.markdown("---")

def render_input_tab(tab_idx):
    mode = st.radio(f"입력 방식 ({tab_idx})", ["📝 직접 입력", "📂 DB 불러오기"], key=f"mode_{tab_idx}", label_visibility="collapsed")

    if mode == "📂 DB 불러오기":
        if df_products.empty:
            st.warning("데이터 파일 없음")
            return None
        
        # X 버튼으로 삭제 가능한 검색창
        sel = st.multiselect("제품 검색 (X 눌러서 삭제)", df_products['name'].tolist(), max_selections=1, key=f"search_{tab_idx}")
        
        if sel:
            name = sel[0]
            row = df_products[df_products['name'] == name].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("원가", f"{row['cost']:,}")
            c2.metric("정가", f"{row['price']:,}")
            c3.metric("DB 할인", f"{row['discount']}%")
            return {"type": "db", "name": name, "cost": row['cost'], "prices": [row['price']], "fixed_discount": row['discount']}
        return None
    else:
        name = st.text_input("제품명", key=f"n_{tab_idx}")
        cost = st.number_input("원가", step=1000, key=f"c_{tab_idx}")
        c1, c2, c3 = st.columns(3)
        p1 = c1.number_input("정가 A", step=1000, key=f"p1_{tab_idx}")
        p2 = c2.number_input("정가 B", step=1000, key=f"p2_{tab_idx}")
        p3 = c3.number_input("정가 C", step=1000, key=f"p3_{tab_idx}")
        if cost:
            prices = [p for p in [p1, p2, p3] if p]
            if prices: return {"type": "manual", "name": name or f"제품{tab_idx}", "cost": cost, "prices": prices, "fixed_discount": None}
    return None

t1, t2, t3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
items = []
with t1: 
    if (r:=render_input_tab(1)): items.append(r)
with t2: 
    if (r:=render_input_tab(2)): items.append(r)
with t3: 
    if (r:=render_input_tab(3)): items.append(r)

# ---------------------------------------------------------
# 6. 계산 실행
# ---------------------------------------------------------
if st.button("🚀 수익성 분석 실행", type="primary"):
    if not items:
        st.warning("제품을 선택해주세요.")
    else:
        rows = []
        base_fee = 0.28
        user_rates = sorted(selected_rates)
        
        for it in items:
            rates = sorted(list({it['fixed_discount']} | set(user_rates))) if it['type'] == 'db' else (user_rates if user_rates else [0])
            for p in it['prices']:
                if p == 0: continue
                for r in rates:
                    dr = r/100
                    fee_rate = base_fee if dr <= 0.09 else (base_fee-0.01 if dr <= 0.19 else (base_fee-0.02 if dr <= 0.29 else base_fee-0.03))
                    sell = p * (1-dr)
                    fee = sell * fee_rate
                    profit = sell - it['cost'] - fee
                    margin = (profit/sell*100) if sell else 0
                    roi = (profit/it['cost']*100) if it['cost'] else 0
                    rows.append({"제품명":it['name'], "수수료":f"{int(fee_rate*100)}%", "할인":r, "정가":int(p), "판매가":int(sell), "원가":int(it['cost']), "이익":int(profit), "ROI":roi, "마진":margin})
        
        if rows:
            dres = pd.DataFrame(rows).sort_values(['제품명', '할인'])
            def color_margin(val):
                c = '#FF4500' if val < 20 else ('#808080' if val < 31 else ('#228B22' if val <= 35 else '#1E90FF'))
                return f'color: {c}; font-weight: bold'
            
            st.success("분석 완료!")
            st.dataframe(
                dres.style.map(color_margin, subset=['마진']).format({'원가': '{:,}', '정가': '{:,}', '할인': '{}%', '판매가': '{:,}', '이익': '{:,}', '마진': '{:.1f}%', 'ROI': '{:.0f}%'}),
                use_container_width=True, hide_index=True
            )
