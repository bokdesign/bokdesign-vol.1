import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime
import os

# 1. 아이폰 최적화 설정
st.set_page_config(page_title="복디자인 현장관리", layout="centered")

# 모바일 가독성을 위해 버튼과 입력창 크게 조절
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; }
    input { font-size: 16px !important; }
    textarea { font-size: 16px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 상단 로고 (파일 없을 시 텍스트 표시)
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
else:
    st.subheader("🏗️ 복디자인 통합 관리")

# 임시 데이터 저장소 (세션)
if 'status' not in st.session_state: st.session_state.status = "입력중"
if 'field_data' not in st.session_state: st.session_state.field_data = {}

# 사이드바 권한 설정 (사장님이 직접 체크)
role = st.sidebar.radio("작업 모드 선택", ["👷 직원용 (입력/요청)", "👨‍💼 사장님용 (검토/승인)"])

# --- 1. 직원용: 현장 리포트 작성 ---
if role == "👷 직원용 (입력/요청)":
    st.header("현장 작업 입력")
    
    # 탭으로 구분해서 화면을 깔끔하게
    tab1, tab2 = st.tabs(["💧 누수 탐지", "🛠️ 피해 복구"])
    
    with tab1:
        st.write("### 누수 탐지 결과")
        c1, c2, c3 = st.columns(3)
        p1 = c1.number_input("냉수압", 0.0, 10.0, 5.0, step=0.1)
        p2 = c2.number_input("온수압", 0.0, 10.0, 5.0, step=0.1)
        p3 = c3.number_input("난방압", 0.0, 10.0, 5.0, step=0.1)
        leak_memo = st.text_area("탐지 상세 소견", height=120, placeholder="누수 원인 및 정확한 위치를 적으세요.")

    with tab2:
        st.write("### 피해 복구 내역")
        space = st.selectbox("복구 장소", ["거실/침실", "욕실(물 사용)", "다용도실/베란다"])
        repair_memo = st.text_area("복구 공법 및 자재", height=120, placeholder="작업할 상세 내용을 적으세요.")
        est_price = st.number_input("현장 가견적(원)", min_value=0, step=10000, value=0)

    st.divider()
    if st.button("🚀 사장님 승인 요청 (전송)"):
        if leak_memo and repair_memo:
            st.session_state.field_data = {
                "p1":p1, "p2":p2, "p3":p3, "leak":leak_memo, 
                "space":space, "repair":repair_memo, "price":est_price, 
                "date":datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.status = "승인대기"
            st.balloons()
            st.success("사장님께 전송되었습니다! 모드를 전환하여 승인받으세요.")
        else:
            st.error("모든 칸을 채워주셔야 전송이 가능합니다.")

# --- 2. 사장님용: 관리 및 최종 승인 ---
elif role == "👨‍💼 사장님용 (검토/승인)":
    st.header("현장 리포트 검토")
    
    if st.session_state.status == "승인대기":
        d = st.session_state.field_data
        st.warning(f"📍 {d['space']} 복구 요청 건")
        st.write(f"**탐지 소견:** {d['leak']}")
        st.write(f"**복구 상세:** {d['repair']}")
        st.write(f"**직원 가견적:** {d['price']:,}원")
        
        st.divider()
        final_price = st.number_input("최종 확정 금액 (수정 가능)", value=int(d['price']))
        
        if st.button("✅ 최종 승인 및 PDF 발행"):
            st.session_state.field_data['price'] = final_price
            st.session_state.status = "승인완료"
            st.success("최종 승인되었습니다! 아래에서 PDF를 생성하세요.")
    else:
        st.info("현재 대기 중인 승인 요청이 없습니다.")

# --- 3. 최종 PDF 발행 (승인 완료 시에만 노출) ---
if st.session_state.status == "승인완료":
    st.divider()
    st.header("📄 견적서/계약서 발행")
    customer = st.text_input("고객 성함")
    
    if st.button("📥 PDF 견적서 다운로드"):
        pdf = FPDF()
        pdf.add_page()
        
        # 폰트 설정 (font.ttf 있을 때만 한글)
        if os.path.exists("font.ttf"):
            pdf.add_font('Nanum', '', 'font.ttf', uni=True)
            pdf.set_font('Nanum', '', 14)
        else:
            pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="[BOK DESIGN REPORT]", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Date: {st.session_state.field_data['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Space: {st.session_state.field_data['space']}", ln=True)
        pdf.cell(200, 10, txt=f"Amount: {st.session_state.field_data['price']:,} KRW", ln=True)
        pdf.cell(200, 10, txt=f"Customer: {customer} (Sign)", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=f"Leak Note: {st.session_state.field_data['leak']}")
        pdf.multi_cell(0, 10, txt=f"Repair Detail: {st.session_state.field_data['repair']}")

        # 직인 삽입
        if os.path.exists("sign.png"):
            pdf.image("sign.png", x=160, y=pdf.get_y()-20, w=25)

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="BokDesign_Report.pdf" style="display:block; text-align:center; padding:15px; background-color:#2ECC71; color:white; text-decoration:none; border-radius:10px; font-weight:bold;">📄 PDF 저장하기</a>', unsafe_allow_html=True)

# 초기화 버튼 (당일 작업 종료 시)
if st.sidebar.button("🧹 전체 초기화 (새 현장)"):
    st.session_state.status = "입력중"
    st.session_state.field_data = {}
    st.rerun()
