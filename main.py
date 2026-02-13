import requests
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 실제 데이터가 오가는 통로 (API 주소)
# 이 주소는 서버에서 게시글 데이터를 직접 받아오는 경로입니다.
API_URL = "http://snusmic.com/wp-admin/admin-ajax.php"

def send_message(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    requests.get(api_url, params=params)

def fetch_top_5():
    try:
        # 서버에 게시글 목록을 달라고 보내는 요청 데이터
        data = {
            'action': 'elementor_pro_forms_send_form', # 또는 엘리멘터 쿼리 액션
            'action': 'elementor_v2_posts_load_more', 
            # 일반적인 접근이 막힐 경우를 대비해 쿼리 파라미터를 구성하거나 
            # 공개된 다른 API 경로를 시도합니다.
        }
        
        # 하지만 가장 확실한 방법은 RSS 피드를 사용하는 것입니다.
        # 워드프레스 사이트인 snusmic.com은 표준 RSS를 지원합니다.
        feed_url = "http://snusmic.com/feed/"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(feed_url, headers=headers, timeout=30)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'xml') # XML 파서 사용
        
        items = soup.find_all('item')
        
        post_list = []
        for item in items:
            title = item.title.text
            link = item.link.text
            # 연구글 카테고리나 특정 키워드 필터링 (선택 사항)
            post_list.append({'title': title, 'link': link})
            if len(post_list) >= 5: break

        if post_list:
            result_text = "<b>✅ SMIC 최신 연구 리스트 (RSS 추출)</b>\n\n"
            for i, p in enumerate(post_list):
                result_text += f"{i+1}. <b>{p['title']}</b>\n🔗 <a href='{p['link']}'>보고서 읽기</a>\n\n"
            send_message(result_text)
        else:
            send_message("❌ RSS 피드에서도 글을 찾을 수 없습니다.")

    except Exception as e:
        send_message(f"⚠️ 오류 발생: {str(e)}")

if __name__ == "__main__":
    fetch_top_5()
