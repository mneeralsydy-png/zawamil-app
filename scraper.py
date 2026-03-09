import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys

# الروابط والإعدادات
START_URL = "https://www.mmy.ye/cat/multimedia/issa-allaith/?archive_query=title&alphabet_filter"
BASE_DOMAIN = "https://www.mmy.ye"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_mp3_from_page(post_url):
    """يدخل لصفحة الزامل ويبحث عن رابط MP3"""
    soup = get_soup(post_url)
    if not soup: return None

    # 1. البحث في وسم audio
    audio = soup.find('audio')
    if audio and audio.get('src'):
        return audio['src']
    
    # 2. البحث في source داخل audio
    if audio:
        source = audio.find('source')
        if source and source.get('src'):
            return source['src']

    # 3. البحث عن روابط تحميل تحتوي .mp3
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.mp3' in href:
            return href
            
    # 4. البحث في النصوص (أحياناً يكون الرابط مكتوب نصاً)
    text = soup.get_text()
    mp3_match = re.search(r'https?://[^\s"<>]+\.mp3', text)
    if mp3_match:
        return mp3_match.group(0)
        
    return None

def run():
    print("Starting Massive Crawler for Issa Allaith...")
    
    all_data = {}
    posts_to_scan = []
    
    # --- المرحلة الأولى: جمع روابط جميع الزوامل من جميع الصفحات ---
    current_url = START_URL
    page_num = 1
    
    while current_url:
        print(f"Scanning List Page {page_num}...")
        soup = get_soup(current_url)
        if not soup: break

        # البحث عن روابط الزوامل في القائمة
        # عادة تكون داخل h2 أو h3 أو div معين، سنبحث عن كل الروابط ونفلترها
        found_count = 0
        for a in soup.find_all('a', href=True):
            href = a['href']
            # نتأكد أن الرابط يشير لموضوع وليس لصفحة رئيسية
            if DOMAIN in href and "/cat/" not in href and "/page/" not in href and "archive_query" not in href:
                if href not in posts_to_scan:
                    posts_to_scan.append(href)
                    found_count += 1
        
        print(f"Found {found_count} new posts. Total accumulated: {len(posts_to_scan)}")

        # البحث عن رابط الصفحة التالية (Pagination)
        next_link = soup.find('a', string=re.compile(r'التالي|Next|»'))
        if next_link and next_link.get('href'):
            current_url = next_link['href']
            if not current_url.startswith('http'):
                current_url = BASE_DOMAIN + current_url
            page_num += 1
            time.sleep(1) # راحة قصيرة
        else:
            print("No more pages.")
            break
        
        # وقف اذا وصلنا لعدد كبير جداً (للسلامة)
        if page_num > 40: break

    # --- المرحلة الثانية: سحب روابط الصوت من كل زامل ---
    print(f"\nTotal posts found: {len(posts_to_scan)}")
    print("Starting deep extraction... (This might take time)")
    
    processed = 0
    for post_url in posts_to_scan:
        processed += 1
        # طباعة التقدم كل 10 روابط
        if processed % 10 == 0:
            print(f"Processing {processed}/{len(posts_to_scan)}...")
        
        title_guess = post_url.split('/')[-1].replace('-', ' ') # تخمين العنوان من الرابط
        mp3_url = extract_mp3_from_page(post_url)
        
        if mp3_url:
            # استخراج السنة (تخمين من العنوان أو الرابط)
            year_match = re.search(r'20[0-2][0-9]', title_guess + post_url)
            year = year_match.group(0) if year_match else "زوامل متنوعة"
            
            if year not in all_data: all_data[year] = []
            
            # تنظيف العنوان
            title = title_guess
            
            all_data[year].append({"title": title, "url": mp3_url})
        
        time.sleep(0.5) # مهم جداً لعدم الحظر

    # --- الحفظ ---
    print("Saving data...")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    
    print("Done! Total audio files extracted:", sum(len(v) for v in all_data.values()))

if __name__ == "__main__":
    run()
