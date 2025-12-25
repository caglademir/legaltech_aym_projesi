import streamlit as st
from main_engine import start_process, download_and_summarize
from database import ozetlerde_ara, abone_ekle
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="LegalTech AYM", layout="wide", page_icon="⚖️")

# --- YENİLENMİŞ RENK PALETİ CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }

    /* SIDEBAR - Arka plandan daha açık */
    [data-testid="stSidebar"] {
        background-color: #1e2129 !important;
        border-right: 1px solid #31333f;
    }
    
    /* 1. GAZETEYİ TARA - Klasik Bordo */
    button[kind="primary"] {
        background-color: #800000 !important;
        color: white !important;
        border: 1px solid #600000 !important;
    }
    
    /* 2. ANALİZİ BAŞLAT - YENİ RENK: GÜVEN VEREN YEŞİL (#2E7D32) */
    div.stButton > button:not([kind="primary"]) {
        background-color: #2E7D32 !important; 
        color: #ffffff !important; 
        border: 1px solid #1B5E20 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 3. ORİJİNAL PDF'İ AÇ - Kurumsal Mavi */
    .stLinkButton > a {
        background-color: #24527a !important; 
        color: white !important;
    }

    /* 4. ANALİZ RAPORUNU İNDİR - Koyu Lacivert */
    .stDownloadButton > button {
        background-color: #1a3c5a !important; 
        color: white !important;
        width: 100% !important;
    }

    /* Hover Efektleri */
    button:hover {
        filter: brightness(115%) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text):
        if not text: return ""
        text = text.replace("**", "").replace("###", "")
        rep = {"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c", "–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "•": "*"}
        for s, r in rep.items(): text = text.replace(s, r)
        return text.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Helvetica", 'B', size=14)
    pdf.cell(200, 10, txt="AYM KARAR ANALIZ RAPORU", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=f"BASLIK: {clean_text(title)}\n\n{clean_text(content)}")
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏛️ LegalTech Menü")
    st.markdown("---")
    st.subheader("📧 Bülten Aboneliği")
    sub_email = st.text_input("E-posta", key="side_sub", placeholder="avukat@hukuk.com")
    if st.button("ABONE OL", use_container_width=True):
        if "@" in sub_email and "." in sub_email:
            abone_ekle(sub_email)
            st.success("Kaydedildi!")
        else: st.error("Geçersiz e-posta.")

# --- ANA EKRAN ---
st.title("⚖️ AYM Karar Analiz Platformu")
tab1, tab2 = st.tabs(["🔍 Günlük Tarama", "📚 Arşiv"])

with tab1:
    col_left, col_right = st.columns([2, 3])
    with col_left:
        st.subheader("📂 Gazete Akışı")
        c1, c2 = st.columns([2, 1])
        with c1:
            tarih_secimi = st.date_input("Karar Tarihi", value=datetime.now(), label_visibility="collapsed")
        with c2:
            if st.button("TARA", type="primary", use_container_width=True):
                st.session_state['kararlar'] = start_process(tarih_secimi.strftime("%Y%m%d"))
        
        st.markdown("---")
        if 'kararlar' in st.session_state:
            for idx, karar in enumerate(st.session_state['kararlar']):
                with st.container(border=True):
                    st.write(f"**{karar['title']}**")
                    # YENİ YEŞİL BUTON
                    if st.button(f"🔍 Analizi Başlat", key=f"btn_{idx}", use_container_width=True):
                        with st.spinner("İnceleniyor..."):
                            st.session_state['current_summary'] = download_and_summarize(karar, tarih_secimi.strftime("%Y%m%d"))
                            st.session_state['secilen_karar'] = karar
                            st.rerun()

    with col_right:
        st.subheader("📄 Hukuki Analiz Paneli")
        if 'current_summary' in st.session_state:
            b1, b2 = st.columns(2)
            with b1: st.link_button("🔗 PDF'i Aç", st.session_state['secilen_karar']['url'], use_container_width=True)
            with b2:
                try:
                    pdf_bytes = create_pdf(st.session_state['secilen_karar']['title'], st.session_state['current_summary'])
                    st.download_button("📥 Raporu İndir", data=pdf_bytes, file_name="aym_analiz.pdf")
                except: st.error("PDF Hatası")
            st.markdown("---")
            st.info(f"**Karar:** {st.session_state['secilen_karar']['title']}")
            st.markdown(st.session_state['current_summary'])