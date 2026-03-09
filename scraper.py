import requests
from bs4 import BeautifulSoup
import json
import re
import time

# رابط القسم الرئيسي
BASE_URL = "https://www.mmy.ye/cat/multimedia/issa-allaith/"
DOMAIN = "https://www.mmy.ye"

# ترويسة لتجنب الحظر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def run():
    print("Starting Deep Crawler...")
    soup = get_soup(BASE_URL)
    if not soup:
        print("Failed to load main page")
        return

    data = {}
    # البحث عن روابط المواضيع (الزوامل) في الصفحة الرئيسية
    post_links = set()
    
    # البحث عن جميع الروابط التي تبدو أنها روابط مواضيع
    for a in soup.find_all('a', href=True):
        href = a['href']
        # نتحقق أن الرابط تابع للموقع وليس رابط قسم أو صفحة رئيسية
        if DOMAIN in href and "/cat/" not in href and "index" not in href:
            # نفلتر الروابط غير المهمة
            if href.count("/") > 3: 
                 post_links.add(href)

    print(f"Found {len(post_links)} posts to scan. Scanning first 20...")

    # نقوم بفحص أول 20 رابط لتوفير الوقت (يمكن زيادتها لاحقاً)
    count = 0
    for link in list(post_links)[:20]:
        print(f"Scanning: {link}")
        post_soup = get_soup(link)
        if not post_soup: continue

        # استخراج العنوان
        title = "زامل"
        h1 = post_soup.find('h1')
        if h1: title = h1.get_text(strip=True)
        
        # استخراج السنة من العنوان
        year_match = re.search(r'20[0-2][0-9]', title)
        year = year_match.group(0) if year_match else "أخرى"

        # البحث عن رابط الصوت داخل الصفحة
        mp3_url = None
        
        # 1. البحث عن وسم audio أو source
        audio_tag = post_soup.find('audio')
        if audio_tag:
            src = audio_tag.get('src')
            source_tag = audio_tag.find('source')
            if src: mp3_url = src
            elif source_tag: mp3_url = source_tag.get('src')
        
        # 2. البحث عن رابط مباشر يحتوي mp3
        if not mp3_url:
            for a in post_soup.find_all('a', href=True):
                href = a['href']
                if '.mp3' in href:
                    mp3_url = href
                    break
        
        # تنظيف الرابط (إذا كان ناقصاً)
        if mp3_url and not mp3_url.startswith('http'):
            mp3_url = DOMAIN + mp3_url

        # الحفظ
        if mp3_url:
            if year not in data: data[year] = []
            # تجنب التكرار
            if not any(d['url'] == mp3_url for d in data[year]):
                data[year].append({"title": title, "url": mp3_url})
                print(f"Added: {title}")
                count += 1
        
        time.sleep(0.5) # تأدب مع السيرفر

    print(f"Total found: {count}")

    # إذا لم يجد شيء، نضع بيانات تجريبية
    if count == 0:
        print("Warning: No audio found. Check site structure.")
        data["2024"] = [{"title": "لم يتم العثور على زوامل (راجع الموقع)", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"}]

    # الحفظ في الملف
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Done.")

if __name__ == "__main__":
    run()
