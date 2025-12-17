import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정 (무조건 맨 위)
# ---------------------------------------------------------
current_version = "vFinal (Production Ready)"
st.set_page_config(
    page_title=f"수익성 분석기 {current_version}", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 🔒 보안 구역 (비밀번호 체크)
# ---------------------------------------------------------
def check_password():
    """비밀번호가 맞으면 True, 아니면 False 반환"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # 로그인 화면
    st.markdown("## 🔒 접속 권한 확인")
    st.info("원가 데이터 보호를 위해 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호", type="password", key="password_input")

    if password_input:
        # Streamlit Secrets에 설정된 비번과 비교
        if password_input == st.secrets["password"]:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

    return False

# 비밀번호 틀리면 여기서 코드 실행 중단
if not check_password():
    st.stop()

# =========================================================
# 🔓 로그인 성공 후 실행되는 메인 프로그램
# =========================================================

# 로그아웃 함수
def logout():
    st.session_state.password_correct = False
    st.rerun()

# --- 사이드바 설정 ---
with st.sidebar:
    st.title("⚙️ 관리자 메뉴")
    st.success("✅ 인증 완료")
    st.write(f"버전: {current_version}")
    st.markdown("---")
    if st.button("🔒 로그아웃 (사이드바)", use_container_width=True):
        logout()

# --- 메인 상단바 ---
col_title, col_logout = st.columns([8, 2])
with col_title:
    st.title("📊 멀티 수익성 분석기")
    st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")
with col_logout:
    st.write("") 
    if st.button("🔒 로그아웃", key='top_logout', use_container_width=True):
        logout()

st.divider()

# ---------------------------------------------------------
# 3. 데이터 로딩 (안전 장치 포함)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "products.csv"
    
    # 1. 파일 존재 확인
    if not os.path.exists(file_path):
        # 파일이 없으면 빈 껍데기 반환 (에러 방지)
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        # 2. 인코딩 자동 감지 (한글 깨짐 방지)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp949')
        
        # 3. 컬럼명 공백 제거 및 소문자 변환
        df.columns = df.columns.str.strip().str.replace(" ", "").str.lower()
        
        # 4. 한글 컬럼명을 내부 로직용 영어로 변환
        rename_map = {
            '상품명': 'name', 
            '원가': 'cost', 
            '판매가': 'price', '정가': 'price', 
            '할인율': 'discount'
        }
        df.rename(columns=rename_map, inplace=True)
        
        # 5. 필수 컬럼 확인 (없으면 위치로 강제 매핑)
        if 'name' not in df.columns:
            if len(df.columns) >= 4:
                df.columns.values[0] = 'name'
                df.columns.values[1] = 'cost'
                df.columns.values[2] = 'price'
                df.columns.values[3] = 'discount'
            else:
                return pd.DataFrame() # 형식이 너무 다르면 빈 값 반환

        # 6. 숫자 데이터 변환 (콤마 제거)
        for col in ['cost', 'price', 'discount']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            else:
                df[col] = 0
                
        return df
        
    except Exception:
        return pd.DataFrame()

df_products = load_data()

# ---------------------------------------------------------
# 4. 스타일 및 입력 화면
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; font-weight: bold; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.write("🔻 **추가로 비교할 할인율을 선택하세요**")
selected_rates = st.multiselect("할인율(%)", options=range(0, 95, 5), default=[])
st.write("")

# 입력 탭 생성 함수
def render_input_tab(tab_idx):
    mode = st.radio(f"입력 방식 ({tab_idx})", ["📝 직접 입력", "📂 DB 불러오기"], key=f"mode_{tab_idx}", label_visibility="collapsed")

    if mode == "📂 DB 불러오기":
        if df_products.empty:
            st.warning("데이터 파일(products.csv)을 읽을 수 없습니다.")
            return None
        
        # [핵심] X 버튼으로 삭제 가능한 검색창 (Multiselect max=1)
        sel = st.multiselect(
            "제품 검색 (X 버튼으로 삭제)", 
            df_products['name'].tolist(), 
            max_selections=1, 
            key=f"search_{tab_idx}",
            placeholder="제품명을 입력하세요"
        )
        
        if sel:
            name = sel[0]
            row = df_products[df_products['name'] == name].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("원가", f"{row['cost']:,}원")
            c2.metric("정가", f"{row['price']:,}원")
            c3.metric("DB 할인", f"{row['discount']}%")
            
            return {
                "type": "db", 
                "name": name, 
                "cost": row['cost'], 
                "prices": [row['price']], 
                "fixed_discount": row['discount']
            }
        else:
            st.info("👆 제품을 검색해주세요.")
            return None

    else: # 직접 입력
        name = st.text_input("제품명", key=f"n_{tab_idx}")
        cost = st.number_input("원가", step=1000, key=f"c_{tab_idx}")
        
        c1, c2, c3 = st.columns(3)
        p1 = c1.number_input("정가 A", step=1000, key=f"p1_{tab_idx}")
        p2 = c2.number_input("정가 B", step=1000, key=f"p2_{tab_idx}")
        p3 = c3.number_input("정가 C", step=1000, key=f"p3_{tab_idx}")
        
        if cost:
            prices = [p for p in [p1, p2, p3] if p]
            if prices: 
                return {
                    "type": "manual", 
                    "name": name or f"제품{tab_idx}", 
                    "cost": cost, 
                    "prices": prices, 
                    "fixed_discount": None
                }
    return None

# 탭 배치
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
# 5. 계산 실행 및 결과 출력
# ---------------------------------------------------------
if st.button("🚀 수익성 분석 실행", type="primary", use_container_width=True):
    if not items:
        st.warning("제품을 하나 이상 선택하거나 입력해주세요.")
    else:
        rows = []
        base_fee = 0.28
        user_rates = sorted(selected_rates)
        
        for it in items:
            # DB 제품은 기본 할인율 포함, 직접 입력은 선택한 할인율만
            if it['type'] == 'db':
                rates = sorted(list({it['fixed_discount']} | set(user_rates)))
            else:
                rates = user_rates if user_rates else [0]

            for p in it['prices']:
                if p == 0: continue
                for r in rates:
                    dr = r / 100.0
                    # 수수료 구간 로직
                    if dr <= 0.09: fee_rate = base_fee; fee_note = "28%"
                    elif dr <= 0.19: fee_rate = base_fee - 0.01; fee_note = "27%"
                    elif dr <= 0.29: fee_rate = base_fee - 0.02; fee_note = "26%"
                    else: fee_rate = base_fee - 0.03; fee_note = "25%"

                    sell = p * (1 - dr)
                    fee = sell * fee_rate
                    profit = sell - it['cost'] - fee
                    
                    margin = (profit / sell * 100) if sell else 0
                    roi = (profit / it['cost'] * 100) if it['cost'] else 0
                    
                    rows.append({
                        "제품명": it['name'], 
                        "수수료": fee_note, 
                        "할인": f"{r}%",
                        "정가": int(p), 
                        "판매가": int(sell), 
                        "원가": int(it['cost']),
                        "이익": int(profit), 
                        "ROI": roi,
                        "마진": margin
                    })
        
        if rows:
            dres = pd.DataFrame(rows).sort_values(['제품명', '할인'])
            
            # 마진율에 따른 색상 함수
            def color_margin(val):
                if val > 35: color = '#1E90FF' # 파랑
                elif 31 <= val <= 35: color = '#228B22' # 초록
                elif 25 <= val < 31: color = '#808080' # 회색
                elif 20 <= val < 25: color = '#FF8C00' # 주황
                else: color = '#FF4500' # 빨강
                return f'color: {color}; font-weight: bold'
            
            st.success(f"총 {len(rows)}개의 시나리오 분석 완료!")
            st.dataframe(
                dres.style.map(color_margin, subset=['마진']).format({
                    '원가': '{:,}', '정가': '{:,}', 
                    '판매가': '{:,}', '이익': '{:,}', 
                    '마진': '{:.1f}%', 'ROI': '{:.0f}%'
                }),
                use_container_width=True, 
                hide_index=True
            )
