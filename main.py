import requests
from bs4 import BeautifulSoup
import os

# 환경 변수에서 토큰 가져오기
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text}
    requests.get(api_url, params=params)

def check_posts():
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # snusmic 사이트의 게시글 제목 태그 (분석 결과에 따라 수정 필요)
        post = soup.select_one('.list-item-title') 
        if not post:
            return
            
        current_title = post.text.strip()
        
        # 이전에 저장된 제목 확인
        last_title = ""
        if os.path.exists("last_post.txt"):
            with open("last_post.txt", "r", encoding="utf-8") as f:
                last_title = f.read().strip()
        
        if current_title != last_title:
            with open("last_post.txt", "w", encoding="utf-8") as f:
                f.write(current_title)
            send_message(f"📢 새로운 연구 게시글이 올라왔습니다!\n제목: {current_title}")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_posts()
