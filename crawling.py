from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time

driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # headless 모드 (창을 띄우지 않음)

url = "https://oasis.ssu.ac.kr/search/ebook-collections/"
driver.get(url)
time.sleep(10)

# 도서 정보를 찾아 변수에 저장 (By.CLASS_NAME 방식)
#book_box = driver.find_element(By.CLASS_NAME, 'ikc-biblios ng-star-inserted')

#book_titles = driver.find_elements(By.CLASS_NAME, "ikc-biblios ng-star-inserted")

#for i in book_titles:
    #title = i.text
    #print(title)




# 책 제목을 저장할 리스트
book_titles = []

# 페이지네이션을 처리하면서 책 제목을 추출
while True:
    try:
        # 책 제목 추출 (각 페이지가 로드된 후)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ikc-biblio-title')))
        titles = driver.find_elements(By.CSS_SELECTOR, '.ikc-biblio-title')
        
        # 제목들을 리스트에 추가
        for title in titles:
            book_titles.append(title.text.strip()) 
            print(title.text.strip())
            

        # 다음 페이지로 이동
        next_button = driver.find_element(By.CSS_SELECTOR, '.mat-paginator-navigation-next')  # 페이지네이션에서 '다음' 버튼의 클래스명
        if "disabled" in next_button.get_attribute("class"):
            print("마지막 페이지입니다.")
            break
        next_button.click()
        time.sleep(5)  # 페이지가 로드되도록 잠시 대기

    except Exception as e:
        print(f"오류 발생: {e}")
        break

# 브라우저 종료
driver.quit()
