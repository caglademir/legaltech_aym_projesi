from mail_manager import yeni_karar_duyurusu
from database import db_kur
import sqlite3

# 1. Veritabanını ve tabloları hazırla
db_kur()

# 2. Test mailini abone listesine ekle (zaten varsa hata vermez)
conn = sqlite3.connect("aym_arsiv.db")
cursor = conn.cursor()
try:
    cursor.execute("INSERT INTO aboneler (eposta, kayit_tarihi) VALUES (?, ?)", 
                   ("aym.kararlari@gmail.com", "2025-12-18"))
    conn.commit()
    print("Abone listesi güncellendi.")
except sqlite3.IntegrityError:
    print("Bu e-posta zaten abone listesinde.")
conn.close()

# 3. YENİ FONKSİYONU TEST ET
# Farz edelim ki bugün 3 yeni karar yayımlandı
print("Bildirim gönderiliyor...")
sonuc = yeni_karar_duyurusu(3) 

if sonuc:
    print("BAŞARILI: Bildirim maili gönderildi!")
else:
    print("HATA: Mail gönderilemedi. Terminal loglarını kontrol et.")