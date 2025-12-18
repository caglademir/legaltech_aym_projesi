import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def yeni_karar_duyurusu(karar_sayisi, site_linki="https://legaltech-aym.streamlit.app"):
    # ... (bağlantı ve abone çekme kısımları aynı)
    
    konu = f"⚖️ Bugün {karar_sayisi} Yeni AYM Kararı Yayımlandı!"
    
    html_icerik = f"""
    <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2 style="color: #1d3557;">⚖️ Resmi Gazete Bildirimi</h2>
            <p>Sayın Meslektaşım,</p>
            <p>Bugün yayımlanan Resmi Gazete'de <strong>{karar_sayisi} yeni Anayasa Mahkemesi kararı</strong> tespit edildi.</p>
            <div style="margin: 20px 0;">
                <a href="{site_linki}" style="background-color: #e63946; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">
                    Analizleri Görüntüle ve PDF Olarak İndir
                </a>
            </div>
            <p style="font-size: 12px; color: #777;">Bu bildirim otomatik takip sisteminiz tarafından gönderilmiştir.</p>
        </body>
    </html>
    """

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gonderen, sifre)
        for abone in aboneler:
            msg = MIMEMultipart()
            msg['From'], msg['To'], msg['Subject'] = gonderen, abone, "Yeni AYM Kararı Analizi"
            msg.attach(MIMEText(html_icerik, 'html'))
            server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Mail Hatası: {e}")
        return False