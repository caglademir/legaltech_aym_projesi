import sqlite3

import datetime

def abone_ekle(eposta):
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    try:
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO aboneler (eposta, kayit_tarihi, aktif_mi) VALUES (?, ?, 1)", (eposta, tarih))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_kur():
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    
    # Kararlar tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS kararlar 
                     (tarih TEXT, baslik TEXT, ozet TEXT, url TEXT)''')
    
    # EKSİK OLAN TABLO BURASI:
    cursor.execute('''CREATE TABLE IF NOT EXISTS aboneler 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      eposta TEXT UNIQUE, 
                      kayit_tarihi TEXT, 
                      aktif_mi INTEGER DEFAULT 1)''')
    
    conn.commit()
    conn.close()

def ozet_kaydet(tarih, baslik, url, ozet):
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kararlar (tarih, baslik, url, ozet) VALUES (?, ?, ?, ?)",
                       (tarih, baslik, url, ozet))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Zaten varsa üzerine yazma
    finally:
        conn.close()

def ozet_getir(url):
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ozet FROM kararlar WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def ozetlerde_ara(anahtar_kelime):
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    # Özetin veya başlığın içinde geçen kelimeyi arar
    sorgu = "SELECT tarih, baslik, ozet, url FROM kararlar WHERE ozet LIKE ? OR baslik LIKE ?"
    cursor.execute(sorgu, (f'%{anahtar_kelime}%', f'%{anahtar_kelime}%'))
    results = cursor.fetchall()
    conn.close()
    return results