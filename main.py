import requests
from bs4 import BeautifulSoup
import os

# GitHub Secrets에서 가져오는 설정
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # HTML 모드를 사용하여 링크를 클릭 가능하게 만듭니다.
    params = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        # 1. 페이지 데이터 가져오기 (브라우저인 척 하기 위해 headers 추가)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 소스코드 분석 결과: Elementor의 포스트 위젯 구조를 타겟팅합니다.
        # 제목을 감싸는 가장 정확한 클래스는 'elementor-post__title'입니다.
        posts = soup.select('.elementor-post__title a')

        if posts:
            result_text = "<b>🔍 SMIC Research 최근 게시물 5개</b>\n\n"
            
            # 상위 5개만 추출
            for i, post in enumerate(posts[:5]):
                title = post.get_text().strip()
                link = post.get('href')
                result_text += f"{i+1}. <b>{title}</b>\n🔗 <a href='{link}'>게시글 읽기</a>\n\n"
            
            send_message(result_text)
        else:
            # 만약 위 셀렉터로 못 찾을 경우를 대비한 백업 (h3 태그)
            backup_posts = soup.select('h3 a')
            if backup_posts:
                result_text = "<b>⚠️ 구조 변경 감지 (백업 모드 작동)</b>\n\n"
                for i, post in enumerate(backup_posts[:5]):
                    title = post.get_text().strip()
                    link = post.get('href')
                    result_text += f"{i+1}. {title}\n🔗 {link}\n\n"
                send_message(result_text)
            else:
                send_message("❌ 게시글 구조를 찾을 수 없습니다. 사이트 점검이 필요합니다.")
                
    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
