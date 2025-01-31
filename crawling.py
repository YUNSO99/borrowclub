import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

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
driver.set_page_load_timeout(15)  # 페이지 로딩 타임아웃 설정

# 크롤링할 URL
url = "https://oasis.ssu.ac.kr/search/ebook-collections?offset=0&max=100"
book_titles = []

try:
    driver.get(url)

    while True:
        try:
            # 페이지 로드 대기 및 책 제목 수집
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ikc-biblio-title')))
            titles = driver.find_elements(By.CSS_SELECTOR, '.ikc-biblio-title')

            # 데이터 저장
            for title in titles:
                title_text = title.text.strip()
                if title_text not in book_titles:  # 중복 방지
                    book_titles.append(title_text)
                    print(title_text)

            # '다음' 버튼 확인
            next_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mat-paginator-navigation-next')))

            # '다음' 버튼이 비활성화된 경우 종료
            if "disabled" in next_button.get_attribute("class"):
                print("마지막 페이지입니다.")
                break

            # '다음' 버튼 클릭
            next_button.click()
            time.sleep(2)  # 페이지가 변경될 시간을 잠시 대기

        except Exception as e:
            logging.error(f"페이지 이동 중 오류 발생: {e}")
            print("페이지 이동 중 문제가 발생했습니다. 종료합니다.")
            break

except Exception as e:
    logging.error(f"전체 프로그램 오류: {e}")
    print("프로그램 실행 중 오류가 발생했습니다.")

finally:
    # 크롤링 결과를 무조건 CSV로 저장
    with open('book_titles.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Book Title"])  # 헤더 작성
        for title in book_titles:
            writer.writerow([title])  # 책 제목을 한 줄씩 저장

    print(f"총 {len(book_titles)}개의 데이터를 저장했습니다.")
    driver.quit()
