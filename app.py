import logging
import os
from flask import Flask,  jsonify, Response, stream_with_context
from flask_cors import CORS
from document_retriever import my_retriever
from error_handler import register_error_handlers
from openai import OpenAIError
from werkzeug.exceptions import BadRequest
from conversation_history import save_conversation, history
from pymongo import MongoClient
from utils import get_request_data, topic_classification, handle_weather_topic, handle_trans_topic, handle_else_topic, text_chatgpt
from mongo_client import get_mongo_client
import json
from difflib import SequenceMatcher




# 플라스크 앱 정의
app = Flask(__name__)
CORS(app)
register_error_handlers(app) # flask error handler 등록

# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 환경 변수에서 MongoDB 연결 URL 가져오기
# mongo_uri = os.getenv('MONGO_URI')
client, db, collection = get_mongo_client()



# 환경 변수에서 API 키와 PDF 경로를 로드
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TMAP_API_KEY = os.getenv('TMAP_API_KEY')
KAKAO_MAP_API_KEY = os.getenv('KAKAO_MAP_API_KEY1')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
LOCATION1 = os.getenv('LOCATION1')

# LLM 변수 정의
STREAM_TOKEN_SIZE = 1 # 스트림 토큰 단위 default 125
MODEL_VERSION = "gpt-4o-mini" # "gpt-3.5-turbo"
MAX_TOKENS_OUTPUT = 500

# 검색할 문서 로드
file_path = os.getenv('PDF_PATH', 'data/ktb_data_09.md')
try:
    retriever, faiss_db = my_retriever(file_path)
except OpenAIError as e:
    raise e
print("=======검색기 로드 끝========")

# 모델의 응답을 스트리밍하기 위한 제너레이터 함수
def generate_response_stream(user_id, chat_id, user_input):
    my_history = history(collection, user_id, chat_id)
    for h in my_history:
        print("히스토리:\n")
        print(f"{h['role']}:{h['text']}")
        print("\n")
    # retriever의 스트리밍 응답을 처리 (pipeline.stream 사용)
    save_conversation(collection, user_id, chat_id, "user", user_input) #사용자 질문
    answer_text = ''
    for chunk in retriever.stream({"question":user_input, "chat_history":my_history}):  # stream을 사용하여 스트리밍 처리
        print("chunk:", chunk)
        answer_text += chunk
        chunk_json = json.dumps({"text": chunk}, ensure_ascii=False)
        yield f"data: {chunk_json}\n\n" # "data": ... \n\n 을
        # print(chunk)
    # 질문 & 응답 저장

    #time.sleep(0.1)
    save_conversation(collection, user_id, chat_id, "system", answer_text) # 답변
    print("최종 답변:", answer_text)
    
def is_related_to_previous_conversation(user_input, previous_conversation):
    # 문장 유사도를 기반으로 연관성 판단
    similarity_threshold = 0.3  # 유사도 임계값 (0~1)
    similarity = SequenceMatcher(None, user_input, previous_conversation).ratio()
    
    print(f"유사도: {similarity}")  # 유사도를 출력하여 확인할 수 있음
    
    return similarity > similarity_threshold


@app.route("/nlp-api/conv", methods=['POST'])
def llm():
    params = get_request_data() # request body 를 가져옴
    user_input, user_id, chat_id = params['content'], params['user_id'], params['chat_id']
    print("user_input, user_id, chat_id:", user_input, user_id, chat_id)

    #save_conversation(collection, user_id, chat_id, "user", user_input)

    response_generator = generate_response_stream(user_id, chat_id, user_input)
    return Response(stream_with_context(response_generator), mimetype='text/event-stream', )
    #return Response(stream_message(response_generator), mimetype='application/json')

@app.route("/nlp-api/title", methods=['POST'])
def make_title(): # 대화의 타이틀 생성
    params = get_request_data(title=True)
    user_input = params['content']
    system_prompt = """넌 대화 타이틀을 만드는 역할이야. 챗봇에서 사용자의 첫 번째 메시지를 기반으로 해당 대화의 제목을 요약해줘."""
    title = text_chatgpt(system_prompt, user_input)

    if title is None:
        return jsonify({"error": "죄송해요. 챗 지피티가 제목을 제대로 가져오지 못했어요."})
    title = title.strip('"') # 앞뒤의 큰 따옴표 제거
    return jsonify({"title": title})

'''
@app.route("/nlp-api/test", methods=['POST'])
def test(): # whole text 만든 다음, 청크 단위로 나눠 스트림 형식으로 전달
    params = get_request_data() # request body 를 가져옴
    user_input, user_id, chat_id = params['content'], params['user_id'], params['chat_id']
    system_prompt = """사용자의 질문에 친절하게 대답해줘."""
    result = text_chatgpt(system_prompt, user_input)
    print("result(whole text):", result)
    response_generator = generate_response_stream(user_id, chat_id, user_input)
    return Response(response_generator, mimetype='text/event-stream')
@app.route("/nlp-api/test/stream", methods=['POST'])
def stream_output(): # chatGPT API 에서 실시간으로 청크 단위로 답변을 받아옴.
    #user_input, user_id, chat_id = get_request_data()  # 공통
    params = get_request_data() # request body 를 가져옴
    user_input, user_id, chat_id = params['content'], params['user_id'], params['chat_id']
    # 답변 가져오기
    response_generator = generate_response_stream(user_id, chat_id, user_input)
    return Response(response_generator, mimetype='text/event-stream')
# test function for error handling
@app.route("/nlp-api/error_handling", methods=['POST'])
def error_handle(): # 대화의 타이틀 생성 #(params)
    params = get_request_data() # request body 를 가져옴
    if not params : # json = {}
        raise BadRequest("No request body")
    elif 'content' not in params or not params['content'].strip(): # json = {'msg': "..."} or json = {'content': ""}
        raise BadRequest("No content field in request body or value for content is empty")
    return jsonify({"result": f"no error:{params['content']}"})'''



if __name__ == '__main__':
    print("app starts running")
    app.run(port=5001, debug=True)