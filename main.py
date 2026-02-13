import requests
import os
import re

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
FEED_URL = "http://snusmic.com/feed/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # 마크다운이나 HTML 없이 일반 텍스트로 안전하게 전송
    params = {'chat_id': CHAT_ID, 'text': text}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(FEED_URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        content = response.text

        # 1. 정규표현식으로 <title>과 <link> 태그 안의 내용만 추출
        # XML 구조가 깨져 있어도 텍스트 패턴으로 찾아냅니다.
        titles = re.findall(r'<title>(.*?)</title>', content)
        links = re.findall(r'<link>(.*?)</link>', content)

        # 2. 첫 번째 타이틀은 보통 사이트 이름(SMIC)이므로 제외하고 수집
        post_list = []
        # titles[1:] 부터 시작하여 실제 게시글만 추출
        for t, l in zip(titles[1:], links[1:]):
            # CDATA 태그나 특수문자 정제
            clean_title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', t).strip()
            if len(clean_title) > 5:
                post_list.append(f"📍 {clean_title}\n🔗 {l}")
            
            if len(post_list) >= 5:
                break

        # 3. 결과 전송
        if post_list:
            result_text = "[SMIC 최신 게시글 5개]\n\n" + "\n\n".join(post_list)
            send_message(result_text)
        else:
            send_message("❌ 게시글 패턴을 찾지 못했습니다. 소스 확인이 필요합니다.")

    except Exception as e:
        send_message(f"⚠️ 실행 오류: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
