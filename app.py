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

st.title("📊 수익성 분석기 (Mobile)")
st.caption("원가와 정가안을 입력하면 수수료/마진을 자동 분석합니다.")

# 입력 폼
with st.container():
    # value=None으로 설정하면 빈칸이 됩니다. placeholder는 흐릿한 안내 문구입니다.
    p_name = st.text_input("제품명", placeholder="예: 25SS 옥스포드 셔츠")
    
    # 원가 입력 (빈칸)
    cost = st.number_input("원가 (원)", value=None, step=1000, format="%d", placeholder="원가를 입력하세요")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    # 정가안 입력 (빈칸)
    with col1: p1 = st.number_input("정가안 A", value=None, step=1000, format="%d", placeholder="가격 A")
    with col2: p2 = st.number_input("정가안 B", value=None, step=1000, format="%d", placeholder="가격 B")
    with col3: p3 = st.number_input("정가안 C", value=None, step=1000, format="%d", placeholder="가격 C")

# 계산 로직
def calculate(product_name, cost_price, list_prices):
    discount_steps = [0, 5, 10, 15, 20, 25, 30, 35]
    base_fee = 0.28
    results = []

    for price in list_prices:
        # 입력되지 않은 정가(None)는 건너뜀
        if price is None:
            continue
            
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
                "정가": f"{int(price/1000)}k", 
                "할인": f"{dc_percent}%",
                "수수료": fee_note,
                "판매가": f"{int(sell_price):,}",
                "이익": f"{int(profit):,}",
                "마진": f"{margin_rate:.1f}%",
                "ROI": f"{roi:.0f}%"
            })
    return pd.DataFrame(results)

# 실행 버튼
if st.button("분석 결과 보기 (터치)"):
    # 입력값 검증 (빈칸이 있는지 확인)
    if cost is None:
        st.error("⚠️ 원가를 입력해주세요!")
    elif p1 is None and p2 is None and p3 is None:
        st.error("⚠️ 정가안을 적어도 하나는 입력해주세요!")
    else:
        # 정가 리스트 (입력된 것만 모음)
        valid_prices = [p for p in [p1, p2, p3] if p is not None]
        
        # 제품명 없으면 기본값 설정
        if not p_name: 
            p_name = "제품"
            
        df = calculate(p_name, cost, valid_prices)
        
        st.success(f"✅ [{p_name}] 분석 완료")
        
        # 모바일 보기 좋게 출력
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        st.info("💡 팁: 표의 맨 윗줄(헤더)을 누르면 정렬됩니다.")
