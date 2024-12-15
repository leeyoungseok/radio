from bs4 import BeautifulSoup
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

# 메인 페이지 열기
url = 'https://program.kbs.co.kr/1fm/radio/musicall/pc/board.html?smenu=c1ef1a&bbs_loc=R2007-0077-03-821927,list,none,1,0'
driver.get(url)

# iframe이 로드될 때까지 대기
time.sleep(3)

# iframe으로 전환
iframe = driver.find_element(By.ID, 'one_board')
driver.switch_to.frame(iframe)

# 날짜별 링크 추출
links = []
dates = []
full_links = []

# 날짜 링크는 "a" 태그로 감싸져 있으며, href와 onclick 속성을 가진다.
date_links = driver.find_elements(By.XPATH, "//a[@href='#view']")

for link in date_links:
    onclick_text = link.get_attribute('onclick')
    date_text = link.text.strip()
    dates.append(date_text)

    # onclick 속성에서 필요한 ID 정보 추출
    if onclick_text:
        parts = onclick_text.split("'")
        if len(parts) > 5:
            post_id = parts[3]
            post_no = parts[5]
            post_link = f"https://pbbs.kbs.co.kr/general/read.html?bbs_id=R2007-0077-03-821927&id={post_id}&post_no={post_no}&page=1&post_header="
            full_links.append(post_link)

# 음악 정보 저장을 위한 리스트
music_info_list = []

# 각 링크에서 bbs_contents와 관련된 정보를 추출
for date, post_link in zip(dates, full_links):
    driver.get(post_link)  # 해당 링크로 이동
    time.sleep(1)  # 페이지 로드를 위한 대기

    try:
        # 페이지 전체의 innerHTML을 가져옴
        page_source = driver.page_source
        
        # BeautifulSoup을 사용하여 page_source 파싱
        soup = BeautifulSoup(page_source, 'html.parser')

        # "board-box-cont" id="post_content" 내의 음악 정보 추출
        post_content = soup.find("div", {"class": "board-box-cont", "id": "post_content"})

        # 음악 정보가 있는 <span> 태그에서 텍스트 추출
        if post_content:
            music_info = post_content.find_all("span", style="font-size: 16px;")
            print(f"날짜: {date}")
            for info in music_info:
                print(info.text)
            print("-" * 80)
            
            # 음악 정보 리스트에 저장
            music_info_list.append({
                'date': date,
                'link': post_link,
                'music_info': [info.text for info in music_info]
            })
        else:
            print(f"{date}의 내용을 찾지 못했습니다.")
    except Exception as e:
        print(f"{date}의 내용을 가져오지 못했습니다: {e}")

# 브라우저 종료
driver.quit()

# 추가 작업: 음악 정보 결과 출력
print("\n=== 음악 정보 리스트 ===\n")
for item in music_info_list:
    print(f"날짜: {item['date']}")
    print(f"링크: {item['link']}")
    for music in item['music_info']:
        print(f"음악 정보: {music}")
    print("-" * 80)
