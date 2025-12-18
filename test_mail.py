from mail_manager import bulten_gonder
from database import db_kur
import sqlite3

# 1. Önce tablonun oluştuğundan emin olalım
db_kur()

# 2. Test mailini ekleyelim
conn = sqlite3.connect("aym_arsiv.db")
cursor = conn.cursor()
try:
    # Kendi mailini buraya yaz
    cursor.execute("INSERT INTO aboneler (eposta, kayit_tarihi) VALUES (?, ?)", 
                   ("KENDI_MAIL_ADRESIN@gmail.com", "2025-12-18"))
    conn.commit()
    print("Abone eklendi.")
except sqlite3.IntegrityError:
    print("Abone zaten mevcut.")
conn.close()

# 3. Maili gönder
print("Mail gönderiliyor...")
sonuc = bulten_gonder("TEST KARARI", "Bu bir test analizidir. Analiz motoru çalışıyor!")
print("Gönderim sonucu:", sonuc)
