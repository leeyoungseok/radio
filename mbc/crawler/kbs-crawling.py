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
            links.append(post_id)
            full_links.append(post_link)

# 결과 출력 (날짜, ID, 전체 링크)
for date, post_id, post_link in zip(dates, links, full_links):
    print(f"Date: {date}, ID: {post_id}, Link: {post_link}")

# 브라우저 종료
driver.quit()
