import spacy
from pymongo import MongoClient
from datetime import datetime
import pytz

# spaCy를 사용하여 간단한 키워드 기반 태그 추출
nlp = spacy.load("en_core_web_sm")

def extract_tags(text):
    doc = nlp(text)
    tags = [chunk.text for chunk in doc.noun_chunks]
    return tags

# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']  # 데이터베이스 이름 설정
collection = db['chat_history']  # 콜렉션 이름 설정

def save_conversation(user_id, thread_id, role, text):
    # 현재 시간을 한국 시간으로 설정
    korea_tz = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(korea_tz).strftime('%Y-%m-%d %H:%M:%S')

    # 대화 태그 추출
    tags = extract_tags(text)

    # 대화 내용 저장
    conversation = {
        "user_id": user_id,
        "thread_id": thread_id,
        "timestamp": current_time,
        "role": role,
        "text": text,
        "tags": tags  # 태그 저장
    }
    collection.insert_one(conversation)

def history(user_id, thread_id, limit=5):
    # 대화 기록 불러오기
    query = {
        "user_id": user_id,
        "thread_id": thread_id
    }
    conversations = collection.find(query).sort("timestamp", -1).limit(limit)

    # 내림차순으로 가져온 후, 이를 다시 뒤집어 최신순으로 반환
    return list(conversations)[::-1]

# 예시 사용
save_conversation("user123", "thread456", "user", "Hello, how are you?")
save_conversation("user123", "thread456", "system", "I'm fine, thank you! Let's talk about the weather.")

# 최근 대화 5개 가져오기
recent_conversations = history("user123", "thread456", limit=5)
for conversation in recent_conversations:
    print(f"대화 시간: {conversation['timestamp']}")
    print(f"발화 주체: {conversation['role']}")
    print(f"대화 텍스트: {conversation['text']}")
    print(f"태그: {conversation['tags']}\n")
