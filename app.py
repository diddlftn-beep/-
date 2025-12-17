import streamlit as st
import pandas as pd
import io

# ---------------------------------------------------------
# 0. 내 제품 리스트 (여기에 변환된 코드를 붙여넣으세요)
# ---------------------------------------------------------
MY_DATABASE = {
    # 예시 데이터 (지우고 변환된 걸 붙여넣으세요)
    "25SS 옥스포드 셔츠": 18000,
    "25SS 데님 팬츠": 22000,
}

# ---------------------------------------------------------
# 1. 버전 관리
# ---------------------------------------------------------
current_version = "v1.8"
update_history = [
    {"ver": "v1.8", "date": "24.12.17", "desc": "편의기능 추가: 엑셀 데이터를 코드 포맷으로 자동 변환해주는 도구 탑재"},
    {"ver": "v1.7", "date": "24.12.17", "desc": "제품 데이터베이스(DB) 연동: 리스트에서 선택 시 원가 자동입력 기능 추가"},
    {"ver": "v1.6", "date": "24.12.17", "desc": "긴급패치: 제품3 입력칸 먹통 현상 해결 (ID 충돌 수정)"},
    {"ver": "v1.5", "date": "24.12.17", "desc": "설명 텍스트 오류(물결표시) 수정, 버전 히스토리 탭 추가"},
    {"ver": "v1.4", "date": "24.12.17", "desc": "제품명 기준 정렬 시 할인율 오름차순 자동 정렬 적용"},
    {"ver": "v1.3", "date": "24.12.17", "desc": "표 항목 순서 변경 및 가운데 정렬 디자인 적용"},
    {"ver": "v1.2", "date": "24.12.17", "desc": "마진율 구간별 색상 자동 적용 (파랑~빨강)"},
    {"ver": "v1.1", "date": "24.12.17", "desc": "제품 3개 비교 탭 및 할인율 선택 기능 추가"},
]

st.set_page_config(page_title=f"브랜디드 수익성 계산기 {current_version}", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    th { text-align: center !important; }
    td { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 사이드바 (히스토리 + 엑셀 변환기)
# ---------------------------------------------------------
with st.sidebar:
    # --- 엑셀 변환기 (새로 추가된 기능) ---
    with st.expander("🛠️ 엑셀 데이터 변환기 (Click)", expanded=False):
        st.caption("엑셀의 [제품명] [원가] 두 열을 복사해서 아래에 붙여넣으세요.")
        raw_text = st.text_area("엑셀 데이터 붙여넣기", height=150)
        
        if raw_text:
            try:
                # 엑셀 복사 데이터 처리 (탭으로 구분됨)
                converted_lines = []
                lines = raw_text.strip().split('\n')
                for line in lines:
                    parts = line.split('\t') # 엑셀은 보통 탭으로 구분
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        cost = parts[1].strip().replace(',', '') # 콤마 제거
                        converted_lines.append(f'"{name}": {cost},')
                
                result_code = "\n".join(converted_lines)
                st.code(result_code, language='python')
                st.caption("▲ 위 코드를 복사해서 MY_DATABASE 안에 붙여넣으세요.")
            except:
                st.error("형식이 올바르지 않습니다. 엑셀에서 두 열만 드래그해서 복사해주세요.")

    st.markdown("---")
    st.header(f"📜 업데이트 히스토리")
    st.caption(f"Current Version: **{current_version}**")
    for item in update_history:
        st.markdown(f"**[{item['ver']}]** ({item['date']})")
        st.write(f"- {item['desc']}")
        st.markdown("") 

# ---------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 할인율 선택
with st.container():
    st.write("🔻 **보고 싶은 할인율을 선택하세요**")
    selected_rates = st.multiselect(
        "할인율(%)", 
        options=range(0, 95, 5), 
        default=[] 
    )
    st.markdown("---")

# 제품 정보 입력 (탭 구분)
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
products = [] 

# 제품 리스트 옵션 만들기
product_options = ["(직접 입력)"] + list(MY_DATABASE.keys())

# --- 제품 1 ---
with tab1:
    sel1 = st.selectbox("📂 저장된 제품 불러오기", product_options, key="s1")
    if sel1 != "(직접 입력)":
        def_name_1 = sel1; def_cost_1 = MY_DATABASE[sel1]
    else:
        def_name_1 = ""; def_cost_1 = None

    p1_name = st.text_input("제품명 (1)", value=def_name_1, placeholder="직접 입력하세요", key="t1_name")
    p1_cost = st.number_input("원가 (1)", value=def_cost_1, step=1000, format="%d", key="t1_cost")
    
    col1, col2, col3 = st.columns(3)
    with col1: p1_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="t1_p1")
    with col2: p1_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="t1_p2")
    with col3: p1_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="t1_p3")
    
    if p1_cost is not None:
        valid_prices = [p for p in [p1_p1, p1_p2, p1_p3] if p is not None]
        if valid_prices:
            products.append({"name": p1_name if p1_name else "제품1", "cost": p1_cost, "prices": valid_prices})

# --- 제품 2 ---
with tab2:
    sel2 = st.selectbox("📂 저장된 제품 불러오기", product_options, key="s2")
    if sel2 != "(직접 입력)":
        def_name_2 = sel2; def_cost_2 = MY_DATABASE[sel2]
    else:
        def_name_2 = ""; def_cost_2 = None

    p2_name = st.text_input("제품명 (2)", value=def_name_2, placeholder="직접 입력하세요", key="t2_name")
    p2_cost = st.number_input("원가 (2)", value=def_cost_2, step=1000, format="%d", key="t2_cost")
    
    col1, col2, col3 = st.columns(3)
    with col1: p2_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="t2_p1")
    with col2: p2_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="t2_p2")
    with col3: p2_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="t2_p3")

    if p2_cost is not None:
        valid_prices = [p for p in [p2_p1, p2_p2, p2_p3] if p is not None]
        if valid_prices:
            products.append({"name": p2_name if p2_name else "제품2", "cost": p2_cost, "prices": valid_prices})

# --- 제품 3 ---
with tab3:
    sel3 = st.selectbox("📂 저장된 제품 불러오기", product_options, key="s3")
    if sel3 != "(직접 입력)":
        def_name_3 = sel3; def_cost_3 = MY_DATABASE[sel3]
    else:
        def_name_3 = ""; def_cost_3 = None

    p3_name = st.text_input("제품명 (3)", value=def_name_3, placeholder="직접 입력하세요", key="t3_name")
    p3_cost = st.number_input("원가 (3)", value=def_cost_3, step=1000, format="%d", key="t3_cost")
    
    col1, col2, col3 = st.columns(3)
    with col1: p3_p1 = st.number_input("정가 A", value=None, step=1000, format="%d", key="t3_p1")
    with col2: p3_p2 = st.number_input("정가 B", value=None, step=1000, format="%d", key="t3_p2")
    with col3: p3_p3 = st.number_input("정가 C", value=None, step=1000, format="%d", key="t3_p3")

    if p3_cost is not None:
        valid_prices = [p for p in [p3_p1, p3_p2, p3_p3] if p is not None]
        if valid_prices:
            products.append({"name": p3_name if p3_name else "제품3", "cost": p3_cost, "prices": valid_prices})


# ---------------------------------------------------------
# 계산 및 출력
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
                    "수수료": fee_note,
                    "할인": dc_percent,     
                    "정가": int(price),
                    "판매가": int(sell_price),
                    "원가": cost_price,
                    "이익": int(profit),
                    "ROI": roi,
                    "마진": margin_rate
                })
    
    df = pd.DataFrame(results)
    
    if not df.empty:
        df = df.sort_values(by=['제품명', '할인'], ascending=[True, True])
        cols = ["제품명", "수수료", "할인", "정가", "판매가", "원가", "이익", "ROI", "마진"]
        df = df[cols]
        
    return df

def color_margin_rows(val):
    color = ''
    weight = 'bold'
    if val > 35: color = '#1E90FF' 
    elif 31 <= val <= 35: color = '#228B22' 
    elif 25 <= val < 31: color = '#808080' 
    elif 20 <= val < 25: color = '#FF8C00' 
    else: color = '#FF4500' 
    return f'color: {color}; font-weight: {weight}'

if st.button("분석 결과 보기 (터치)"):
    if not products:
        st.error("⚠️ 최소한 하나의 제품 정보(원가, 정가)를 입력해주세요!")
    elif not selected_rates:
        st.info("👈 **상단에서 '할인율'을 먼저 선택해주세요!**")
    else:
        df = calculate_all(products, selected_rates)
        st.success(f"✅ 총 {len(products)}개 제품 분석 완료")
        
        styled_df = df.style.map(color_margin_rows, subset=['마진'])\
            .format({
                '원가': '{:,}',
                '정가': '{:,}',
                '할인': '{}%', 
                '판매가': '{:,}',
                '이익': '{:,}',
                '마진': '{:.1f}%',
                'ROI': '{:.0f}%'
            })\
            .set_properties(**{'text-align': 'center'}) \
            .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
            
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
