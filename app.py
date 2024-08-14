# import requests
# from bs4 import BeautifulSoup
#
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
# url = "https://playboard.co/chart/short/"
#
# data = requests.get(url, headers=headers)
#
# soup = BeautifulSoup(data.text, 'html.parser')
# links = soup.find_all('a', class_='title__label')  # class 이름을 정확히 대체하세요.
#
# urls = [link['href'] for link in links]
# print(len(urls))
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

import os
import time
import yt_dlp as youtube_dl

# ChromeDriver 경로 설정
service = Service('C:/Program Files/chromedriver-win64/chromedriver.exe')  # ChromeDriver의 경로를 설정하세요.
driver = webdriver.Chrome(service=service)

driver.get("https://playboard.co/chart/short/")

# 인피니트 스크롤 수행
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 페이지 소스 가져오기
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 원하는 데이터 추출
links = soup.find_all('a', class_='title__label')  # 정확한 클래스 이름을 확인해야 할 수도 있습니다.
urls = ["https://youtube.com/shorts/" + link['href'].split("/")[2] for link in links]

print(urls)

driver.quit()

resource_folder = os.path.join(os.getcwd(), 'resources')
if not os.path.exists(resource_folder):
    os.makedirs(resource_folder)

# youtube-dl 옵션 설정
ydl_opts = {
    'outtmpl': os.path.join(resource_folder, '%(id)s.%(ext)s'),  # 파일명을 URL의 고유 식별자로 설정
}

# 동영상 다운로드
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(urls)
