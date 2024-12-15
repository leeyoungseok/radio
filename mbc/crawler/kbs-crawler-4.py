from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

# Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저를 숨김 모드로 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 브라우저 열기
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 음악 정보 저장을 위한 리스트
music_info_list = []

def clean_date(date_str):
    date_str = date_str.replace("(월)", "").replace("(화)", "").replace("(수)", "").replace("(목)", "").replace("(금)","").replace("(토)","").replace("(일)","")
    formatted_date = date_str.replace("년", "").replace(" ", "").replace(".", "").replace("월", "").replace("일","").replace("선곡내용","")
    return formatted_date

def save_to_file(date_str, music_info_list):
    # 날짜 문자열에서 파일 이름 형식으로 변환 (YYYYMMDD)
    date_str = date_str.replace("(월)", "Mon").replace("(화)", "Tue").replace("(수)", "Wed").replace("(목)", "Thrs").replace("(금)","Fri").replace("(토)","Sat").replace("(일)","Sun")
    formatted_date = date_str.replace("년", "").replace(" ", "").replace(".", "").replace("월", "").replace("일","-").replace("선곡내용","")
    file_name = f"{formatted_date}.txt"
    
    # 파일에 음악 정보를 기록
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f"날짜: {date_str}\n")
        file.write("-" * 80 + "\n")
        for music_info in music_info_list:
            file.write(f"{music_info}\n")
        file.write("-" * 80 + "\n")
    print(f"{file_name}에 저장 완료")

def crawl_page(page_number):
    # 해당 페이지로 이동
    url = f'https://pbbs.kbs.co.kr/general/list.html?bbs_id=R2007-0077-03-821927&page={page_number}#n'
    driver.get(url)
    
    time.sleep(2)  # 페이지 로드를 위한 대기
    
    print("page:", page_number)
    time.sleep(3)
    #input()
    # 게시글이 있는지 확인
    try:
        # 게시글 목록을 찾습니다.
        date_links = driver.find_elements(By.XPATH, "//a[@href='#view']")
        if not date_links:
            print(f"페이지 {page_number}에 게시글이 없습니다. 크롤링을 종료합니다.")
            return False  # 게시글이 없으면 False 반환하여 종료
        
        # 날짜 필드에서 연도 및 날짜 정보 추출
        date_fields = driver.find_elements(By.XPATH, "//td[@class='date']")
        #year_dates = [date_field.text.strip() for date_field in date_fields]
        year_dates = [date_field.text.strip().split('.')[0] + "년" for date_field in date_fields]  
        
    except Exception as e:
        print(f"페이지 {page_number}에서 오류 발생: {e}")
        return False
    
    # 날짜별 링크 추출
    dates = []
    full_links = []

    for link, year_date in zip(date_links, year_dates):
        today = datetime.now().strftime('%Y%m%d')
        onclick_text = link.get_attribute('onclick')
        date_text = link.text.strip()
        full_date = f"{year_date} {date_text}"  # 연도와 날짜를 결합
        clean_today = clean_date(full_date)
        print(today, clean_today)
        if today != clean_today : continue

        dates.append(full_date)
        # onclick 속성에서 필요한 ID 정보 추출
        if onclick_text:
            parts = onclick_text.split("'")
            if len(parts) > 5:
                post_id = parts[3]
                post_no = parts[5]
                post_link = f"https://pbbs.kbs.co.kr/general/read.html?bbs_id=R2007-0077-03-821927&id={post_id}&post_no={post_no}&page=1&post_header="
                full_links.append(post_link)

    # 각 링크에서 bbs_contents와 관련된 정보를 추출
    for date, post_link in zip(dates, full_links):
        driver.get(post_link)  # 해당 링크로 이동
        time.sleep(5)  # 페이지 로드를 위한 대기

        try:
            # 페이지 전체의 innerHTML을 가져옴
            page_source = driver.page_source
            
            # BeautifulSoup을 사용하여 page_source 파싱
            soup = BeautifulSoup(page_source, 'html.parser')

            # "board-box-cont" id="post_content" 내의 음악 정보 추출
            post_content = soup.find("div", {"class": "board-box-cont", "id": "post_content"})

            # 음악 정보가 있는 <span> 태그에서 텍스트 추출
            if post_content:
                #music_info = post_content.find_all("span", style="font-size: 16px;")
                music_info = post_content.find_all("span", style=lambda s: s and ("font-size: 16px;" in s or "font-size: 14px;" in s))

                music_texts = [info.text for info in music_info]
                
                # 파일로 저장
                save_to_file(date, music_texts)
                
            else:
                print(f"{date}의 내용을 찾지 못했습니다.")
        except Exception as e:
            print(f"{date}의 내용을 가져오지 못했습니다: {e}")
    
    return True  # 게시글이 있을 경우 True 반환

# 페이지 1부터 시작하여 최대 500 페이지까지 크롤링
for page in range(1, 2):
    if page % 5 == 0:
        time.sleep(10)
    if not crawl_page(page):
        break  # 게시글이 없는 페이지가 나오면 크롤링 종료

# 브라우저 종료
driver.quit()
