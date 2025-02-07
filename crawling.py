from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv

# Chrome 드라이버 자동 설치 및 서비스 설정
options = Options()
options.add_argument("--start-maximized")  # 창 최대화
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL로 이동
#AI
#url = 'https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=job.latest_order&years=0&years=3&selected=1025&selected=1022&selected=1634&selected=1024&locations=all'
#백엔드
#url = 'https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=job.latest_order&years=0&years=3&selected=873&selected=895&selected=893&selected=1027&selected=795&locations=all'
#프론트
url = 'https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=job.latest_order&years=0&years=3&selected=669&selected=939&locations=all'
driver.get(url)

# 페이지 로딩 대기
time.sleep(5)

# 추가 공고 로딩을 위해 휠 내려서 더 많은 공고를 로딩
# 몇 번이나 스크롤을 내릴지 설정 (예: 5번)
for _ in range(1):  # 원하는 만큼 반복
    # 휠 내리기 (스크롤 내리기)
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(3)  # 페이지가 업데이트 될 때까지 잠시 대기

# 공고 리스트의 링크 추출
links = driver.find_elements(By.CLASS_NAME, 'JobCard_JobCard__Tb7pI')

job_links = []
for link in links:
    try:
        job_link = link.find_element(By.TAG_NAME, 'a').get_attribute('href')
        job_links.append(job_link)
    except Exception as e:
        print(f"링크 추출 오류: {e}")
print(len(job_links), "개 추출 완료")

# 상세 정보 추출
job_details = []
for job_link in job_links:
    try:
        driver.get(job_link)
        time.sleep(5)  # 페이지 로딩 기다리기

        # 회사명과 공고명 추출
        try:
            company_name = driver.find_element(By.CLASS_NAME, 'JobHeader_JobHeader__Tools__Company__Link__zAvYv').text
        except:
            company_name = '정보 없음'

        try:
            job_title = driver.find_element(By.CLASS_NAME, 'wds-jtr30u').text
        except:
            job_title = '정보 없음'

        # '더 보기' 버튼 찾기
        try:
            button = driver.find_element(By.CSS_SELECTOR, '.Button_Button__root__m1NGq.Button_Button__outlined__0HnEd.Button_Button__outlinedAssistive__JKDyz.Button_Button__outlinedSizeLarge__A_H8o.Button_Button__fullWidth__zAnDP')
            
            # 🔹 **JavaScript로 강제 클릭**
            driver.execute_script("arguments[0].click();", button)
            time.sleep(5)  # 페이지 업데이트 기다리기
        except Exception as e:
            print(f"버튼 클릭 오류: {e}")

        # 상세 정보 추출
        details = driver.find_elements(By.CLASS_NAME, 'wds-wcfcu3')

        position_details = details[0].text if len(details) > 0 else '정보 없음'
        key_responsibilities = details[1].text if len(details) > 1 else '정보 없음'
        salary_requirements = details[2].text if len(details) > 2 else '정보 없음'
        preferred_qualifications = details[3].text if len(details) > 3 else '정보 없음'
        benefits = details[4].text if len(details) > 4 else '정보 없음'
        recruitment_process = details[5].text if len(details) > 5 else '정보 없음'

        job_details.append([job_link, company_name, job_title, position_details, key_responsibilities, salary_requirements, preferred_qualifications, benefits, recruitment_process])

    except Exception as e:
        print(f"공고 처리 오류: {e}")

# CSV 파일 저장
with open('job_details_front.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['공고 링크', '회사명', '공고명', '직무 상세', '주요 업무', '자격요건', '우대 사항', '복리후생', '채용 절차'])
    writer.writerows(job_details)

# 크롬 드라이버 종료
driver.quit()
