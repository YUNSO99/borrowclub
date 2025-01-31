from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# 크롬 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 창을 띄우지 않음
options.add_argument('--disable-gpu')  # GPU 가속 비활성화
options.add_argument('--no-sandbox')  # 샌드박스 모드 비활성화 (Linux에서 유용)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")

# 웹드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 크롤링할 URL
url = "https://oasis.ssu.ac.kr/search/ebook-collections?offset=0&max=100"
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

        # '다음' 버튼 찾기
        next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mat-paginator-navigation-next')))
        
        # '다음' 버튼이 비활성화되었으면 종료
        if not next_button.is_enabled():
            print("마지막 페이지입니다.")
            break

        # 버튼이 활성화될 때까지 기다렸다가 클릭
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.mat-paginator-navigation-next'))).click()
        
        # 페이지 로딩 대기 (새 페이지의 책 제목이 나타날 때까지)
        WebDriverWait(driver, 10).until(EC.staleness_of(titles[0]))

    except Exception as e:
        print(f"오류 발생: {e}")
        break

# CSV 파일로 저장
with open('book_titles.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Book Title"])  # 헤더 작성
    for title in book_titles:
        writer.writerow([title])  # 책 제목을 한 줄씩 작성

# 브라우저 종료
driver.quit()
