import os
from dotenv import load_dotenv
import base64
import requests
import io
from playwright.sync_api import sync_playwright
from openai import OpenAI
from pdf2image import convert_from_path
from database import db_kur, ozet_getir, ozet_kaydet
# YENİ: Mail gönderim fonksiyonunu içe aktar
from mail_manager import bulten_gonder

# Başlangıçta DB'yi hazırla
db_kur()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def start_process(tarih_str):
    year, month = tarih_str[:4], tarih_str[4:6]
    url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{tarih_str}.htm"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        aym_links = []
        links = page.locator("a").all()
        for link in links:
            href, text = link.get_attribute("href") or "", link.inner_text().strip()
            if "ANAYASA" in text.upper() and ".pdf" in href.lower():
                clean_href = href.split('/')[-1]
                full_url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{clean_href}"
                aym_links.append({"title": text, "url": full_url})
        browser.close()
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
            - SONUÇ VE PRATİK ETKİ
            Lütfen karar tarihini tam olarak oku."""},
            
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
    
    # 6. YENİ: E-POSTA BİLTENİ GÖNDER
    # Bu satır analiz biter bitmez mail_manager.py'yi tetikler
    try:
        bulten_gonder(karar_obj['title'], ai_ozet)
    except Exception as e:
        print(f"Bülten gönderilirken hata oluştu: {e}")

    return ai_ozet