from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

import os
import time
import yt_dlp as youtube_dl
import subprocess

audio_path = "assets/TickTick.mp3"  # 음원 파일 경로
ffmpeg_path = 'C:/Program Files/ffmpeg/bin/ffmpeg.exe'
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
    'format': 'bestvideo+bestaudio/best',  # 최고 화질과 음질을
    'merge_output_format': 'mp4',
    'outtmpl': os.path.join(resource_folder, '%(id)s.%(ext)s'),  # 파일명을 URL의 고유 식별자로 설정
    'ffmpeg_location': ffmpeg_path
}

file_urls = []

# 동영상 다운로드 및 파일 경로 수집
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    for url in urls:
        info_dict = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info_dict)
        file_urls.append(video_file)

print(file_urls)

# audio.mp3 파일이 실제로 존재하는지 확인
if not os.path.exists(audio_path):
    raise FileNotFoundError(f"Audio file not found: {audio_path}")

# 각 파일에 대해 ffmpeg 명령어 실행
for video_path in file_urls:
    # 출력 파일명 설정 (final_ 붙이기)
    output_path = os.path.join(os.path.dirname(video_path), f"final_{os.path.basename(video_path)}")

    # ffmpeg 명령어 설정 (볼륨 조절 추가)
    command = [
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[a]",
        "-map", "0:v",  # 비디오 트랙
        "-map", "[a]",  # 믹스된 오디오 트랙
        "-c:v", "copy",  # 비디오 복사
        "-c:a", "aac",  # 오디오 코덱 설정
        "-shortest",  # 짧은 길이에 맞춤
        output_path
    ]

    # 명령어 실행
    subprocess.run(command, check=True)

print("모든 동영상에 음원이 추가되었습니다.")