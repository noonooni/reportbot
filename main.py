import requests
import os
import xml.etree.ElementTree as ET

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
FEED_URL = "http://snusmic.com/feed/"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        # 1. RSS 피드 가져오기
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(FEED_URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 2. 내장 라이브러리(ElementTree)로 XML 분석
        root = ET.fromstring(response.text)
        
        # 워드프레스 RSS는 channel 태그 안에 item 태그들이 있습니다.
        items = root.findall('.//item')
        
        post_list = []
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            post_list.append({'title': title, 'link': link})
            
            if len(post_list) >= 5: # 최신순 5개
                break

        # 3. 결과 전송
        if post_list:
            result_text = "<b>✅ SMIC 최신 소식 (자동 업데이트)</b>\n\n"
            for i, p in enumerate(post_list):
                # 텔레그램 메시지 포맷팅
                result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 <a href='{p['link']}'>보고서 읽기</a>\n\n"
            send_message(result_text)
        else:
            send_message("❌ 새로운 게시글을 찾을 수 없습니다.")

    except Exception as e:
        # 에러 발생 시 상세 내용을 텔레그램으로 보냄
        send_message(f"⚠️ 시스템 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
