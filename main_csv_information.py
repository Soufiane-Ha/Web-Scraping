import requests
from bs4 import BeautifulSoup
import time
import csv


channels = []

for page in range(1, 199):   

    url = f"https://thingspeak.mathworks.com/channels/public?page={page}"
    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='card channel-card')

        for card in cards:

            header = card.find('div', class_='card-header')
            links = header.find_all('a')
            name = links[1].text.strip() if len(links) > 1 else None

            #  Channel ID
            channel_id_tag = card.find('strong')
            channel_id = channel_id_tag.text.strip() if channel_id_tag else None

            #  Author
            author_tag = card.find('a', href=lambda x: x and "/users/" in x)
            author = author_tag.text.strip() if author_tag else None

            #  Description
            desc_tag = card.find('p', class_='public_channel_description')
            description = desc_tag.text.strip() if desc_tag else None

            #  Progress
            progress = card.find('div', class_='progress-bar')
            percentage = progress['aria-valuenow'] if progress else None


            #  Tags
            tags_section = card.find('div', class_='public_channel_tags')
            tags = [tag.text.strip() for tag in tags_section.find_all('a')] if tags_section else []

            channels.append({
                "Name": name,
                "ID": channel_id,
                "Author": author,
                "Description": description,
                "Tags": tags,
                "percentage": percentage,
                "Page": page
            })

        print(f"Page {page} done")

    else:
        print("Error:", response.status_code)

    time.sleep(2)   



with open('thingspeak.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    
    writer.writerow(['N','Page','Channel ID','Name','Author','Description','percentage','Tags'])

    for i, ch in enumerate(channels, start=1):
        writer.writerow([
            i,
            ch['Page'],
            ch['ID'],
            ch['Name'],
            ch['Author'],
            ch['Description'],
            ch['percentage'],
            ",".join(ch['Tags'])
        ])


print("Data Saved Successfully!")
