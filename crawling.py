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

url = "https://oasis.ssu.ac.kr/search/ebook-collections?offset=0&max=100"
book_titles = []

try:
    driver.get(url)

    while True:
        try:
            # 책 제목 수집
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ikc-biblio-title')))
            titles = driver.find_elements(By.CSS_SELECTOR, '.ikc-biblio-title')

            for title in titles:
                title_text = title.text.strip()
                if title_text not in book_titles:
                    book_titles.append(title_text)
                    print(title_text)

            # '다음' 버튼 확인 및 클릭 (재시도 로직 포함)
            retry_count = 0
            success = False

            while retry_count < 3:
                try:
                    next_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mat-paginator-navigation-next')))

                    # 마지막 페이지인 경우 종료
                    if "disabled" in next_button.get_attribute("class"):
                        print("마지막 페이지입니다.")
                        raise StopIteration  # 루프 종료

                    # '다음' 버튼 클릭
                    next_button.click()
                    success = True  # 클릭 성공 시 상태 변경
                    time.sleep(2)  # 페이지 로딩 대기
                    break  # 클릭 성공 시 탈출

                except Exception as e:
                    retry_count += 1
                    logging.warning(f"다음 버튼 클릭 실패. 재시도 중... ({retry_count}/3) - {e}")
                    time.sleep(1)

            if not success:
                print("다음 버튼 클릭 재시도 실패. 현재 페이지를 건너뜁니다.")
                continue  # 현재 페이지를 건너뛰고 다음으로 진행

        except StopIteration:
            break

        except Exception as e:
            logging.error(f"페이지 이동 중 오류 발생: {e}")
            print("페이지 이동 중 문제가 발생했습니다. 건너뜁니다.")
            continue

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
