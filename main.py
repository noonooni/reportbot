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
        
        # 1. 'Portfolio' 위젯의 각 아이템 덩어리를 모두 가져옵니다.
        items = soup.select('.elementor-portfolio-item')
        
        post_list = []
        for item in items:
            # 제목 추출: 제목을 담고 있는 클래스를 정밀 타겟팅합니다.
            title_tag = item.select_one('.elementor-portfolio-item__title')
            # 링크 추출: 아이템 자체 혹은 내부의 a 태그를 찾습니다.
            link_tag = item.select_one('a')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag.get('href', '')
                
                # 중복 방지 및 유효성 검사
                if title and link.startswith('http') and title not in [p['title'] for p in post_list]:
                    post_list.append({'title': title, 'link': link})
            
            if len(post_list) >= 5: break

        # 2. 결과 전송
        if post_list:
            result_text = "<b>🔍 SMIC Research 최신 리스트</b>\n\n"
            for i, p in enumerate(post_list):
                result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 <a href='{p['link']}'>보고서 보기</a>\n\n"
            send_message(result_text)
        else:
            # 백업 모드: 클래스명이 아닌 텍스트 패턴으로 강제 탐색
            backup_links = soup.find_all('a', href=True)
            for a in backup_links:
                href = a['href']
                text = a.get_text(strip=True)
                # 연구글일 확률이 높은 링크 패턴 필터링
                if '/research/' in href and len(text) > 10:
                    if text not in [p['title'] for p in post_list]:
                        post_list.append({'title': text, 'link': href})
                if len(post_list) >= 5: break
            
            if post_list:
                result_text = "<b>🔍 SMIC Research (패턴 탐색 성공)</b>\n\n"
                for i, p in enumerate(post_list):
                    result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 {p['link']}\n\n"
                send_message(result_text)
            else:
                send_message("❌ 모든 시도가 실패했습니다. 사이트 로딩 구조가 일반적인 크롤링을 허용하지 않습니다.")

    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
