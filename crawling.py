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
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")

# 웹드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(15)

base_url = "https://oasis.ssu.ac.kr/search/ebook-collections?offset={}&max=100"
offset = 0  # 시작 offset
book_titles = []

try:
    while True:
        # 현재 offset을 URL에 적용해서 페이지 이동
        url = base_url.format(offset)
        print(f"현재 페이지: {url}")
        driver.get(url)

        try:
            # 책 제목 수집
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ikc-biblio-title')))
            title_elements = driver.find_elements(By.CSS_SELECTOR, '.ikc-biblio-title')

            for element in title_elements:
                title_id = element.get_attribute('id')
                if title_id:
                    # id를 기반으로 책 제목 가져오기
                    title = driver.find_element(By.ID, title_id).text.strip()
                    if title not in book_titles:  # 중복 방지
                        book_titles.append(title)
                        print(title)

            # 다음 페이지로 이동 (offset 증가)
            offset += 100  # 한 번에 100개의 데이터를 가져왔으므로 offset 증가

            # '다음' 페이지에 데이터가 없는지 검사
            if not title_elements:
                print("마지막 페이지입니다.")
                break

        except Exception as e:
            logging.error(f"페이지 이동 중 오류 발생: {e}")
            print("페이지 이동 중 문제가 발생했습니다. 다음 페이지로 건너뜁니다.")
            offset += 100  # 오류가 발생해도 offset을 증가시켜 다음 페이지로 이동

except Exception as e:
    logging.error(f"전체 프로그램 오류: {e}")
    print("프로그램 실행 중 오류가 발생했습니다.")

finally:
    # 크롤링 결과를 CSV로 저장
    with open('book_titles.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Book Title"])
        for title in book_titles:
            writer.writerow([title])
    print(f"총 {len(book_titles)}개의 데이터를 저장했습니다.")
    driver.quit()
