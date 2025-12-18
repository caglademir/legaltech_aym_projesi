import sqlite3

def db_kur():
    conn = sqlite3.connect("aym_arsiv.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kararlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            baslik TEXT,
            url TEXT UNIQUE,
            ozet TEXT,
            eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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