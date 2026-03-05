import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

st.set_page_config(page_title="복디자인 통합관리", layout="centered")

if 'status' not in st.session_state: st.session_state.status = "작성중"
if 'data' not in st.session_state: st.session_state.data = {}

st.sidebar.title("복디자인 시스템")
role = st.sidebar.radio("접속 권한", ["직원용 (현장)", "사장님용 (관리)"])

if role == "직원용 (현장)":
    st.title("👷 현장 작업 리포트")
    st.subheader("💧 누수 탐지 공정")
    col1, col2, col3 = st.columns(3)
    p1 = col1.number_input("냉수압", 0.0, 10.0, 5.0)
    p2 = col2.number_input("온수압", 0.0, 10.0, 5.0)
    p3 = col3.number_input("난방압", 0.0, 10.0, 5.0)
    leak_memo = st.text_area("탐지 소견", placeholder="누수 원인 상세 기입")
    
    st.divider()
    st.subheader("🛠️ 피해 복구 공정")
    space = st.selectbox("공간 선택", ["거실/침실", "욕실", "베란다"])
    repair_memo = st.text_area("복구 상세", placeholder="공법 및 자재 기입")
    est_price = st.number_input("가견적(원)", min_value=0, step=10000)

    if st.button("🚀 사장님 승인 요청"):
        st.session_state.data = {"p1":p1, "p2":p2, "p3":p3, "leak":leak_memo, "space":space, "repair":repair_memo, "price":est_price, "date":datetime.now().strftime("%Y-%m-%d")}
        st.session_state.status = "승인대기"
        st.warning("전송 완료!")

elif role == "사장님용 (관리)":
    st.title("👨‍💼 현장 최종 컨펌")
    if st.session_state.status == "승인대기":
        d = st.session_state.data
        st.write(f"📍 {d['space']} / 💰 가견적: {d['price']:,}원")
        final_price = st.number_input("최종 금액 확정", value=d['price'])
        if st.button("✅ 최종 승인"):
            st.session_state.data['price'] = final_price
            st.session_state.status = "승인완료"
            st.success("승인됨!")

if st.session_state.status == "승인완료":
    st.divider()
    if st.button("📄 PDF 견적서 생성"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="BOK DESIGN REPORT", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Price: {st.session_state.data['price']:,} KRW", ln=True)
        pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
        b64 = base64.b64encode(pdf_output).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="report.pdf">📥 PDF 다운로드</a>', unsafe_allow_html=True)
