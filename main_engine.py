import os, io, base64, time, requests, fitz
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from openai import OpenAI
from database import db_kur, ozet_getir, ozet_kaydet

db_kur()
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def start_process(tarih_str):
    year, month = tarih_str[:4], tarih_str[4:6]
    url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{tarih_str}.htm"
    aym_links = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(2000)
            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()
                if "ANAYASA" in text.upper() and ".pdf" in href.lower():
                    clean_href = href.split('/')[-1]
                    full_url = f"https://www.resmigazete.gov.tr/eskiler/{year}/{month}/{clean_href}"
                    aym_links.append({"title": text, "url": full_url})
            browser.close()
        except: pass
    return aym_links

def download_and_summarize(karar_obj, tarih_str):
    kayitli = ozet_getir(karar_obj['url'])
    if kayitli: return kayitli

    pdf_res = requests.get(karar_obj['url'], headers={'User-Agent': 'Mozilla/5.0'})
    pdf_path = f"temp_{int(time.time())}.pdf"
    with open(pdf_path, 'wb') as f: f.write(pdf_res.content)
    
    try:
        doc = fitz.open(pdf_path)
        full_text, images = "", []
        for i in range(min(5, len(doc))):
            full_text += doc[i].get_text()
            pix = doc[i].get_pixmap(dpi=150)
            images.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(pix.tobytes('jpeg')).decode('utf-8')}"}})
        doc.close()

        # BİÇİMLENDİRME KURALLARI EKLENMİŞ PROMPT
        safe_prompt = """Sen profesyonel bir hukuk analiz asistanısın. 
        Analizini aşağıdaki Markdown formatına göre, başlıkları kalınlaştırarak ve maddeler kullanarak yap:

        ### 🏛 **KARARIN KİMLİĞİ**
        - (Esas No, Karar No, Karar Tarihi ve Tarafları buraya yaz)

        ### 📄 **SOMUT DÜZENLEME**
        - (İptali istenen kanun maddesini veya başvurunun konusunu net yaz)

        ### ⚖️ **HUKUKİ ÇATIŞMA**
        - (Hangi anayasal ilkenin ihlal edildiği iddiası olduğunu açıkla)

        ### 🧠 **MAHKEME GEREKÇESİ**
        - (Mahkemenin temel argümanlarını maddeler halinde yaz)

        ### 📌 **SONUÇ**
        - (İptal/Red/İhlal kararını ve varsa karşı oyları belirt)

        Not: Sadece nesnel verilere sadık kal, uydurma."""

        content = [{"type": "text", "text": safe_prompt + (f"\n\nMETİN:\n{full_text}" if len(full_text) > 300 else "\nLütfen görselleri analiz et: ")}]
        if len(full_text) <= 300: content += images

        completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": content}], temperature=0)
        ai_ozet = completion.choices[0].message.content
        ozet_kaydet(tarih_str, karar_obj['title'], karar_obj['url'], ai_ozet)
        return ai_ozet
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)