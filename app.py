import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="브랜디드 수익성 계산기", layout="wide")

# 스타일 조정 (모바일 최적화)
st.markdown(\"\"\"
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    </style>
\"\"\", unsafe_allow_html=True)

st.title("📊 수익성 분석기 (Mobile)")
st.caption("원가와 정가안을 입력하면 수수료/마진을 자동 분석합니다.")

# 입력 폼
with st.container():
    p_name = st.text_input("제품명", "25SS 옥스포드 셔츠")
    cost = st.number_input("원가 (원)", value=18000, step=1000, format="%d")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: p1 = st.number_input("정가안 A", value=39000, step=1000, format="%d")
    with col2: p2 = st.number_input("정가안 B", value=45000, step=1000, format="%d")
    with col3: p3 = st.number_input("정가안 C", value=49000, step=1000, format="%d")

# 계산 로직
def calculate(product_name, cost_price, list_prices):
    discount_steps = [0, 5, 10, 15, 20, 25, 30, 35]
    base_fee = 0.28
    results = []

    for price in list_prices:
        for dc_percent in discount_steps:
            discount_rate = dc_percent / 100.0
            
            # 수수료 구간 할인 로직
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
            
            if sell_price > 0:
                margin_rate = (profit / sell_price) * 100 
            else:
                margin_rate = 0
            
            roi = (profit / cost_price) * 100 if cost_price > 0 else 0
            
            results.append({
                "정가": f"{price//1000}k",  # 모바일용 축약 (39000 -> 39k)
                "할인": f"{dc_percent}%",
                "수수료": fee_note,
                "판매가": f"{int(sell_price):,}",
                "이익": f"{int(profit):,}",     # '실제 수익' 축약
                "마진": f"{margin_rate:.1f}%", # '마진율' 축약
                "ROI": f"{roi:.0f}%"
            })
    return pd.DataFrame(results)

# 실행 버튼
if st.button("분석 결과 보기 (터치)"):
    df = calculate(p_name, cost, [p1, p2, p3])
    
    st.success(f"✅ [{p_name}] 분석 완료")
    
    # 모바일 보기 좋게 출력
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    st.info("💡 팁: 표의 맨 윗줄(헤더)을 누르면 정렬됩니다.")
