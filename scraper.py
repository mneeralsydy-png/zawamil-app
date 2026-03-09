import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.mmy.ye/cat/multimedia/issa-allaith/"

def run():
    print("Starting scraper...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    data = {}
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن جميع الروابط
            links = soup.find_all('a')
            
            count = 0
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # البحث عن روابط الصوت أو كلمة تحميل
                if href and ('.mp3' in href or 'download' in href or 'get_file' in href):
                    
                    # استخراج السنة
                    year_match = re.search(r'20[0-9]{2}', text + href)
                    year = year_match.group(0) if year_match else "أخرى"
                    
                    # تنظيف العنوان
                    title = text if text else href.split('/')[-1]
                    title = re.sub(r'تحميل|استماع|mp3', '', title, flags=re.IGNORECASE).strip()
                    
                    if year not in data: data[year] = []
                    
                    # تجنب التكرار
                    if not any(d['url'] == href for d in data[year]):
                        data[year].append({"title": title, "url": href})
                        count += 1
            
            print(f"Found {count} audio files.")
            
            # إذا لم يجد شيئاً، نضع بيانات تجريبية لضمان عدم فراغ التطبيق
            if count == 0:
                print("No links found, using demo data.")
                data["2024"] = [{"title": "زامل تجريبي (لم يتم العثور على روابط)", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"}]
                
        else:
            print("Failed to retrieve page")
            
    except Exception as e:
        print(f"Error: {e}")
        data["خطأ"] = [{"title": "حدث خطأ في الجلب", "url": ""}]

    # حفظ الملف
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Data saved to data.json")

if __name__ == "__main__":
    run()
