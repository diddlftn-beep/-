import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
current_version = "v9.0 (Bulk Analysis)"
st.set_page_config(
    page_title=f"수익성 분석기 {current_version}", 
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

    st.markdown("## 🔒 관계자 외 접근 금지")
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
# 🔓 메인 프로그램
# =========================================================

def logout():
    st.session_state.password_correct = False
    st.rerun()

# 상단 UI
col_t, col_l = st.columns([8,2])
with col_t:
    st.title("📊 멀티 수익성 분석기")
with col_l:
    st.write("")
    if st.button("🔒 로그아웃"): logout()

st.divider()

# ---------------------------------------------------------
# 3. 데이터 로딩
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "products.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["name", "cost", "price", "discount"])
    
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp949')
        
        df.columns = df.columns.str.strip().str.replace(" ", "").str.lower()
        rename_map = {'상품명': 'name', '원가': 'cost', '판매가': 'price', '정가': 'price', '할인율': 'discount'}
        df.rename(columns=rename_map, inplace=True)

        if 'name' not in df.columns:
            if len(df.columns) >= 4:
                df.columns.values[0] = 'name'
                df.columns.values[1] = 'cost'
                df.columns.values[2] = 'price'
                df.columns.values[3] = 'discount'
            else:
                return pd.DataFrame()

        for col in ['cost', 'price', 'discount']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
            
        return df
    except:
        return pd.DataFrame()

df_products = load_data()

# ---------------------------------------------------------
# 4. 분석 모드 선택 및 입력
# ---------------------------------------------------------
st.markdown("""<style>.stButton>button { border-radius: 8px; font-weight: bold; }</style>""", unsafe_allow_html=True)

# 공통 옵션
selected_rates = st.multiselect("추가 비교 할인율(%)", options=range(0, 95, 5))
st.write("")

# 모드 선택 라디오 버튼
analysis_mode = st.radio(
    "분석 모드를 선택하세요", 
    ["📑 탭 모드 (소량/수동 입력)", "📚 대량/전체 분석 (DB 전용)"], 
    horizontal=True
)

st.markdown("---")

items_to_process = []

# [모드 1] 기존 탭 방식
if analysis_mode == "📑 탭 모드 (소량/수동 입력)":
    t1, t2, t3 = st.tabs(["제품 1", "제품 2", "제품 3"])
    
    def render_tab(idx):
        mode = st.radio(f"입력 방식 {idx}", ["직접 입력", "DB 불러오기"], key=f"m{idx}", label_visibility="collapsed")
        
        if mode == "DB 불러오기":
            if df_products.empty:
                st.warning("데이터 없음")
                return None
            sel = st.multiselect("제품 검색", df_products['name'].tolist(), max_selections=1, key=f"s{idx}", placeholder="제품명 검색")
            if sel:
                row = df_products[df_products['name'] == sel[0]].iloc[0]
                c1, c2, c3 = st.columns(3)
                c1.metric("원가", f"{row['cost']:,}")
                c2.metric("정가", f"{row['price']:,}")
                c3.metric("할인", f"{row['discount']}%")
                return [{"name": sel[0], "cost": row['cost'], "price": row['price'], "disc": row['discount']}]
        else:
            nm = st.text_input("이름", key=f"nm{idx}")
            ct = st.number_input("원가", step=1000, key=f"ct{idx}")
            pr = st.number_input("정가", step=1000, key=f"pr{idx}")
            if ct and pr:
                return [{"name": nm or f"제품{idx}", "cost": ct, "price": pr, "disc": 0}]
        return []

    with t1: items_to_process.extend(render_tab(1) or [])
    with t2: items_to_process.extend(render_tab(2) or [])
    with t3: items_to_process.extend(render_tab(3) or [])

# [모드 2] 대량/전체 분석 방식
else:
    st.info("💡 DB에 있는 제품을 여러 개 선택하거나, 전체를 한 번에 분석합니다.")
    
    col_all, col_sel = st.columns([2, 8])
    
    # 전체 선택 체크박스
    use_all = col_all.checkbox("📦 전체 제품 불러오기", value=False)
    
    target_products = []
    
    if use_all:
        if df_products.empty:
            st.error("데이터 파일이 비어있습니다.")
        else:
            st.success(f"총 {len(df_products)}개의 제품이 선택되었습니다.")
            # 전체 데이터를 리스트로 변환
            for index, row in df_products.iterrows():
                items_to_process.append({
                    "name": row['name'], 
                    "cost": row['cost'], 
                    "price": row['price'], 
                    "disc": row['discount']
                })
    else:
        # 멀티 선택창 (max_selections 제한 없음)
        selected_names = col_sel.multiselect(
            "제품 검색 및 다중 선택", 
            options=df_products['name'].tolist() if not df_products.empty else [],
            placeholder="제품을 선택하세요 (여러 개 가능)"
        )
        
        if selected_names:
            for name in selected_names:
                row = df_products[df_products['name'] == name].iloc[0]
                items_to_process.append({
                    "name": row['name'], 
                    "cost": row['cost'], 
                    "price": row['price'], 
                    "disc": row['discount']
                })

# ---------------------------------------------------------
# 5. 계산 실행 및 출력
# ---------------------------------------------------------
if st.button("🚀 분석 실행", type="primary", use_container_width=True):
    if not items_to_process:
        st.warning("분석할 제품이 선택되지 않았습니다.")
    else:
        rows = []
        base_fee = 0.28
        
        # 진행률 표시 (데이터가 많을 경우를 대비)
        progress_bar = st.progress(0)
        total_items = len(items_to_process)
        
        for i, it in enumerate(items_to_process):
            # DB 모드면 DB할인율 + 선택할인율, 수동이면 선택할인율만
            # (대량 모드는 무조건 DB 베이스이므로 DB할인율 포함)
            current_disc = it['disc'] if 'disc' in it else 0
            
            # 할인율 리스트 합치기 (중복 제거 및 정렬)
            all_rates = sorted(list(set([current_disc] + selected_rates)))
            
            for r in all_rates:
                dr = r / 100
                # 수수료 구간
                fee_rate = 0.28 if dr <= 0.09 else (0.27 if dr <= 0.19 else (0.26 if dr <= 0.29 else 0.25))
                
                sell = it['price'] * (1 - dr)
                fee = sell * fee_rate
                profit = sell - it['cost'] - fee
                margin = (profit / sell * 100) if sell else 0
                roi = (profit / it['cost'] * 100) if it['cost'] else 0
                
                rows.append({
                    "제품명": it['name'], 
                    "수수료": f"{int(fee_rate*100)}%", 
                    "할인": f"{r}%",
                    "정가": int(it['price']), 
                    "판매가": int(sell), 
                    "원가": int(it['cost']),
                    "이익": int(profit), 
                    "ROI": roi,
                    "마진": margin
                })
            
            # 진행률 업데이트
            if total_items > 1:
                progress_bar.progress((i + 1) / total_items)
        
        if total_items > 1:
            progress_bar.empty()

        # 결과 데이터프레임
        dres = pd.DataFrame(rows).sort_values(['제품명', '할인'])
        
        # 색상 함수
        def color_map(val):
            if val > 35: return 'color: #1E90FF; font-weight: bold'
            elif 31 <= val <= 35: return 'color: #228B22; font-weight: bold'
            elif 25 <= val < 31: return 'color: #808080; font-weight: bold'
            elif 20 <= val < 25: return 'color: #FF8C00; font-weight: bold'
            return 'color: #FF4500; font-weight: bold'

        st.success(f"✅ 총 {len(rows)}개의 시나리오 분석 완료")
        
        # 데이터프레임 표시 (전체 너비, 인덱스 숨김)
        st.dataframe(
            dres.style.map(color_map, subset=['마진']).format({
                '원가':'{:,}', '정가':'{:,}', '판매가':'{:,}', '이익':'{:,}', 
                '마진':'{:.1f}%', 'ROI':'{:.0f}%'
            }), 
            use_container_width=True, 
            hide_index=True,
            height=600 # 목록이 길어질 수 있으므로 높이 확보
        )
