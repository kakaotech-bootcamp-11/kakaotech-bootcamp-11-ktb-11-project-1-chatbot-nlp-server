import os
from pymongo import MongoClient

# 환경 변수에서 MongoDB 연결 URL 가져오기
mongo_uri = os.getenv('MONGO_URI')

# MongoDB 클라이언트 생성 함수
def get_mongo_client():
    try:
        client = MongoClient(mongo_uri)
        db = client['chatbot_db']
        collection = db['chat_history']
        print("MongoDB 연결 성공")
        return client, db, collection
    except Exception as e:
        print(f"MongoDB 연결 실패: {str(e)}")
        return None, None, None