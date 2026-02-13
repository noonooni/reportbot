import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text}
    res = requests.get(api_url, params=params)
    print(f"전송 결과: {res.status_code}, {res.text}") # 로그 확인용

def check_posts():
    # 테스트를 위해 무조건 메시지 전송!
    send_message("🤖 봇이 정상적으로 연결되었습니다! 이제 사이트를 감시합니다.")
    
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 실제 사이트 제목 태그 추출 (사이트마다 다름)
        # snusmic.com은 보통 <h3> 이나 특정 클래스를 사용함
        post = soup.select_one('h3') # 임시로 h3 태그 확인
        if post:
            current_title = post.text.strip()
            print(f"가져온 제목: {current_title}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_posts()
