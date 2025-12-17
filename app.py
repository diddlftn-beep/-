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

st.title("📊 멀티 수익성 분석기")
st.caption("제품 3개까지 한 번에 비교 분석 가능합니다.")

# ---------------------------------------------------------
# 1. 할인율 선택 기능 (멀티 셀렉트)
# ---------------------------------------------------------
with st.container():
    st.write("🔻 **보고 싶은 할인율을 선택하세요** (삭제/추가 가능)")
    default_rates = [0, 5, 10, 15, 20, 25, 30, 35]
    selected_rates = st.multiselect(
        "할인율 선택", 
        options=range(0, 95, 5), # 0~90%까지 5단위
        default=default_rates
    )
    st.markdown("---")

# ---------------------------------------------------------
# 2. 제품 정보 입력 (탭으로 구분)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])

products = [] # 입력된 제품 정보를 담을 리스트

# 제품 1 입력
with tab1:
    p1_name = st.text_input("제품명 (1)", placeholder="예: 옥스포드 셔츠", key="n1")
    p1_cost = st.number_input("원가 (1)", value=None, step=1000, format="%d", key="c1")
    col1, col2, col3 = st.columns(3)
    with col1: p1_p1 = st.number_input("정가안 A", value=None, step=1000, format="%d", key="p1_1")
    with col2: p1_p2 = st.number_input("정가안 B", value=None, step=1000, format="%d", key="p1_2")
    with col3: p1_p3 = st.number_input("정가안 C", value=None, step=1000, format="%d", key="p1_3")
    
    # 입력 확인 후 리스트에 추가
    if p1_cost is not None:
        valid_prices = [p for p in [p1_p1, p1_p2, p1_p3] if p is not None]
        if valid_prices:
            products.append({"name": p1_name if p1_name else "제품1", "cost": p1_cost, "prices": valid_prices})

# 제품 2 입력
with tab2:
    p2_name = st.text_input("제품명 (2)", placeholder="예: 데님 팬츠", key="n2")
    p2_cost = st.number_input("원가 (2)", value=None, step=1000, format="%d", key="c2")
    col1, col2, col3 = st.columns(3)
    with col1: p2_p1 = st.number_input("정가안 A", value=None, step=1000, format="%d", key="p2_1")
    with col2: p2_p2 = st.number_input("정가안 B", value=None, step=1000, format="%d", key="p2_2")
    with col3: p2_p3 = st.number_input("정가안 C", value=None, step=1000, format="%d", key="p2_3")

    if p2_cost is not None:
        valid_prices = [p for p in [p2_p1, p2_p2, p2_p3] if p is not None]
        if valid_prices:
            products.append({"name": p2_name if p2_name else "제품2", "cost": p2_cost, "prices": valid_prices})

# 제품 3 입력
with tab3:
    p3_name = st.text_input("제품명 (3)", placeholder="예: 니트 베스트", key="n3")
    p3_cost = st.number_input("원가 (3)", value=None, step=1000, format="%d", key="c3")
    col1, col2, col3 = st.columns(3)
    with col1: p3_p1 = st.number_input("정가안 A", value=None, step=1000, format="%d", key="p3_1")
    with col2: p3_p2 = st.number_input("정가안 B", value=None, step=1000, format="%d", key="p3_2")
    with col3: p3_p3 = st.number_input("정가안 C", value=None, step=1000, format="%d", key="p3_3")

    if p3_cost is not None:
        valid_prices = [p for p in [p3_p1, p3_p2, p3_p3] if p is not None]
        if valid_prices:
            products.append({"name": p3_name if p3_name else "제품3", "cost": p3_cost, "prices": valid_prices})


# ---------------------------------------------------------
# 3. 계산 로직 (선택된 할인율만 반영)
# ---------------------------------------------------------
def calculate_all(product_list, rates):
    base_fee = 0.28
    results = []
    
    # 선택된 할인율 정렬
    rates.sort()

    for item in product_list:
        p_name = item['name']
        cost_price = item['cost']
        
        for price in item['prices']:
            for dc_percent in rates:
                discount_rate = dc_percent / 100.0
                
                # 수수료 구간
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
                    "원가": cost_price, # 원가 항목 추가
                    "정가": int(price),
                    "할인": dc_percent,
                    "수수료": fee_note,
                    "판매가": int(sell_price),
                    "이익": int(profit),
                    "마진": margin_rate,
                    "ROI": roi
                })
    return pd.DataFrame(results)

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
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "원가": st.column_config.NumberColumn(format="%d"),
                "정가": st.column_config.NumberColumn(format="%d"),
                "할인": st.column_config.NumberColumn(format="%d%%"),
                "판매가": st.column_config.NumberColumn(format="%d"),
                "이익": st.column_config.NumberColumn(format="%d"),
                "마진": st.column_config.NumberColumn(format="%.1f%%"),
                "ROI": st.column_config.NumberColumn(format="%.0f%%"),
            }
        )
        st.info("💡 팁: '제품명' 헤더를 누르면 제품별로 모아볼 수 있습니다.")
