import json
from bson import ObjectId
from pymongo import MongoClient

# MongoDB에 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']
collection = db['chat_history']

# 모든 데이터를 가져오기
data = list(collection.find())

# ObjectId를 문자열로 변환하는 함수
def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# 데이터를 변환
data = convert_objectid(data)

# JSON 파일로 저장
with open('output.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)