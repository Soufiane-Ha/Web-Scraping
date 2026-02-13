import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

channels = []

for page in range(1, 6):
    url = f"https://thingspeak.mathworks.com/channels/public?page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='card channel-card')
        for card in cards:
            header = card.find('div', class_='card-header')
            links = header.find_all('a')
            name = links[1].text.strip() if len(links) > 1 else None

            channel_id_tag = card.find('strong')
            channel_id = channel_id_tag.text.strip() if channel_id_tag else None

            author_tag = card.find('a', href=lambda x: x and "/users/" in x)
            author = author_tag.text.strip() if author_tag else None

            desc_tag = card.find('p', class_='public_channel_description')
            description = desc_tag.text.strip() if desc_tag else ''

            tags_section = card.find('div', class_='public_channel_tags')
            tags = [tag.text.strip() for tag in tags_section.find_all('a')] if tags_section else []

            channels.append({
                "Page": page,
                "ID": channel_id,
                "Name": name,
                "Author": author,
                "Description": description,
                "Tags": tags
            })
        print(f"Page {page} done")
    else:
        print("Error:", response.status_code)
    time.sleep(2)  

print(f"Total channels collected: {len(channels)}")
keywords = [
    # الحرارة والرطوبة
    'temperature', 'temp', 'humidity', 'hygrometer', 'dht11', 'dht22', 'bmp180', 'bmp280', 'bme280',
    
    # الضغط
    'pressure', 'barometer', 'bmp180', 'bmp280', 'bme280',
    
    # الماء / مستوى السائل
    'water', 'water level', 'ultrasonic', 'ultraschall', 'waterflow', 'flowmeter', 'rain', 'turbidity',
    
    # الغاز / جودة الهواء
    'gas', 'mq2', 'mq3', 'mq5', 'mq7', 'mq135', 'co2', 'co', 'smoke', 'air quality', 'voc',
    
    # الضوء
    'light', 'luminance', 'photoresistor', 'ldr', 'lux', 'photocell',
    
    # المسافة / الحركة
    'distance', 'ultrasonic', 'infrared', 'pir', 'proximity', 'motion', 'accelerometer', 'gyroscope',
    
    # الصوت
    'sound', 'microphone', 'noise', 'decibel', 'mic',
    
    # الحرارة الأرضية أو التربة
    'soil', 'soil moisture', 'moisture', 'ph', 'temperature sensor',
    
    # الطاقة / كهرباء
    'voltage', 'current', 'ampere', 'power', 'energy', 'pzem', 'acs712',
    
    # كاميرات ومستشعرات صورة
    'camera', 'video', 'motion sensor', 'photo',
    
    # Misc / عامة
    'smoke', 'fire', 'uv', 'gps', 'rfid', 'weight', 'load cell', 'capacitive', 'touch', 'magnet', 'magnetometer'
]

for ch in channels:
    text = ch['Description'].lower() + " " + " ".join([t.lower() for t in ch['Tags']])
    sensors = [k for k in keywords if k in text]
    ch['Sensors'] = sensors if sensors else ['Unknown']
df = pd.DataFrame(channels)
df.insert(0, 'N', range(1, len(df)+1))  # إضافة ترقيم
df.to_csv("thingspeak_channels.csv", index=False, encoding='utf-8-sig')
print("CSV saved successfully!")
import matplotlib.pyplot as plt

all_sensors = [sensor for ch in channels for sensor in ch['Sensors']]
sensor_counts = pd.Series(all_sensors).value_counts()

plt.figure(figsize=(10,6))
sensor_counts.plot(kind='bar', color='skyblue')
plt.title("Frequency of Sensors in ThingSpeak Channels")
plt.xlabel("Sensor Type")
plt.ylabel("Number of Senser")
plt.xticks(rotation=45)
plt.show()
