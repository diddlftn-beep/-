import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
current_version = "v6.2 (Cache Reset + Fix)"
st.set_page_config(
    page_title=f"수익성 분석기 {current_version}", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 🔒 보안 구역
# ---------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("## 🔒 관계자 외 접근 금지")
    st.info("데이터 보호를 위해 비밀번호를 입력해주세요.")
    
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
# 🔓 메인 프로그램 시작
# =========================================================

# 로그아웃 함수
def logout():
    st.session_state.password_correct = False
    st.rerun()

# 상단 UI
col_title, col_logout = st.columns([8, 2])
with col_title:
    st.title("📊 멀티 수익성 분석기")
    st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")
with col_logout:
    st.write("")
    if st.button("🔒 로그아웃", use_container_width=True):
        logout()

st.divider()

# 사이드바
with st.sidebar:
    st.success(f"✅ 로그인됨 ({current_version})")
    if st.button("사이드바 로그아웃"):
        logout()

# ---------------------------------------------------------
# 3. 데이터 로딩 (강력한 오류 방지 적용)
# ---------------------------------------------------------
@st.cache_data
def load_data_v6_2():  # 함수 이름을 바꿔서 기존 캐시를 강제 초기화합니다.
    file_path = "products.csv"
    
    # 1. 파일 존재 확인
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        # 2. 인코딩 자동 감지 시도 (utf-8-sig는 엑셀 CSV의 BOM 처리용)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp949') # 한글 윈도우 호환
        
        # 3. 컬럼명 정리 (공백 제거)
        df.columns = df.columns.str.strip().str.replace(" ", "")
        
        # 4. 한글 컬럼명을 영어로 변환 (매핑 테이블)
        rename_map = {
            '상품명': 'name', 
            '원가': 'cost', 
            '판매가': 'price', '정가': 'price', 
            '할인율': 'discount'
        }
        df.rename(columns=rename_map, inplace=True)
        
        # 5. 필수 컬럼 확인 (없으면 생성)
        if 'name' not in df.columns:
            # 만약 이름 매핑이 실패했다면, 강제로 순서대로 이름을 붙입니다 (최후의 수단)
            if len(df.columns) >= 4:
                # 0:이름, 1:원가, 2:가격, 3:할인율 이라고 가정
                df.columns.values[0] = 'name'
                df.columns.values[1] = 'cost'
                df.columns.values[2] = 'price'
                df.columns.values[3] = 'discount'
        
        # 6. 숫자 변환 (콤마 제거 및 정수화)
        for col in ['cost', 'price', 'discount']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
            else:
                df[col] = 0 # 컬럼이 없으면 0으로 채움
                
        return df
        
    except Exception as e:
        st.error(f"❌ 데이터 로딩 중 치명적 오류: {e}")
        return pd.DataFrame()

df_products = load_data_v6_2()

# ---------------------------------------------------------
# 4. 화면 구성 및 입력
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; font-weight: bold; }
    th, td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.write("🔻 **비교할 추가 할인율 선택**")
selected_rates = st.multiselect("할인율(%)", options=range(0, 95, 5), default=[])
st.write("")

def render_input_tab(tab_idx):
    mode = st.radio(f"입력 방식 ({tab_idx})", ["📝 직접 입력", "📂 DB 불러오기"], key=f"mode_{tab_idx}", label_visibility="collapsed")

    if mode == "📂 DB 불러오기":
        if df_products.empty or 'name' not in df_products.columns:
            st.warning("데이터 파일을 읽을 수 없거나 형식이 올바르지 않습니다.")
            return None
        
        # [수정] 검색창 (X 버튼으로 삭제 가능)
        sel = st.multiselect(
            "제품 검색", 
            df_products['name'].tolist(), 
            max_selections=1, 
            key=f"search_{tab_idx}",
            placeholder="제품명을 입력하세요"
        )
        
        if sel:
            name = sel[0]
            # 해당 제품 정보 가져오기
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
            if prices: 
                return {"type": "manual", "name": name or f"제품{tab_idx}", "cost": cost, "prices": prices, "fixed_discount": None}
    return None

t1, t2, t3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
items = []
with t1: 
    if (r:=render_input_tab(1)): items.append(r)
with t2: 
    if (r:=render_input_tab(2)): items.append(r)
with t3: 
    if (r:=render_input_tab(3)): items.append(r)

st.markdown("---")

# ---------------------------------------------------------
# 5. 계산 실행
# ---------------------------------------------------------
if st.button("🚀 수익성 분석 실행", type="primary", use_container_width=True):
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
