from main_engine import start_process
from mail_manager import yeni_karar_duyurusu
from datetime import datetime

def daily_check():
    # Bugünün tarihini al (Örn: 20251218)
    bugun = datetime.now().strftime('%Y%m%d')
    
    # Bugünün gazetesini tara
    kararlar = start_process(bugun)
    
    # EĞER KARAR VARSA MAİL GÖNDER
    if len(kararlar) > 0:
        print(f"Bugün {len(kararlar)} karar bulundu, mail gönderiliyor...")
        yeni_karar_duyurusu(len(kararlar))
    else:
        print("Bugün yeni AYM kararı yok.")

if __name__ == "__main__":
    daily_check()