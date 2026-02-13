import requests
import os
import re
import json

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
        html_content = response.text
        
        # 방식 1: 소스코드에 포함된 게시글 JSON 패턴을 직접 정규식으로 찾기
        # 'title' : '게시글제목', 'url' : '링크' 형태를 찾습니다.
        titles = re.findall(r'"title":"(.*?)"', html_content)
        urls = re.findall(r'"url":"(.*?)"', html_content)
        
        post_list = []
        for t, u in zip(titles, urls):
            # 유니코드 깨짐 복구 및 정제
            clean_title = t.encode().decode('unicode_escape').replace('\\/', '/')
            clean_url = u.replace('\\/', '/')
            
            # 메뉴 항목(Research, Members 등) 제외 및 중복 제거
            if len(clean_title) > 5 and 'snusmic.com' in clean_url:
                if clean_title not in [p['title'] for p in post_list]:
                    post_list.append({'title': clean_title, 'link': clean_url})
            
            if len(post_list) >= 5: break

        # 방식 2: 방식 1 실패 시, 단순히 텍스트 패턴으로 찾기
        if not post_list:
            # "Research - SMIC" 같이 페이지 제목 외에 실제 게시글스러운 패턴 탐색
            pattern = re.compile(r'<a[^>]+href="(http://snusmic\.com/[^"]+)"[^>]*>(.*?)</a>')
            matches = pattern.findall(html_content)
            for link, title in matches:
                title = re.sub('<[^<]+?>', '', title).strip() # 태그 제거
                if len(title) > 10:
                    post_list.append({'title': title, 'link': link})
                if len(post_list) >= 5: break

        # 결과 전송
        if post_list:
            result_text = "<b>🔍 SMIC Research 데이터 추출 성공</b>\n\n"
            for i, post in enumerate(post_list):
                result_text += f"{i+1}. <b>{post['title']}</b>\n🔗 {post['link']}\n\n"
            send_message(result_text)
        else:
            # 소스코드 일부를 로그로 출력 (디버깅용)
            print("Page Length:", len(html_content))
            send_message("❌ 데이터 추출에 실패했습니다. 사이트 보안이 강화되었거나 구조가 완전히 비표준입니다.")

    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
