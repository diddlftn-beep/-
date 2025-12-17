import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 버전 관리 & 설정
# ---------------------------------------------------------
current_version = "v3.1 (Bug Fix)"
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
    # 파일이 있는지 확인
    if not os.path.exists("products.csv"):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        # CSV 파일 읽기
        df = pd.read_csv("products.csv")
        # 컬럼 이름 공백 제거
        df.columns = df.columns.str.strip()
        # 숫자가 아닌 문자 제거 (콤마 등) 및 숫자 변환
        for col in ['cost', 'price', 'discount']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"데이터 파일(products.csv)을 읽는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 데이터 로드
df_products = load_data()

# ---------------------------------------------------------
# 3. 메인 화면
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 할인율 선택 (직접 입력 모드용)
with st.container():
    st.write("🔻 **[직접 입력] 모드일 때 비교할 할인율**")
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
            st.warning("products.csv 파일이 비어있거나 없습니다.")
            return None
            
        # 검색 기능이 포함된 선택박스
        options = df_products['name'].tolist()
        selection = st.selectbox("제품 검색 및 선택", options, key=f"sel_{tab_idx}")
        
        # 선택된 데이터 찾기
        row = df_products[df_products['name'] == selection].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("원가", f"{row['cost']:,}원")
        c2.metric("정가", f"{row['price']:,}원")
        c3.metric("할인율", f"{row['discount']}%")
        
        return {
            "type": "db",
            "name": selection,
            "cost": row['cost'],
            "prices": [row['price']],
            "fixed_discount": row['discount']
        }

    else:
        # 직접 입력
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
# 4. 계산 로직 (수정됨)
# ---------------------------------------------------------
def calculate_all(product_list, manual_rates):
    base_fee = 0.28
    results = []
    manual_rates.sort()

    for item in product_list:
        if item['type'] == 'db':
            target_rates = [item['fixed_discount']]
        else:
            target_rates = manual_rates if manual_rates else [0] # 할인율 미선택시 0%

        for price in item['prices']:
            if price == 0: continue # 정가 0원이면 패스
            for dc_percent in target_rates:
                discount_rate = dc_percent / 100.0
                # 수수료
                if discount_rate <= 0.09: applied_fee_rate = base_fee; fee_note = "28%"
                elif discount_rate <= 0.19: applied_fee_rate = base_fee - 0.01; fee_note = "27%"
                elif discount_rate <= 0.29: applied_fee_rate = base_fee - 0.02; fee_note = "26%"
                else: applied_fee_rate = base_fee - 0.03; fee_note = "25%"

                sell_price = price * (1 - discount_rate)
                fee = sell_price * applied_fee_rate
                
                # --- [수정 완료] 이전 코드의 잔재(cost_price) 제거됨 ---
                profit = sell_price - item['cost'] - fee

                margin_rate = (profit / sell_price) * 100 if sell_price > 0 else 0
                roi = (profit / item['cost']) * 100 if item['cost'] > 0 else 0
                
                results.append({
                    "제품명": item['name'],
                    "수수료": fee_note,
                    "할인": dc_percent,     
                    "정가": int(price),
                    "판매가": int(sell_price),
                    "원가": int(item['cost']),
                    "이익": int(profit),
                    "ROI": roi,
                    "마진": margin_rate
                })
    
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by=['제품명', '할인'])
        cols = ["제품명", "수수료", "할인", "정가", "판매가", "원가", "이익", "ROI", "마진"]
        df = df[cols]
    return df

def color_margin_rows(val):
    color = '#FF4500' # 기본 빨강
    if val > 35: color = '#1E90FF' 
    elif 31 <= val <= 35: color = '#228B22' 
    elif 25 <= val < 31: color = '#808080' 
    elif 20 <= val < 25: color = '#FF8C00' 
    return f'color: {color}; font-weight: bold'

if st.button("분석 결과 보기"):
    if not products_to_calc:
        st.error("입력된 제품이 없습니다.")
    else:
        df_res = calculate_all(products_to_calc, selected_rates)
        if not df_res.empty:
            st.success(f"✅ 총 {len(products_to_calc)}개 제품 분석 완료")
            st.dataframe(
                df_res.style.map(color_margin_rows, subset=['마진']).format({
                    '원가': '{:,}', '정가': '{:,}', '할인': '{}%', 
                    '판매가': '{:,}', '이익': '{:,}', 
                    '마진': '{:.1f}%', 'ROI': '{:.0f}%'
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.warning("결과를 계산할 수 없습니다 (정가가 0원이거나 정보 부족)")
