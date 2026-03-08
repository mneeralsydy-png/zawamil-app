import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.mmy.ye/cat/multimedia/issa-allaith/"

def scrape_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        data = {}
        
        # البحث عن جميع الروابط
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # شروط البحث عن روابط الصوتيات
            if href and ('.mp3' in href or 'download' in href or 'get_file' in href or 'zamel' in text.lower()):
                
                # استخراج السنة من النص أو الرابط
                year_match = re.search(r'20[0-9]{2}', text + href)
                year = year_match.group(0) if year_match else "أخرى"
                
                # تنظيف العنوان
                title = text
                if not title:
                    title = href.split('/')[-1]
                title = re.sub(r'تحميل|استماع|mp3|_|-', ' ', title).strip()
                
                if year not in data:
                    data[year] = []
                
                # إضافة الزامل إذا لم يكن مكرراً
                if not any(x['url'] == href for x in data[year]):
                    data[year].append({"title": title, "url": href})
        
        # ترتيب تنازلي للسنوات
        sorted_data = dict(sorted(data.items(), key=lambda item: item[0], reverse=True))
        return sorted_data

    except Exception as e:
        print(f"Error: {e}")
        return {}

if __name__ == "__main__":
    data = scrape_data()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Data updated successfully!")
