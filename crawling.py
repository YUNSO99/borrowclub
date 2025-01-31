import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# 로깅 설정
logging.basicConfig(filename='crawler_errors.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 크롬 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 창을 띄우지 않음
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")

# 웹드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 크롤링할 URL
url = "https://oasis.ssu.ac.kr/search/ebook-collections?offset=0&max=50"
driver.get(url)

# 책 제목을 저장할 리스트
book_titles = []

while True:
    try:
        # 책 제목이 나타날 때까지 기다림
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ikc-biblio-title')))
        titles = driver.find_elements(By.CSS_SELECTOR, '.ikc-biblio-title')

        # 제목 리스트 저장
        for title in titles:
            book_titles.append(title.text.strip()) 
            print(title.text.strip())

        # '다음' 버튼이 활성화된 경우에만 클릭하도록 수정
        next_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mat-paginator-navigation-next')))
        
        # '다음' 버튼이 비활성화되었는지 확인
        if "disabled" in next_button.get_attribute("class"):
            print("마지막 페이지입니다.")
            break
        # '다음' 버튼 클릭
        next_button.click()

        # 페이지가 로딩될 때까지 기다림
        WebDriverWait(driver, 10).until(EC.staleness_of(titles[0]))  # 페이지 로딩 후 새로 로드된 요소 기다림

    except Exception as e:
        # 오류 발생 시 로깅
        logging.error(f"오류 발생: {e}")
        break

# CSV 파일로 저장
with open('book_titles.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Book Title"])  # 헤더 작성
    for title in book_titles:
        writer.writerow([title])  # 책 제목을 한 줄씩 작성

# 브라우저 종료
driver.quit()
