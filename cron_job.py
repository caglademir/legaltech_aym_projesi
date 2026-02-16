from main_engine import start_process, download_and_summarize
from mail_manager import yeni_karar_duyurusu
from datetime import datetime
import time
import schedule

def daily_check():
    bugun = datetime.now().strftime('%Y%m%d')
    print(f"[{datetime.now()}] Kontrol başlıyor: {bugun}")
    
    # 1. Bugünün linklerini bul
    aym_linkleri = start_process(bugun)
    
    if not aym_linkleri:
        print("Bugün yeni AYM kararı bulunamadı.")
        return

    islenen_kararlar = []
    
    # 2. Her bir kararı indir ve analiz et (Download & Summarize)
    for karar in aym_linkleri:
        try:
            print(f"Analiz ediliyor: {karar['title']}")
            # Bu fonksiyon hem AI analizini yapar hem DB'ye kaydeder
            download_and_summarize(karar, bugun)
            islenen_kararlar.append(karar)
            # OpenAI API limitlerine takılmamak ve sunucuyu yormamak için kısa bir es
            time.sleep(2) 
        except Exception as e:
            print(f"Karar işlenirken hata oluştu ({karar['url']}): {e}")

    # 3. Eğer en az bir karar başarıyla işlendiyse duyuru yap
    if islenen_kararlar:
        print(f"Toplam {len(islenen_kararlar)} karar işlendi. Mail gönderiliyor...")
        yeni_karar_duyurusu(islenen_kararlar)
    else:
        print("Karar linkleri bulundu ama analiz edilemedi.")

def run_scheduler():
    print("Zamanlayıcı başlatıldı. Her gün 08:00'de kontrol yapılacak.")
    # Her gün 08:00'de çalışacak şekilde ayarla
    schedule.every().day.at("08:00").do(daily_check)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Test amaçlı hemen bir kez çalıştırılabilir, production'da sadece run_scheduler() çağrılır.
    # daily_check() 
    run_scheduler()