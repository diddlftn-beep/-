import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="브랜디드 수익성 계산기", layout="wide")

# 스타일 조정
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 멀티 수익성 분석기 (컬러 적용됨)")
st.caption("마진율에 따라 색상이 자동 변경됩니다. (파랑 > 초록 > 회색 > 주황 > 빨강)")

# ---------------------------------------------------------
# 1. 할인율 선택 기능
# ---------------------------------------------------------
with st.container():
    st.write("🔻 **보고 싶은 할인율 선택**")
    default_rates = [0, 5, 10, 15, 20, 25, 30, 35]
    selected_rates = st.multiselect(
        "할인율(%)", 
        options=range(0, 95, 5), 
        default=default_rates
    )
    st.markdown("---")

# ---------------------------------------------------------
# 2. 제품 정보 입력 (탭 구분)
# ---------------------------------------------------------
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
    with col3: p2_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="p2_3")

    if p2_cost is not None:
        valid_prices = [p for p in [p2_p1, p2_p2, p2_p3] if p is not None]
        if valid_prices:
            products.append({"name": p2_name if p2_name else "제품2", "cost": p2_cost, "prices": valid_prices})

with tab3:
    p3_name = st.text_input("제품명 (3)", placeholder="예: 니트 베스트", key="n3")
    p3_cost = st.number_input("원가 (3)", value=None, step=1000, format="%d", key="c3")
    col1, col2, col3 = st.columns(3)
    with col1: p3_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="p3_1")
    with col2: p3_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="p3_2")
    with col3: p3_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="p3_3")

    if p3_cost is not None:
        valid_prices = [p for p in [p3_p1, p3_p2, p3_p3] if p is not None]
        if valid_prices:
            products.append({"name": p3_name if p3_name else "제품3", "cost": p3_cost, "prices": valid_prices})


# ---------------------------------------------------------
# 3. 계산 및 색상 로직
# ---------------------------------------------------------
def calculate_all(product_list, rates):
    base_fee = 0.28
    results = []
    rates.sort()

    for item in product_list:
        p_name = item['name']
        cost_price = item['cost']
        
        for price in item['prices']:
            for dc_percent in rates:
                discount_rate = dc_percent / 100.0
                
                if discount_rate <= 0.09:       
                    applied_fee_rate = base_fee; fee_note = "28%"
                elif discount_rate <= 0.19:     
                    applied_fee_rate = base_fee - 0.01; fee_note = "27%"
                elif discount_rate <= 0.29:     
                    applied_fee_rate = base_fee - 0.02; fee_note = "26%"
                else:                           
                    applied_fee_rate = base_fee - 0.03; fee_note = "25%"

                sell_price = price * (1 - discount_rate)
                fee = sell_price * applied_fee_rate
                profit = sell_price - cost_price - fee
                
                margin_rate = (profit / sell_price) * 100 if sell_price > 0 else 0
                roi = (profit / cost_price) * 100 if cost_price > 0 else 0
                
                results.append({
                    "제품명": p_name,
                    "원가": cost_price,
                    "정가": int(price),
                    "할인": dc_percent,
                    "수수료": fee_note,
                    "판매가": int(sell_price),
                    "이익": int(profit),
                    "마진": margin_rate,
                    "ROI": roi
                })
    return pd.DataFrame(results)

# 색상 적용 함수
def color_margin_rows(val):
    color = ''
    weight = 'bold'
    if val > 35:
        color = '#1E90FF' # 파랑 (DodgerBlue)
    elif 31 <= val <= 35:
        color = '#228B22' # 초록 (ForestGreen)
    elif 25 <= val < 31:
        color = '#808080' # 회색 (Gray)
    elif 20 <= val < 25:
        color = '#FF8C00' # 주황 (DarkOrange)
    else: # 20 미만
        color = '#FF4500' # 빨강 (OrangeRed)
    
    return f'color: {color}; font-weight: {weight}'

# ---------------------------------------------------------
# 4. 실행 및 출력
# ---------------------------------------------------------
if st.button("분석 결과 보기 (터치)"):
    if not products:
        st.error("⚠️ 최소한 하나의 제품 정보(원가, 정가)를 입력해주세요!")
    elif not selected_rates:
        st.error("⚠️ 할인율을 적어도 하나 선택해주세요!")
    else:
        df = calculate_all(products, selected_rates)
        st.success(f"✅ 총 {len(products)}개 제품 분석 완료")
        
        # 데이터프레임 스타일 적용 (색상 입히기)
        # map 함수를 통해 마진 컬럼에 색상 규칙 적용
        styled_df = df.style.map(color_margin_rows, subset=['마진'])\
            .format({
                '원가': '{:,}',
                '정가': '{:,}',
                '할인': '{}%',
                '판매가': '{:,}',
                '이익': '{:,}',
                '마진': '{:.1f}%',
                'ROI': '{:.0f}%'
            })
            
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        st.caption("※ 마진율 색상: 🔵35%초과 🟢31~35% ⚪25~31% 🟠20~25% 🔴20%미만")
