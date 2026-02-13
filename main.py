import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        # 1. 페이지 데이터 가져오기
        headers = {'User-Agent': 'Mozilla/5.0'} # 차단 방지용 헤더
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 게시글 목록 찾기 
        # snusmic 사이트는 보통 'article' 태그나 'entry-title' 클래스를 사용합니다.
        posts = soup.select('h3.elementor-post__title a') # elementor 라이브러리 사용 시 흔한 구조
        
        if not posts:
            # 위 구조가 아닐 경우를 대비한 2차 시도 (일반적인 워드프레스 구조)
            posts = soup.select('.entry-title a')

        result_text = "🔍 *현재 홈페이지 최근 5개 게시물*\n\n"
        
        # 3. 상위 5개만 추출
        for i, post in enumerate(posts[:5]):
            title = post.text.strip()
            link = post.get('href')
            result_text += f"{i+1}. [{title}]({link})\n\n"
        
        if not posts:
            result_text = "❌ 게시물을 찾지 못했습니다. 사이트 구조를 다시 확인해야 합니다."
            
        send_message(result_text)
        
    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
