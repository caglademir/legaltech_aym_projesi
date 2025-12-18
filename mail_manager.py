import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def bulten_gonder(karar_basligi, analiz_ozeti):
    # Değişkenleri Çevresel Değişkenlerden Alıyoruz
    gonderen = os.getenv("EMAIL_ADRESI")
    sifre = os.getenv("EMAIL_SIFRESI")
    site_linki = "https://legaltech-aym.streamlit.app"
    
    # 1. Veritabanından Aboneleri Çek
    try:
        conn = sqlite3.connect("aym_arsiv.db")
        cursor = conn.cursor()
        cursor.execute("SELECT eposta FROM aboneler WHERE aktif_mi = 1")
        aboneler = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Veritabanı Hatası: {e}")
        return False

    if not aboneler:
        print("Gönderilecek abone bulunamadı.")
        return False

    # 2. HTML İçeriği (Yönlendirme Butonlu)
    html_icerik = f"""
    <html>
        <body style="font-family: sans-serif; border-top: 4px solid #e63946; padding: 20px;">
            <h2 style="color: #1d3557;">⚖️ AYM Karar Analiz Bülteni</h2>
            <p>Sayın Meslektaşım, sistemimiz yeni bir kararı analiz etti:</p>
            <div style="background: #f1faee; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <strong>Karar:</strong> {karar_basligi}<br><br>
                <p>Analiz özetine ve detaylı rapora web sitemiz üzerinden ulaşabilirsiniz.</p>
            </div>
            <div style="text-align: center;">
                <a href="{site_linki}" style="background-color: #e63946; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Analizi Web Sitesinde Görüntüle
                </a>
            </div>
            <p style="font-size: 11px; color: #777; margin-top: 30px;">LegalTech AYM Otomasyon Sistemi</p>
        </body>
    </html>
    """

    # 3. Mail Gönderim Süreci
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gonderen, sifre)
        
        for abone in aboneler:
            msg = MIMEMultipart()
            msg['From'] = gonderen
            msg['To'] = abone
            msg['Subject'] = f"Yeni AYM Karar Analizi: {karar_basligi[:50]}..."
            msg.attach(MIMEText(html_icerik, 'html'))
            server.send_message(msg)
            
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Hatası: {e}")
        return False