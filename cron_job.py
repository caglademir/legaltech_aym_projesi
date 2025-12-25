from main_engine import start_process, download_and_summarize
from mail_manager import yeni_karar_duyurusu
from datetime import datetime
import time

def daily_check():
    bugun = datetime.now().strftime('%Y%m%d')
    print(f"[{datetime.now()}] Kontrol başlıyor: {bugun}")
    
    # 1. Bugünün linklerini bul
    aym_linkleri = start_process(bugun)
    
    if not aym_linkleri:
        print("Bugün yeni AYM kararı bulunamadı.")
        return

    islenen_karar_sayisi = 0
    
    # 2. Her bir kararı indir ve analiz et (Download & Summarize)
    for karar in aym_linkleri:
        try:
            print(f"Analiz ediliyor: {karar['title']}")
            # Bu fonksiyon hem AI analizini yapar hem DB'ye kaydeder
            download_and_summarize(karar, bugun)
            islenen_karar_sayisi += 1
            # OpenAI API limitlerine takılmamak ve sunucuyu yormamak için kısa bir es
            time.sleep(2) 
        except Exception as e:
            print(f"Karar işlenirken hata oluştu ({karar['url']}): {e}")

    # 3. Eğer en az bir karar başarıyla işlendiyse duyuru yap
    if islenen_karar_sayisi > 0:
        print(f"Toplam {islenen_karar_sayisi} karar işlendi. Mail gönderiliyor...")
        yeni_karar_duyurusu(islenen_karar_sayisi)
    else:
        print("Karar linkleri bulundu ama analiz edilemedi.")

if __name__ == "__main__":
    daily_check()