import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="브랜디드 수익성 계산기", layout="wide")

# 스타일 조정 (모바일 최적화)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 수익성 분석기 (정렬 패치됨)")
st.caption("헤더를 누르면 이제 숫자가 올바르게 정렬됩니다.")

# 입력 폼
with st.container():
    p_name = st.text_input("제품명", placeholder="예: 25SS 옥스포드 셔츠")
    cost = st.number_input("원가 (원)", value=None, step=1000, format="%d", placeholder="원가를 입력하세요")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: p1 = st.number_input("정가안 A", value=None, step=1000, format="%d", placeholder="가격 A")
    with col2: p2 = st.number_input("정가안 B", value=None, step=1000, format="%d", placeholder="가격 B")
    with col3: p3 = st.number_input("정가안 C", value=None, step=1000, format="%d", placeholder="가격 C")

# 계산 로직
def calculate(product_name, cost_price, list_prices):
    discount_steps = [0, 5, 10, 15, 20, 25, 30, 35]
    base_fee = 0.28
    results = []

    for price in list_prices:
        if price is None: continue
            
        for dc_percent in discount_steps:
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
                "정가": int(price),     # 숫자 그대로 저장
                "할인": dc_percent,     # 숫자 5, 10 저장 (5% 아님)
                "수수료": fee_note,
                "판매가": int(sell_price), # 숫자
                "이익": int(profit),      # 숫자
                "마진": margin_rate,      # 숫자
                "ROI": roi                # 숫자
            })
    return pd.DataFrame(results)

# 실행 버튼
if st.button("분석 결과 보기 (터치)"):
    if cost is None:
        st.error("⚠️ 원가를 입력해주세요!")
    elif p1 is None and p2 is None and p3 is None:
        st.error("⚠️ 정가안을 적어도 하나는 입력해주세요!")
    else:
        valid_prices = [p for p in [p1, p2, p3] if p is not None]
        if not p_name: p_name = "제품"
            
        df = calculate(p_name, cost, valid_prices)
        st.success(f"✅ [{p_name}] 분석 완료")
        
        # 여기서 숫자를 보기 좋게 꾸며줍니다 (정렬은 숫자로, 보이는 건 %로)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "정가": st.column_config.NumberColumn(format="%d"),
                "할인": st.column_config.NumberColumn(format="%d%%"), # 숫자 5를 5%로 보여줌
                "판매가": st.column_config.NumberColumn(format="%d"),
                "이익": st.column_config.NumberColumn(format="%d"),
                "마진": st.column_config.NumberColumn(format="%.1f%%"),
                "ROI": st.column_config.NumberColumn(format="%.0f%%"),
            }
        )
        st.info("💡 이제 할인, 이익, 마진 헤더를 누르면 크기순으로 정확하게 정렬됩니다.")
