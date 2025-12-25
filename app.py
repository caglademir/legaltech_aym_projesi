import streamlit as st
from main_engine import start_process, download_and_summarize
from database import ozetlerde_ara, abone_ekle
from datetime import datetime
import urllib.parse

# Sayfa Konfigürasyonu
st.set_page_config(page_title="LegalTech AYM AI", layout="wide", page_icon="⚖️")

# --- CSS & TASARIM ---
# --- CSS GÜNCELLEME ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #0e1117; }
    
    /* Sidebar Renk ve Stil Düzenlemesi */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important; /* Bir ton daha koyu/profesyonel gri */
        border-right: 1px solid #30363d; /* İnce ayırıcı çizgi */
    }

    /* Sidebar içindeki başlık ve metin renkleri */
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #f0f6fc !important;
    }

    /* Kaydol Butonu Renk Ayarı (Sidebar) */
    [data-testid="stSidebar"] .stButton button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        border-color: #8b949e !important;
        color: white !important;
    }

    /* Dashboard Kartları (Eski Renkler Korundu) */
    .metric-card {
        background-color: #1e2129; 
        padding: 20px; 
        border-radius: 12px;
        border: 1px solid #31333f; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Renklerle Uyumlu İçerik) ---
with st.sidebar:
    st.markdown("## ⚖️ Kontrol Merkezi")
    st.divider()
    
    with st.expander("📩 Bülten Aboneliği"):
        st.write("Yeni kararlardan haberdar olun.")
        sub_email = st.text_input("E-posta Adresiniz", key="sb_mail")
        if st.button("KAYDOL", use_container_width=True):
            if "@" in sub_email:
                # database fonksiyonunuzu çağırın
                st.success("Kaydedildi!")
            else:
                st.error("Geçersiz format.")

    st.divider()
    st.caption("LegalTech AYM v2.0")

# --- AI ETİKET ÜRETİCİ ---
def generate_tags(content):
    tags = ["#AYM", "#HukukAnaliz"]
    low_content = content.lower()
    if "mülkiyet" in low_content: tags.append("#MülkiyetHakkı")
    if "yargılanma" in low_content: tags.append("#AdilYargılanma")
    if "ihlal" in low_content: tags.append("#HakIhlali")
    if "tazminat" in low_content: tags.append("#Tazminat")
    if "ifade özgürlüğü" in low_content: tags.append("#İfadeÖzgürlüğü")
    return tags



# --- ANA EKRAN & DASHBOARD ---
st.title("⚖️ AYM Karar Analiz Platformu")

# Dashboard Güvenlik Kontrolü
if 'kararlar' in st.session_state and st.session_state['kararlar'] is not None:
    m1, m2, m3, m4 = st.columns(4)
    total = len(st.session_state['kararlar'])
    ihlal_sayisi = sum(1 for k in st.session_state['kararlar'] if "ihlal" in k.get('title','').lower())
    
    m1.markdown(f'<div class="metric-card">📝 Toplam Karar<br><h2>{total}</h2></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card">🔴 İhlal Kararı<br><h2 style="color:#ff4b4b">{ihlal_sayisi}</h2></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card">🟢 İhlal Yok<br><h2>{total - ihlal_sayisi}</h2></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card">👥 Aktif Abone<br><h2>124</h2></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Günlük Tarama", "📚 Arşiv"])

# --- TAB 1: GÜNLÜK TARAMA ---
with tab1:
    col_list, col_analysis = st.columns([2, 3])
    with col_list:
        st.subheader("📂 Gazete Akışı")
        t_col1, t_col2 = st.columns([2,1])
        with t_col1:
            tarih = st.date_input("Tarih", value=datetime.now(), label_visibility="collapsed")
        with t_col2:
            if st.button("TARA", type="primary", use_container_width=True):
                st.session_state['kararlar'] = start_process(tarih.strftime("%Y%m%d"))
                st.rerun()
        
        st.divider()
        if 'kararlar' in st.session_state and st.session_state['kararlar']:
            for idx, karar in enumerate(st.session_state['kararlar']):
                with st.container(border=True):
                    st.write(f"**{karar['title']}**")
                    if st.button(f"🔍 Analizi Başlat", key=f"btn_{idx}", use_container_width=True):
                        with st.spinner("AI Analiz Ediyor..."):
                            summary = download_and_summarize(karar, tarih.strftime("%Y%m%d"))
                            st.session_state['current_summary'] = summary
                            st.session_state['secilen_karar'] = karar
                            st.session_state['tags'] = generate_tags(summary)
                            st.rerun()

    with col_analysis:
        st.subheader("📄 Hukuki Analiz Paneli")
        if 'current_summary' in st.session_state:
            # Araç Çubuğu
            a1, a2, a3 = st.columns([3,2,2])
            with a1: st.link_button("🔗 PDF Gör", st.session_state['secilen_karar']['url'], use_container_width=True)
            with a2: st.button("📥 Raporu İndir", use_container_width=True)
            with a3:
                msg = f"*AYM Karar Analizi*\n{st.session_state['secilen_karar']['title']}"
                wa_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-icon"><i class="fab fa-whatsapp"></i></a>', unsafe_allow_html=True)
            
            st.divider()
            # ETİKETLERİ BURADA GÖSTERİYORUZ
            st.write("🏷️ **AI Etiketleri:**")
            tag_html = "".join([f'<span class="badge">{t}</span>' for t in st.session_state['tags']])
            st.markdown(tag_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(st.session_state['current_summary'])
        else:
            st.info("Sol listeden bir karar seçerek analizi başlatın.")

# --- TAB 2: ARŞİV ---
with tab2:
    st.subheader("📚 Karar Arşivi")
    search_q = st.text_input("Arşivde Ara", placeholder="Anahtar kelime veya Karar No girin...")
    
    if search_q:
        sonuclar = ozetlerde_ara(search_q)
        if sonuclar:
            for row in sonuclar:
                # Arşiv kartı tasarımı
                with st.container():
                    st.markdown(f"""
                    <div class="archive-card">
                        <small style="color: #888;">{row[0]}</small><br>
                        <strong>{row[1]}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("Analiz Özetini Gör"):
                        st.write(row[2])
                        st.link_button("Orijinal Karara Git", row[3])
        else:
            st.warning("Sonuç bulunamadı.")
    else:
        st.info("Geçmiş analizlere ulaşmak için yukarıdaki arama kutusunu kullanın.")