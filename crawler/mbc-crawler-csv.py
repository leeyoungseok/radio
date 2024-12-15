import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 브라우저 열기
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# MBC 라디오 선곡표 페이지 열기
url = 'https://www.imbc.com/broad/radio/fm4u/musiccamp/musictable/index.html'
driver.get(url)

# iframe이 로드될 때까지 대기
time.sleep(3)

# iframe으로 전환
iframe = driver.find_element(By.ID, 'songlist_frame')
driver.switch_to.frame(iframe)

# <div id='musicWrap'> 찾기
music_wrap = driver.find_element(By.ID, 'musicWrap')

# 날짜별 링크 추출
table_rows = music_wrap.find_elements(By.XPATH, ".//tbody/tr")
dates_and_links = []

for row in table_rows:
    columns = row.find_elements(By.TAG_NAME, 'td')
    date = columns[0].text.strip()
    link_element = columns[1].find_element(By.TAG_NAME, 'a')
    link = link_element.get_attribute('href')
    dates_and_links.append((date, link))

# 각 링크 방문하여 선곡 정보 추출 및 저장
count = 0
for date, link in dates_and_links:
    if count == 1:
        break
    driver.get(link)
    time.sleep(1)

    try:
        # <div id='musicView'>에서 선곡 정보 추출
        music_view = driver.find_element(By.ID, 'musicView')
        table_rows = music_view.find_elements(By.XPATH, ".//tbody/tr")

        # 선곡 정보를 리스트로 저장
        playlist = []
        for row in table_rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            song_number = columns[0].text.strip()
            song_title = columns[1].text.strip()
            artist = columns[2].text.strip()
            playlist.append({'No': song_number, 'Title': song_title, 'Artist': artist})

        # 날짜별로 CSV 파일 저장
        filename = f"mbc_playlist_{date.replace('-', '')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['No', 'Title', 'Artist'])
            writer.writeheader()
            writer.writerows(playlist)

        print(f"Saved playlist for {date} to {filename}")
        count += 1

    except Exception as e:
        print(f"{date}의 내용을 가져오지 못했습니다: {e}")

# 브라우저 종료
driver.quit()
