import requests
import os
import re

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
URL = "http://snusmic.com/research/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        html_content = response.text

        # 1. 소스코드 내부에 숨겨진 JSON 데이터 패턴을 찾습니다.
        # "title":"글제목", "url":"링크" 형태를 정규식으로 낚아챕니다.
        # %20 같은 URL 인코딩 문자도 대응합니다.
        titles = re.findall(r'"title":"([^"]+)"', html_content)
        urls = re.findall(r'"url":"([^"]+)"', html_content)

        post_list = []
        for t, u in zip(titles, urls):
            # 필터링: 페이지 제목이거나 메뉴인 것 제외
            if "Research" in t or "SMIC" in t or "http" not in u:
                continue
            
            # 주소 내 역슬래시(\/) 제거 및 인코딩된 문자 정리
            clean_title = t.replace('\\/', '/').replace('%20', ' ')
            clean_url = u.replace('\\/', '/')
            
            if clean_title not in [p['title'] for p in post_list]:
                post_list.append({'title': clean_title, 'link': clean_url})
            
            if len(post_list) >= 5: break

        # 2. 만약 위 방식이 실패하면, article 태그 주변의 링크를 강제로 수집합니다.
        if not post_list:
            links = re.findall(r'<a[^>]+href="(http://snusmic\.com/[^"]+)"[^>]*>(.*?)</a>', html_content)
            for l, t in links:
                t = re.sub('<[^<]+?>', '', t).strip() # 태그 제거
                if len(t) > 10 and t not in [p['title'] for p in post_list]:
                    post_list.append({'title': t, 'link': l})
                if len(post_list) >= 5: break

        # 3. 결과 전송
        if post_list:
            result_text = "[SMIC 연구 게시글 탐색 성공]\n\n"
            for i, p in enumerate(post_list):
                result_text += f"{i+1}. {p['title']}\n🔗 {p['link']}\n\n"
            send_message(result_text)
        else:
            send_message("❌ 소스코드 내 데이터 패턴을 분석할 수 없습니다. 사이트가 로딩 방식을 완전히 바꿨을 수 있습니다.")

    except Exception as e:
        send_message(f"⚠️ 실행 오류: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
