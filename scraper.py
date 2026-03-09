import requests
from bs4 import BeautifulSoup
import json
import re

# رابط معاينة القناة كصفحة ويب
CHANNEL_URL = "https://t.me/s/zwamlallaith"

def run():
    print("Connecting to Telegram Channel Web Preview...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    all_data = {}
    
    try:
        # 1. جلب صفحة القناة
        response = requests.get(CHANNEL_URL, headers=headers, timeout=20)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. البحث عن الرسائل (كل رسالة في div خاص)
            messages = soup.find_all('div', class_='tgme_widget_message')
            
            print(f"Found {len(messages)} messages. Analyzing...")
            
            for msg in messages:
                # استخراج التاريخ لمعرفة السنة
                date_tag = msg.find('time')
                year = "أخرى"
                if date_tag and date_tag.has_attr('datetime'):
                    full_date = date_tag['datetime'] # Format: 2024-01-01T...
                    year = full_date[:4]
                
                # استخراج العنوان (من نص الرسالة)
                text_tag = msg.find('div', class_='tgme_widget_message_text')
                title = "زامل"
                if text_tag:
                    # نأخذ أول 50 حرف كعنوان
                    title = text_tag.get_text(strip=True)[:50]
                
                # استخراج رابط التحميل (يكون عادة زر تحميل أو رابط ملف)
                audio_url = None
                
                # الحالة الأولى: ملف صوتي مرفق (يظهر كزر تحميل)
                download_btn = msg.find('a', class_='tgme_widget_message_document_title')
                if download_btn and download_btn.has_attr('href'):
                    audio_url = download_btn['href']
                
                # الحالة الثانية: رابط خارجي في النص
                if not audio_url and text_tag:
                    links = text_tag.find_all('a')
                    for a in links:
                        href = a['href']
                        if '.mp3' in href or 'download' in href:
                            audio_url = href
                            break
                
                # حفظ البيانات
                if audio_url:
                    if year not in all_data:
                        all_data[year] = []
                    
                    # تنظيف العنوان قليلاً
                    title = re.sub(r'https?://\S+', '', title).strip()
                    if not title:
                        title = f"زامل {year}"
                        
                    all_data[year].append({
                        "title": title,
                        "url": audio_url
                    })

            # ترتيب السنوات تنازلياً
            sorted_data = dict(sorted(all_data.items(), key=lambda x: x[0], reverse=True))
            
            print(f"Total extracted: {sum(len(v) for v in sorted_data.values())}")
            
            # الحفظ
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, ensure_ascii=False, indent=4)
            print("Success! Data saved.")
            
        else:
            print("Failed to load Telegram page")
            # بيانات احتياطية
            save_fallback()
            
    except Exception as e:
        print(f"Error: {e}")
        save_fallback()

def save_fallback():
    data = {"2024": [{"title": "تعذر جلب البيانات (استخدم الكود يدوياً)", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"}]}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run()
