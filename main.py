import requests
from bs4 import BeautifulSoup
import os
import re

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
        
        # 1. 모든 게시글 박스(article)를 먼저 찾습니다.
        # 소스 분석 결과 elementor-post 클래스가 각 게시글의 단위입니다.
        articles = soup.find_all('article', class_=re.compile(r'elementor-post'))
        
        post_list = []
        
        for article in articles:
            # a) 제목 찾기: h3 내부의 a 태그 혹은 article 내부의 첫 번째 유의미한 a 태그
            title_tag = article.find('h3') or article.find('a')
            if not title_tag: continue
            
            title = title_tag.get_text().strip()
            link = ""
            
            # b) 링크 찾기
            link_tag = article.find('a')
            if link_tag:
                link = link_tag.get('href', '')
            
            # c) 불필요한 공백이나 메뉴 방지 (제목이 4자 이상인 것만)
            if len(title) > 3 and link.startswith('http'):
                if title not in [p['title'] for p in post_list]:
                    post_list.append({'title': title, 'link': link})
            
            if len(post_list) >= 5: break

        # 2. 결과 전송
        if post_list:
            result_text = "<b>🔍 SMIC Research 최신 게시물</b>\n\n"
            for i, post in enumerate(post_list):
                result_text += f"{i+1}. <b>{post['title']}</b>\n🔗 <a href='{post['link']}'>게시글로 이동</a>\n\n"
            send_message(result_text)
        else:
            # 3. 최후의 수단: 소스코드 내 모든 링크 중 'portfolio'나 'research' 단어가 들어간 제목 있는 링크 추출
            all_links = soup.find_all('a')
            for a in all_links:
                t = a.get_text().strip()
                l = a.get('href', '')
                if len(t) > 10 and ('/research/' in l or '/portfolio/' in l):
                    if t not in [p['title'] for p in post_list]:
                        post_list.append({'title': t, 'link': l})
                if len(post_list) >= 5: break
            
            if post_list:
                result_text = "<b>🔍 SMIC 게시물 (대체 탐색 성공)</b>\n\n"
                for i, post in enumerate(post_list):
                    result_text += f"{i+1}. <b>{post['title']}</b>\n🔗 {post['link']}\n\n"
                send_message(result_text)
            else:
                send_message("❌ 게시글 추출 실패. 사이트가 콘텐츠를 숨기고 있습니다.")

    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
