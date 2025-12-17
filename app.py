import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="수익성 분석기 v8.0 (Emergency Mode)", 
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

    st.markdown("## 🔒 접속 권한 확인")
    password_input = st.text_input("비밀번호", type="password")

    if password_input:
        # secrets가 설정 안 되어 있을 경우를 대비한 예외 처리
        try:
            if password_input == st.secrets["password"]:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ 비밀번호 불일치")
        except:
            # secrets 설정이 없으면 임시로 1234로 통과 (비상 조치)
            if password_input == "1234":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.warning("⚠️ Streamlit Secrets 설정이 확인되지 않습니다. 임시 비번(1234) 시도 혹은 설정 확인 필요.")
    return False

if not check_password():
    st.stop()

# =========================================================
# 🔓 메인 프로그램
# =========================================================

# 로그아웃 버튼 (사이드바 & 메인)
if st.sidebar.button("🔒 로그아웃"):
    st.session_state.password_correct = False
    st.rerun()

st.title("📊 수익성 분석기 (캐시 미사용 모드)")
st.caption("현재 데이터 로딩 오류 해결을 위해 '캐시 기능'을 껐습니다.")

# ---------------------------------------------------------
# 3. 데이터 로딩 (캐시 제거 + 무조건 읽기)
# ---------------------------------------------------------
# [중요] @st.cache_data 데코레이터를 지웠습니다. (캐시 무시)
def load_data_emergency():
    file_path = "products.csv"
    
    if not os.path.exists(file_path):
        st.error("🚨 'products.csv' 파일이 없습니다. 깃허브에 파일이 올라갔는지 확인하세요.")
        return pd.DataFrame()
    
    try:
        # 인코딩 자동 시도
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp949')
        
        # [핵심] 컬럼 이름이 뭐든 상관없이 순서대로 강제 할당
        # CSV 파일 순서가 [상품명, 원가, 정가, 할인율] 이라고 가정
        if len(df.columns) >= 4:
            df.columns.values[0] = 'name'
            df.columns.values[1] = 'cost'
            df.columns.values[2] = 'price'
            df.columns.values[3] = 'discount'
        else:
            st.error(f"🚨 CSV 파일의 데이터 칸 수가 부족합니다. (현재 {len(df.columns)}칸)")
            st.write("인식된 데이터 예시:", df.head())
            return pd.DataFrame()

        # 숫자 변환 (콤마 제거 등)
        for col in ['cost', 'price', 'discount']:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
        return df
        
    except Exception as e:
        st.error(f"🚨 데이터 읽기 실패: {e}")
        return pd.DataFrame()

df_products = load_data_emergency()

# ---------------------------------------------------------
# 4. UI 및 기능
# ---------------------------------------------------------
st.divider()

# 할인율 선택
selected_rates = st.multiselect("추가 비교 할인율(%)", options=range(0, 95, 5))

# 입력 탭
def render_tab(idx):
    mode = st.radio(f"입력 {idx}", ["DB 선택", "직접 입력"], key=f"m{idx}", label_visibility="collapsed")
    
    if mode == "DB 선택":
        if df_products.empty:
            st.warning("데이터가 없습니다.")
            return None
            
        sel = st.multiselect("제품 검색", df_products['name'].tolist(), max_selections=1, key=f"s{idx}", placeholder="제품명 검색")
        if sel:
            row = df_products[df_products['name'] == sel[0]].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("원가", f"{row['cost']:,}")
            c2.metric("정가", f"{row['price']:,}")
            c3.metric("기본 할인", f"{row['discount']}%")
            return {"type": "db", "name": sel[0], "cost": row['cost'], "prices": [row['price']], "fixed_discount": row['discount']}
    else:
        name = st.text_input("상품명", key=f"nm{idx}")
        cost = st.number_input("원가", step=1000, key=f"ct{idx}")
        price = st.number_input("정가", step=1000, key=f"pr{idx}")
        if cost and price:
            return {"type": "manual", "name": name or f"제품{idx}", "cost": cost, "prices": [price], "fixed_discount": None}
    return None

cols = st.columns(3)
items = []
for i, col in enumerate(cols):
    with col:
        st.subheader(f"🛒 제품 {i+1}")
        if (item := render_tab(i+1)):
            items.append(item)

st.markdown("---")

if st.button("🚀 분석 실행", type="primary", use_container_width=True):
    if not items:
        st.warning("제품을 하나 이상 선택하세요.")
    else:
        rows = []
        for it in items:
            rates = sorted(list({it['fixed_discount']} | set(selected_rates))) if it['type'] == 'db' else (selected_rates if selected_rates else [0])
            for p in it['prices']:
                for r in rates:
                    dr = r/100
                    # 수수료 구간
                    fee_rate = 0.28 if dr <= 0.09 else (0.27 if dr <= 0.19 else (0.26 if dr <= 0.29 else 0.25))
                    
                    sell = p * (1-dr)
                    fee = sell * fee_rate
                    profit = sell - it['cost'] - fee
                    margin = (profit/sell*100) if sell else 0
                    
                    rows.append({
                        "제품명": it['name'], "수수료": f"{int(fee_rate*100)}%", "할인": f"{r}%",
                        "정가": int(p), "판매가": int(sell), "원가": int(it['cost']),
                        "이익": int(profit), "마진": margin
                    })
        
        dres = pd.DataFrame(rows).sort_values(['제품명', '할인'])
        
        def color_map(val):
            c = '#FF4500' if val < 20 else ('#808080' if val < 31 else ('#228B22' if val <= 35 else '#1E90FF'))
            return f'color: {c}; font-weight: bold'

        st.dataframe(
            dres.style.map(color_map, subset=['마진']).format({
                '원가':'{:,}','정가':'{:,}','판매가':'{:,}','이익':'{:,}','마진':'{:.1f}%'
            }), 
            use_container_width=True, hide_index=True
        )
