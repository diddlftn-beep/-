import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
current_version = "v7.0 (Debug Fix)"
st.set_page_config(
    page_title=f"수익성 분석기 {current_version}", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 🔒 보안 구역 (로그인)
# ---------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("## 🔒 관계자 외 접근 금지")
    
    # 비밀번호 입력
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
# 🔓 메인 프로그램 (로그인 성공 시)
# =========================================================

def logout():
    st.session_state.password_correct = False
    st.rerun()

# 상단 로그아웃 버튼
col_t, col_l = st.columns([8,2])
with col_t:
    st.title("📊 수익성 분석기 (진단 모드)")
with col_l:
    st.write("")
    if st.button("🔒 로그아웃"): logout()

st.divider()

# ---------------------------------------------------------
# 3. 데이터 로딩 (진단 기능 포함)
# ---------------------------------------------------------
# 캐시를 쓰지 않고 매번 새로 읽도록 설정 (문제 해결용)
def load_data_debug():
    file_path = "products.csv"
    
    if not os.path.exists(file_path):
        st.error("❌ 'products.csv' 파일이 없습니다. 깃허브에 파일이 있는지 확인하세요.")
        return pd.DataFrame()
    
    df = None
    # 1. 인코딩 시도 (utf-8-sig -> cp949 -> utf-8)
    encodings = ['utf-8-sig', 'cp949', 'utf-8']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break # 성공하면 중단
        except:
            continue
            
    if df is None:
        st.error("❌ 파일을 읽을 수 없습니다 (인코딩 오류). CSV 파일을 'UTF-8' 형식으로 다시 저장해주세요.")
        return pd.DataFrame()

    # 2. 컬럼명 정리 (공백 제거)
    df.columns = df.columns.str.strip().str.replace(" ", "")
    
    # 3. 현재 컬럼명 확인 (디버깅용 출력)
    # st.warning(f"🛠️ 현재 파일의 컬럼 목록: {list(df.columns)}") 

    # 4. 컬럼명 매핑 (한글 -> 영어)
    rename_map = {
        '상품명': 'name', '원가': 'cost', 
        '판매가': 'price', '정가': 'price', 
        '할인율': 'discount'
    }
    df.rename(columns=rename_map, inplace=True)

    # 5. 필수 컬럼 검사
    required = ['name', 'cost', 'price', 'discount']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        st.error(f"❌ 데이터 형식 오류! 다음 항목을 찾을 수 없습니다: {missing}")
        st.info(f"현재 인식된 항목: {list(df.columns)}")
        st.stop() # 여기서 멈춤

    # 6. 숫자 변환
    try:
        for col in ['cost', 'price', 'discount']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
    except Exception as e:
        st.error(f"❌ 숫자 변환 오류: {e}")
        st.stop()

    return df

df_products = load_data_debug()

# ---------------------------------------------------------
# 4. 화면 구성
# ---------------------------------------------------------
st.markdown("""
    <style> .stButton>button { border-radius: 8px; font-weight: bold; } </style>
""", unsafe_allow_html=True)

selected_rates = st.multiselect("추가 할인율(%)", options=range(0, 95, 5))
st.write("")

def render_tab(idx):
    mode = st.radio(f"방식{idx}", ["직접 입력", "DB 불러오기"], key=f"m{idx}", label_visibility="collapsed")
    
    if mode == "DB 불러오기":
        sel = st.multiselect("제품 검색", df_products['name'].tolist(), max_selections=1, key=f"s{idx}")
        if sel:
            row = df_products[df_products['name'] == sel[0]].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("원가", f"{row['cost']:,}")
            c2.metric("정가", f"{row['price']:,}")
            c3.metric("할인", f"{row['discount']}%")
            return {"type": "db", "name": sel[0], "cost": row['cost'], "prices": [row['price']], "fixed_discount": row['discount']}
    else:
        name = st.text_input("이름", key=f"nm{idx}")
        cost = st.number_input("원가", step=1000, key=f"ct{idx}")
        p1 = st.number_input("정가", step=1000, key=f"pr{idx}")
        if cost and p1:
            return {"type": "manual", "name": name or f"제품{idx}", "cost": cost, "prices": [p1], "fixed_discount": None}
    return None

t1, t2, t3 = st.tabs(["제품 1", "제품 2", "제품 3"])
items = []
with t1: 
    if (r:=render_tab(1)): items.append(r)
with t2: 
    if (r:=render_tab(2)): items.append(r)
with t3: 
    if (r:=render_tab(3)): items.append(r)

st.markdown("---")

if st.button("🚀 분석 실행", type="primary", use_container_width=True):
    if not items:
        st.warning("제품을 선택하세요.")
    else:
        rows = []
        for it in items:
            rates = sorted(list({it['fixed_discount']} | set(selected_rates))) if it['type'] == 'db' else (selected_rates if selected_rates else [0])
            for p in it['prices']:
                for r in rates:
                    dr = r/100
                    fee_rate = 0.28 if dr <= 0.09 else (0.27 if dr <= 0.19 else (0.26 if dr <= 0.29 else 0.25))
                    sell = p * (1-dr)
                    profit = sell - it['cost'] - (sell * fee_rate)
                    rows.append({
                        "제품명": it['name'], "수수료": f"{int(fee_rate*100)}%", "할인": r,
                        "정가": int(p), "판매가": int(sell), "원가": int(it['cost']),
                        "이익": int(profit), "마진": (profit/sell*100) if sell else 0
                    })
        
        dres = pd.DataFrame(rows).sort_values(['제품명', '할인'])
        st.dataframe(dres.style.format({'원가':'{:,}','정가':'{:,}','판매가':'{:,}','이익':'{:,}','마진':'{:.1f}%'}), use_container_width=True, hide_index=True)
