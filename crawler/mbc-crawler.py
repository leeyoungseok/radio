from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저를 숨김 모드로 실행
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

# 날짜와 링크 수집
for row in table_rows:
    columns = row.find_elements(By.TAG_NAME, 'td')
    date = columns[0].text.strip()  # 날짜
    link_element = columns[1].find_element(By.TAG_NAME, 'a')
    link = link_element.get_attribute('href')  # 링크
    
    # 날짜와 링크를 저장
    dates_and_links.append((date, link))

# 수집한 날짜별 링크를 출력
for date, link in dates_and_links:
    print(f"날짜: {date}, 링크: {link}")

# 각 링크 방문하여 선곡 정보 추출
for date, link in dates_and_links:
    driver.get(link)
    time.sleep(1)  # 페이지 로드를 위한 대기

    try:
        # <div id='musicView'>에서 선곡 정보 추출
        music_view = driver.find_element(By.ID, 'musicView')
        table_rows = music_view.find_elements(By.XPATH, ".//tbody/tr")
        
        print(f"\n날짜: {date} 선곡 정보:")
        
        for row in table_rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            song_number = columns[0].text.strip()  # 노래번호
            song_title = columns[1].text.strip()   # 노래제목
            artist = columns[2].text.strip()       # 가수

            # 노래번호, 노래제목, 가수 출력
            print(f"노래번호: {song_number}, 노래제목: {song_title}, 가수: {artist}")

    except Exception as e:
        print(f"{date}의 내용을 가져오지 못했습니다: {e}")

# 브라우저 종료
driver.quit()
