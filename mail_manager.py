import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def yeni_karar_duyurusu(karar_sayisi):
    gonderen = os.getenv("EMAIL_ADRESI")
    sifre = os.getenv("EMAIL_SIFRESI")
    site_linki = "https://legaltech-aym.streamlit.app" # Canlı site linkin
    
    # Veritabanından aboneleri çek
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    cursor.execute("SELECT eposta FROM aboneler WHERE aktif_mi = 1")
    aboneler = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not aboneler: return False

    # İstediğin "Yönlendirme" odaklı tasarım
    html_icerik = f"""
    <html>
        <body style="font-family: sans-serif; border-top: 4px solid #1d3557; padding: 20px;">
            <h2 style="color: #1d3557;">⚖️ Güncel AYM Karar Bildirimi</h2>
            <p>Sayın Meslektaşım,</p>
            <p>Bugün yayımlanan Resmi Gazete'de <strong>{karar_sayisi} yeni Anayasa Mahkemesi kararı</strong> tespit edildi.</p>
            <p>Yapay zeka tarafından hazırlanan detaylı analiz raporlarını ve mali denetim sonuçlarını incelemek için aşağıdaki butonu kullanabilirsiniz:</p>
            <div style="margin: 30px 0; text-align: center;">
                <a href="{site_linki}" style="background-color: #e63946; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Analizleri Görüntüle
                </a>
            </div>
            <p style="font-size: 11px; color: #777;">LegalTech AYM Otomasyon Sistemi - Otomatik Bilgilendirme</p>
        </body>
    </html>
    """

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gonderen, sifre)
        for abone in aboneler:
            msg = MIMEMultipart()
            msg['From'], msg['To'], msg['Subject'] = gonderen, abone, "📢 Yeni AYM Kararları Yayımlandı!"
            msg.attach(MIMEText(html_icerik, 'html'))
            server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Mail Hatası: {e}")
        return False