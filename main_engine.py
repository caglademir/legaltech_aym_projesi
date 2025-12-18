import os
from dotenv import load_dotenv
import base64
import requests
import io
from playwright.sync_api import sync_playwright
from openai import OpenAI
from pdf2image import convert_from_path
from database import db_kur, ozet_getir, ozet_kaydet
from mail_manager import yeni_karar_duyurusu

# Başlangıçta DB'yi hazırla
db_kur()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def start_process(tarih_str):
    year, month = tarih_str[:4], tarih_str[4:6]
    url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{tarih_str}.htm"
    aym_links = []
    
    try:
        with sync_playwright() as p:
            # Buradaki try-except tarayıcı başlatma hatalarını yakalar
            try:
                browser = p.chromium.launch(headless=True)
            except Exception:
                # Eğer sunucuda tarayıcı yoksa anında kurmayı dener
                os.system("playwright install chromium")
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()
            # Timeout süresini artırıyoruz ve hata oluşursa boş liste dönmesini sağlıyoruz
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                
                links = page.locator("a").all()
                for link in links:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    if "ANAYASA" in text.upper() and ".pdf" in href.lower():
                        clean_href = href.split('/')[-1]
                        full_url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{clean_href}"
                        aym_links.append({"title": text, "url": full_url})
            except Exception as e:
                print(f"Resmi Gazete sayfa hatası (Muhtemelen bugün gazete yok): {e}")
            finally:
                browser.close()
    except Exception as e:
        print(f"Playwright genel hatası: {e}")
        return [] # Hata olsa bile uygulama çökmez, boş liste döner.

    # Sadece link varsa mail gönder
    if len(aym_links) > 0:
        try:
            yeni_karar_duyurusu(len(aym_links))
        except:
            pass
            
    return aym_links

def download_and_summarize(karar_obj, tarih_str):
    # 1. VERİTABANI KONTROLÜ
    kayitli_ozet = ozet_getir(karar_obj['url'])
    if kayitli_ozet:
       return kayitli_ozet

    # 2. PDF İNDİRME
    headers = {'User-Agent': 'Mozilla/5.0'}
    pdf_res = requests.get(karar_obj['url'], headers=headers)
    pdf_path = "temp_karar.pdf"
    with open(pdf_path, 'wb') as f:
        f.write(pdf_res.content)
    
    # 3. GÖRÜNTÜYE ÇEVİRME (OCR)
    images = convert_from_path(pdf_path, dpi=300) 
    buffered = io.BytesIO()
    images[0].save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # 4. ANALİZ TALEBİ
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """Sen kıdemli bir hukuk müşavirisin. 
            Görevini şu adımlarla icra et:
            1. Önce kararın 'Hukuki Alanını' tespit et.
            2. Tespit ettiğin alana göre aşağıdaki detaylı şablonu doldur:
            - KARARIN KİMLİĞİ
            - SOMUT DÜZENLEME
            - HUKUKİ ÇATIŞMA
            - MAHKEMENİN GEREKÇELİ GÖRÜŞÜ
            - SONUÇ VE PRATİK ETKİ"""},
            
            {"role": "user", "content": [
                {"type": "text", "text": "Bu AYM kararını analiz et:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        temperature=0.2
    )
    
    ai_ozet = completion.choices[0].message.content
    
    # 5. KAYDET
    ozet_kaydet(tarih_str, karar_obj['title'], karar_obj['url'], ai_ozet)
    
    return ai_ozet