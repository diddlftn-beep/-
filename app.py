import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 0. 비밀번호 보안 설정 (가장 위에 넣으세요)
# ---------------------------------------------------------
def check_password():
    """Returns `True` if the user had the correct password."""

    # 비밀번호가 맞았는지 확인하는 함수
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 보안을 위해 입력값 삭제
        else:
            st.session_state["password_correct"] = False

    # 이미 인증된 상태라면 True 반환
    if st.session_state.get("password_correct", False):
        return True

    # 비밀번호 입력창 띄우기
    st.set_page_config(page_title="🔒 로그인 필요", layout="centered")
    st.markdown("## 🔒 접근 제한 구역")
    st.text_input(
        "비밀번호를 입력하세요", type="password", on_change=password_entered, key="password"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ 비밀번호가 틀렸습니다.")
        
    return False

# 비밀번호가 틀리면 여기서 프로그램 실행 중단 (아래 코드는 실행 안 됨)
if not check_password():
    st.stop()
    
# ---------------------------------------------------------
# 1. 기본 설정 & 스타일
# ---------------------------------------------------------
current_version = "v4.0 (Final Complete)"
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
# 2. 데이터 불러오기 (오류 방지 로직 포함)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "products.csv"
    
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        df = pd.read_csv(file_path)
        
        # [중요] 컬럼명 공백 제거 및 소문자 변환 (오류 방지)
        df.columns = df.columns.str.strip().str.lower()
        
        # 필수 컬럼 확인 및 매핑 (한글/영어 혼용 대비)
        # 만약 CSV 헤더가 한글이어도 영어로 매핑해줌
        rename_map = {
            '상품명': 'name', '원가': 'cost', '판매가': 'price', '정가': 'price', '할인율': 'discount'
        }
        df = df.rename(columns=rename_map)
        
        # 필수 컬럼이 있는지 체크
        required_cols = ['name', 'cost', 'price', 'discount']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"❌ CSV 파일에 '{col}' 컬럼이 없습니다. (현재 컬럼: {list(df.columns)})")
                return pd.DataFrame()

        # 숫자 데이터 변환 (쉼표 제거 후 숫자로)
        for col in ['cost', 'price', 'discount']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
            
        return df
        
    except Exception as e:
        st.error(f"❌ 데이터 로딩 중 오류 발생: {e}")
        return pd.DataFrame()

df_products = load_data()

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title(f"📊 멀티 수익성 분석기 ({current_version})")
st.caption("마진율 색상: 🔵35%초과 🟢31-35% ⚪25-31% 🟠20-25% 🔴20%미만")

# 공통 할인율 선택 영역
with st.container():
    st.write("🔻 **추가로 비교할 할인율을 선택하세요** (기본 DB 할인율 외에 시뮬레이션용)")
    selected_rates = st.multiselect("할인율(%)", options=range(0, 95, 5), default=[])
    st.markdown("---")

# ---------------------------------------------------------
# 4. 입력 탭 (함수화)
# ---------------------------------------------------------
def render_input_tab(tab_idx):
    mode = st.radio(
        f"입력 방식 ({tab_idx})", 
        ["📝 직접 입력", "📂 DB 불러오기"], 
        key=f"mode_{tab_idx}",
        label_visibility="collapsed"
    )

    if mode == "📂 DB 불러오기":
        if df_products.empty:
            st.warning("데이터 파일(products.csv)을 읽을 수 없습니다.")
            return None
            
        # [핵심 변경] Multiselect를 사용하여 '지우기' 편하게 만듦
        # max_selections=1 로 설정하여 1개만 선택되지만 UI는 태그 형태
        product_selection = st.multiselect(
            "제품 검색 (X 눌러서 삭제 가능)",
            options=df_products['name'].tolist(),
            max_selections=1,
            placeholder="제품명을 입력하거나 선택하세요",
            key=f"search_{tab_idx}"
        )
        
        if product_selection:
            name = product_selection[0] # 리스트에서 첫 번째 값 추출
            row = df_products[df_products['name'] == name].iloc[0]
            
            # 정보 표시
            c1, c2, c3 = st.columns(3)
            c1.metric("원가", f"{row['cost']:,}원")
            c2.metric("정가", f"{row['price']:,}원")
            c3.metric("DB 할인율", f"{row['discount']}%")
            
            return {
                "type": "db",
                "name": name,
                "cost": row['cost'],
                "prices": [row['price']],
                "fixed_discount": row['discount']
            }
        else:
            st.info("👆 위에서 제품을 선택해주세요.")
            return None

    else: # 직접 입력 모드
        p_name = st.text_input(f"제품명", placeholder="예: 신상품 A", key=f"name_{tab_idx}")
        p_cost = st.number_input(f"원가", value=None, step=1000, key=f"cost_{tab_idx}")
        
        c1, c2, c3 = st.columns(3)
        with c1: p1 = st.number_input("정가 A", value=None, step=1000, key=f"p1_{tab_idx}")
        with c2: p2 = st.number_input("정가 B (옵션)", value=None, step=1000, key=f"p2_{tab_idx}")
        with c3: p3 = st.number_input("정가 C (옵션)", value=None, step=1000, key=f"p3_{tab_idx}")
        
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

# 탭 생성 및 입력 받기
tab1, tab2, tab3 = st.tabs(["🛍️ 제품 1", "🛍️ 제품 2", "🛍️ 제품 3"])
products_to_calc = []

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
# 5. 계산 로직 및 결과 출력
# ---------------------------------------------------------
def calculate_results(product_list, compare_rates):
    base_fee = 0.28
    results = []
    
    compare_rates.sort()

    for item in product_list:
        # 할인율 리스트 결정
        if item['type'] == 'db':
            # DB에 있는 고정 할인율 + 사용자가 선택한 비교 할인율
            # set으로 중복 제거 후 정렬
            rates_set = {item['fixed_discount']}
            if compare_rates:
                rates_set.update(compare_rates)
            target_rates = sorted(list(rates_set))
        else:
            # 직접 입력일 경우 선택한 할인율만 (없으면 0%)
            target_rates = compare_rates if compare_rates else [0]

        for price in item['prices']:
            if price == 0: continue
            
            for dc_percent in target_rates:
                discount_rate = dc_percent / 100.0
                
                # 수수료 구간 적용
                if discount_rate <= 0.09: applied_fee_rate = base_fee; fee_note = "28%"
                elif discount_rate <= 0.19: applied_fee_rate = base_fee - 0.01; fee_note = "27%"
                elif discount_rate <= 0.29: applied_fee_rate = base_fee - 0.02; fee_note = "26%"
                else: applied_fee_rate = base_fee - 0.03; fee_note = "25%"

                sell_price = price * (1 - discount_rate)
                fee = sell_price * applied_fee_rate
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
    
    if not results:
        return pd.DataFrame()
        
    df = pd.DataFrame(results)
    # 정렬: 제품명 -> 할인율 순
    df = df.sort_values(by=['제품명', '할인'])
    return df[ ["제품명", "수수료", "할인", "정가", "판매가", "원가", "이익", "ROI", "마진"] ]

# 색상 스타일링 함수
def style_dataframe(val):
    color = '#FF4500' # 빨강 (20% 미만)
    if val > 35: color = '#1E90FF' # 파랑
    elif 31 <= val <= 35: color = '#228B22' # 초록
    elif 25 <= val < 31: color = '#808080' # 회색
    elif 20 <= val < 25: color = '#FF8C00' # 주황
    return f'color: {color}; font-weight: bold'

# 실행 버튼
if st.button("🚀 수익성 분석 실행"):
    if not products_to_calc:
        st.warning("⚠️ 분석할 제품을 선택하거나 입력해주세요.")
    else:
        df_res = calculate_results(products_to_calc, selected_rates)
        
        if not df_res.empty:
            st.success("분석 완료!")
            st.dataframe(
                df_res.style.map(style_dataframe, subset=['마진']).format({
                    '원가': '{:,}', '정가': '{:,}', '할인': '{}%', 
                    '판매가': '{:,}', '이익': '{:,}', 
                    '마진': '{:.1f}%', 'ROI': '{:.0f}%'
                }),
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.error("계산된 결과가 없습니다. 입력 값을 확인해주세요.")
