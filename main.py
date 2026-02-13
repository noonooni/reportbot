import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 소스코드 분석 결과: 포트폴리오 아이템의 제목 태그를 직접 찾습니다.
        # 주신 mem.txt 소스에 있는 정확한 클래스명입니다.
        posts = soup.find_all('div', class_='elementor-portfolio-item__title')
        
        # 2. 만약 위 방식이 안될 경우 부모 요소를 통해 찾습니다.
        if not posts:
            posts = soup.select('.elementor-portfolio-item__content')

        post_list = []
        for post in posts:
            # 텍스트 추출
            title = post.get_text().strip()
            
            # 링크 추출: 보통 제목 주변의 <a> 태그에 있습니다.
            # 부모나 자식 요소 중 <a> 태그를 탐색합니다.
            link_tag = post.find_parent('a') or post.find('a') or post.find_previous('a')
            
            if link_tag:
                link = link_tag.get('href', '')
                if title and link.startswith('http'):
                    post_list.append({'title': title, 'link': link})
            
            if len(post_list) >= 5: break

        # 3. 결과 전송
        if post_list:
            result_text = "<b>🔍 SMIC Research 최신 게시물</b>\n\n"
            for i, p in enumerate(post_list):
                result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 <a href='{p['link']}'>연구 보고서 읽기</a>\n\n"
            send_message(result_text)
        else:
            # 마지막 수단: 텍스트가 있는 모든 링크 중 research가 포함된 것
            all_links = soup.select('a[href*="/research/"]')
            for a in all_links:
                t = a.get_text().strip()
                l = a.get('href', '')
                if len(t) > 5 and t not in ['RESEARCH', 'Research']:
                    post_list.append({'title': t, 'link': l})
                if len(post_list) >= 5: break
            
            if post_list:
                result_text = "<b>🔍 SMIC 게시물 (대체 탐색)</b>\n\n"
                for i, p in enumerate(post_list):
                    result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 {p['link']}\n\n"
                send_message(result_text)
            else:
                send_message("❌ 최종 탐색 실패. 사이트 로딩 방식이 특이합니다.")

    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
