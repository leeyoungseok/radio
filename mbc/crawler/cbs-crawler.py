import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_music_data(output_dir):
    #today =  '2024-12-13'
    today = datetime.now().strftime('%Y%m%d')
    url = f"https://www.cbs.co.kr/program/playlist/cbs_P000219?date={today}&sign=-"

    # Add headers to the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('li', class_='article')

    output_csv = f"{output_dir}cbs_playlist_{today}.csv"

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Title', 'Artist'])

        for article in articles:
            time = article.find('div', class_='time').text.strip() if article.find('div', class_='time') else ''
            title = article.find('div', class_='title').text.strip() if article.find('div', class_='title') else ''
            artist = article.find('div', class_='name').text.strip() if article.find('div', class_='name') else ''
            writer.writerow([time, title, artist])

    print(f"Music data saved to {output_csv}")

if __name__ == "__main__":
    output_directory = "/home/yslee/radio/cbs/"
    scrape_music_data(output_directory)
