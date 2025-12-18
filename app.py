import streamlit as st
import os
from main_engine import start_process, download_and_summarize
from database import ozetlerde_ara, abone_ekle  # database.py'ye eklediğimiz fonksiyon
from datetime import datetime
from fpdf import FPDF

# --- SİSTEM BAŞLATMA VE PLAYWRIGHT KURULUMU ---
try:
    import playwright
except ImportError:
    os.system("pip install playwright")
    os.system("playwright install chromium")

if "playwright_installed" not in st.session_state:
    os.system("playwright install chromium")
    st.session_state["playwright_installed"] = True

st.set_page_config(page_title="LegalTech AYM", layout="wide", page_icon="⚖️")

# --- ABONELİK POP-UP FONKSİYONU ---
@st.dialog("⚖️ Hukuki Bültene Abone Ol")
def abone_ol_popup():
    st.write("Her sabah yeni AYM kararlarından haberdar olmak için e-posta adresinizi bırakın. Analizler otomatik olarak e-postanıza gelsin.")
    yeni_email = st.text_input("E-posta Adresiniz", placeholder="ornek@mail.com")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Kaydı Tamamla", type="primary"):
            if "@" in yeni_email and "." in yeni_email:
                if abone_ekle(yeni_email):
                    st.success("Tebrikler! Aboneliğiniz başarıyla oluşturuldu.")
                    st.balloons()
                else:
                    st.warning("Bu e-posta zaten kayıtlı.")
            else:
                st.error("Lütfen geçerli bir e-posta adresi girin.")
    with col2:
        if st.button("Kapat"):
            st.rerun()

# --- CSS GÜNCELLEMELERİ ---
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #e63946 !important;
        color: white !important;
        font-weight: bold;
    }
    /* Sidebar Abone Ol Butonu Stil */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: #1d3557 !important;
        color: white !important;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: OTOMASYON BİLGİSİ VE ABONE OL ---
with st.sidebar:
    st.title("⚙️ Ayarlar & Takip")
    st.info("🕒 Otomasyon: Her sabah 08:00'de Resmi Gazete taranır ve yeni karar varsa abonelere bildirilir.")
    
    if st.button("🔔 BÜLTENE ABONE OL"):
        abone_ol_popup()
    
    st.markdown("---")
    st.caption("LegalTech AYM v1.0")

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    safe_title = title.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(200, 10, txt="AYM KARAR ANALIZ RAPORU", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=safe_content)
    pdf_output = pdf.output(dest='S')
    return bytes(pdf_output) if not isinstance(pdf_output, str) else pdf_output.encode('latin-1')

# --- ANA SAYFA ---
st.title("⚖️ AYM Karar Analiz Platformu")
tab1, tab2 = st.tabs(["🔍 Günlük Tarama", "📚 Arşivde Arama"])

# --- TAB 1: GÜNLÜK TARAMA ---
with tab1:
    col_list, col_summary = st.columns([2, 3])
    
    with col_list:
        st.subheader("📂 Gazete Akışı")
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            tarih_secimi = st.date_input("Karar Tarihi", value=datetime.now())
            tarih_str = tarih_secimi.strftime("%Y%m%d")
        with t_col2:
            st.write("") # Boşluk için
            ara_butonu = st.button("GAZETEYİ TARA", type="primary")

        if ara_butonu:
            if 'current_summary' in st.session_state: del st.session_state['current_summary']
            if 'secilen_karar' in st.session_state: del st.session_state['secilen_karar']
            
            with st.spinner("Resmi Gazete taranıyor..."):
                sonuclar = start_process(tarih_str)
                if not sonuclar:
                    st.warning(f"⚠️ {tarih_secimi.strftime('%d.%m.%Y')} tarihinde bir AYM kararı bulunamadı.")
                    st.session_state['kararlar'] = []
                else:
                    st.session_state['kararlar'] = sonuclar

        if 'kararlar' in st.session_state and st.session_state['kararlar']:
            for idx, karar in enumerate(st.session_state['kararlar']):
                with st.container(border=True):
                    st.write(f"**{karar['title']}**")
                    if st.button("🔍 İncele ve Analiz Et", key=f"daily_{idx}"):
                        with st.status("Analiz ediliyor...", expanded=True) as status:
                            st.session_state['current_summary'] = download_and_summarize(karar, tarih_str)
                            st.session_state['secilen_karar'] = karar
                            status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)

    with col_summary:
        st.subheader("📄 Hukuki Analiz Paneli")
        if 'current_summary' in st.session_state:
            secilen = st.session_state['secilen_karar']
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                st.link_button("📄 Orijinal PDF'i Aç", secilen['url'])
            with b_col2:
                pdf_data = create_pdf(secilen['title'], st.session_state['current_summary'])
                st.download_button("📥 Analiz Raporunu İndir", data=pdf_data, file_name=f"AYM_Analiz_{tarih_str}.pdf")
            st.markdown("---")
            st.markdown(st.session_state['current_summary'])
        else:
            st.info("Sol taraftan bir tarih seçip tarama yapın, ardından kararlardan birini seçin.")

# --- TAB 2: ARŞİVDE ARAMA ---
with tab2:
    st.subheader("🔎 Arşivlenmiş Analizler")
    arama_col1, arama_col2 = st.columns([4, 1])
    with arama_col1:
        arama_sorgusu = st.text_input("Anahtar kelime...", placeholder="Aramak istediğiniz terimi yazın", label_visibility="collapsed")
    with arama_col2:
        arama_butonu_arsiv = st.button("ARA", use_container_width=True)
    
    if arama_butonu_arsiv and arama_sorgusu:
        with st.spinner(f"'{arama_sorgusu}' terimi arşivde taranıyor..."):
            sonuclar = ozetlerde_ara(arama_sorgusu)
            if sonuclar:
                st.success(f"Bulunan Kayıt Sayısı: {len(sonuclar)}")
                for tarih, baslik, ozet, url in sonuclar:
                    with st.expander(f"📅 {tarih} - {baslik}"):
                        st.markdown(ozet)
                        st.link_button("Karar Metnine Git", url)
            else:
                st.error(f"❌ Arşivde '{arama_sorgusu}' terimine dair bir analiz bulunamadı.")