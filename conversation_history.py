# from konlpy.tag import Okt
from pymongo import MongoClient
from datetime import datetime
import pytz
from mongo_client import get_mongo_client
import os

# KoNLPy를 사용하여 간단한 키워드 기반 태그 추출
# okt = Okt()

"""def extract_tags(text):
    # 명사만 추출
    tags = okt.nouns(text)
    return tags"""

"""# 환경 변수에서 MongoDB 연결 URL 가져오기
mongo_uri = os.getenv('MONGO_URI')
# MongoDB 연결 설정
try:
    client = MongoClient(mongo_uri)
    db = client['chatbot_db']
    collection = db['chat_history']
    print("MongoDB 연결 성공")
except Exception as e:
    print(f"MongoDB 연결 실패: {str(e)}")"""


# # MongoDB 연결 설정
# client = MongoClient(mongo_uri)
# db = client['chatbot_db']  # 데이터베이스 이름 설정
# collection = db['chat_history']  # 콜렉션 이름 설정


# collection

def save_conversation(collection, user_id, chat_id, role, text):
    # 현재 시간을 한국 시간으로 설정
    korea_tz = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(korea_tz).strftime('%Y-%m-%d %H:%M:%S')

    # client, db, collection = get_mongo_client()

    # 대화 내용 저장
    conversation = {
        "user_id": user_id,
        "chat_id": chat_id,
        "timestamp": current_time,
        "role": role,
        "text": text,
        # "tags": tags  # 태그 저장
    }
    collection.insert_one(conversation)


def history(collection, user_id, chat_id, limit=4):  # 대화 기록 조회

    # 대화 기록 불러오기
    query = {
        "user_id": user_id,
        "chat_id": chat_id
    }
    conversations = collection.find(query).sort("timestamp", -1).limit(limit)
    print("history(): conversations:", conversations)

    # 내림차순으로 가져온 후, 이를 다시 뒤집어 최신순으로 반환
    return list(conversations)[::-1]


# 예시 사용
if __name__ == "__main__":
    # 대화 저장
    save_conversation("user123", "thread456", "user", "안녕하세요, 오늘 날씨는 어떤가요?")
    save_conversation("user123", "thread456", "assistant", "안녕하세요! 오늘 날씨는 맑고 따뜻합니다.")

    # 최근 대화 5개 가져오기
    # 최근 대화 5개 가져오기
    recent_conversations = history("user123", "thread456", limit=5)
    for conversation in recent_conversations:
        print(f"대화 시간: {conversation['timestamp']}")
        print(f"발화 주체: {conversation['role']}")
        print(f"대화 텍스트: {conversation['text']}")
        # print(f"태그: {conversation['tags']}\n")