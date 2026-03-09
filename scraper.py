import requests
from bs4 import BeautifulSoup
import json
import re
import os

# رابط القسم الرئيسي
BASE_URL = "https://www.mmy.ye/cat/multimedia/issa-allaith/"

def get_all_zawamil():
    print("جاري جلب الزوامل من الموقع...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    all_data = {}
    
    try:
        # 1. جلب الصفحة الرئيسية
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. البحث عن جميع الروابط في الصفحة
        # الموقع عادة يضع الروابط داخل وسوم معينة، سنبحث عن كل الروابط
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # نريد فقط روابط التحميل أو التي تحتوي على امتداد صوتي أو كلمة زامل
            # لاحظ: بعض المواقع لا تظهر الرابط المباشر في الصفحة الرئيسية، بل داخل صفحة تفاصيل
            # سنحاول جلب الروابط المباشرة أولاً
            
            is_audio = '.mp3' in href
            is_download_text = 'تحميل' in text or 'استماع' in text or 'زامل' in text
            
            if is_audio or is_download_text:
                # محاولة استخراج السنة
                year_match = re.search(r'20[0-2][0-9]', text + href)
                year = year_match.group(0) if year_match else "زوامل متنوعة"
                
                # تنظيف العنوان
                title = text
                if not title:
                    title = href.split('/')[-1].replace('.mp3', '')
                title = re.sub(r'تحميل|استماع|mp3', '', title, flags=re.IGNORECASE).strip()
                
                # إذا كان الرابط غير كامل (يبدأ بـ /) نكمله
                if href.startswith('/'):
                    href = "https://www.mmy.ye" + href
                
                # إضافة للقائمة
                if year not in all_data:
                    all_data[year] = []
                
                # تجنب التكرار
                if not any(d['url'] == href for d in all_data[year]):
                    all_data[year].append({"title": title, "url": href})
        
        # 3. التعامل مع الصفحات الفرعية (Pagination) - محاولة البحث في صفحات التفاصيل
        # هذا الجزء سيبحث عن روابط لمواضيع أخرى قد تحتوي على صوتيات
        article_links = soup.select('h2 a, h3 a, .post-title a')
        for art_link in article_links[:10]: # نأخذ أول 10 مواضيع للتجربة السريعة
            art_href = art_link.get('href', '')
            if art_href.startswith('/'):
                art_href = "https://www.mmy.ye" + art_href
            
            try:
                sub_res = requests.get(art_href, headers=headers, timeout=5)
                sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                sub_audio = sub_soup.find('a', href=lambda x: x and '.mp3' in x)
                
                if sub_audio:
                    mp3_link = sub_audio['href']
                    title_text = sub_soup.find('h1').get_text(strip=True) if sub_soup.find('h1') else "زامل"
                    
                    year_match = re.search(r'20[0-2][0-9]', title_text + mp3_link)
                    year = year_match.group(0) if year_match else "زوامل متنوعة"
                    
                    if year not in all_data: all_data[year] = []
                    if not any(d['url'] == mp3_link for d in all_data[year]):
                        all_data[year].append({"title": title_text, "url": mp3_link})
            except:
                continue

        print(f"تم جمع {sum(len(v) for v in all_data.values())} زامل.")
        
        # ترتيب القائمة تنازلياً
        sorted_data = dict(sorted(all_data.items(), key=lambda item: item[0], reverse=True))
        return sorted_data

    except Exception as e:
        print(f"حدث خطأ: {e}")
        return {}

# تشغيل الكود وحفظ الملف
data = get_all_zawamil()
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
