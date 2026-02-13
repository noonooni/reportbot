import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # 마크다운 대신 일반 텍스트로 우선 전송 (에러 방지)
    params = {'chat_id': CHAT_ID, 'text': text}
    requests.get(api_url, params=params)

def fetch_test():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 시도 1: 모든 <a> 태그 중 제목일 가능성이 높은 것들 수집
        # 보통 연구 게시판은 글 제목에 링크가 걸려 있습니다.
        links = soup.find_all('a')
        
        post_list = []
        for a in links:
            href = a.get('href', '')
            title = a.text.strip()
            
            # /research/ 하위 게시글이거나 특정 패턴을 가진 링크 필터링
            # 보통 게시글 링크는 숫자가 포함되거나 연구 제목이 길게 들어갑니다.
            if len(title) > 10 and ('/research/' in href or 'portfolio' in href or 'p=' in href):
                if title not in [p['title'] for p in post_list]: # 중복 제거
                    post_list.append({'title': title, 'link': href})

        if post_list:
            result_text = "🔍 [탐색 성공] 최근 게시물 목록:\n\n"
            for i, post in enumerate(post_list[:5]):
                result_text += f"{i+1}. {post['title']}\n링크: {post['link']}\n\n"
            send_message(result_text)
        else:
            # 실패 시 로그 기록용
            print("--- HTML 구조 요약 (에러 분석용) ---")
            print(soup.prettify()[:1000]) # 앞부분 1000자만 출력
            send_message("❌ 여전히 게시물을 찾지 못했습니다. 로그 확인이 필요합니다.")
            
    except Exception as e:
        send_message(f"⚠️ 실행 중 오류: {str(e)}")

if __name__ == "__main__":
    fetch_test()
