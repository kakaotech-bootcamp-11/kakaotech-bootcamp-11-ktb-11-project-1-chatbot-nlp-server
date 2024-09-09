import openai
import json
import logging
import warnings
import os
from flask import Flask, request, jsonify, Response, abort, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from document_retriever import my_retriever
from get_weather import get_weather_info
from find_routes_v2 import get_route_description
from error_handler import register_error_handlers
from openai import OpenAIError
from werkzeug.exceptions import BadRequest
from conversation_history import save_conversation, history
#from konlpy.tag import Okt
from pymongo import MongoClient
from datetime import datetime
import pytz

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


# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']  # 데이터베이스 이름 설정
collection = db['chat_history']  # 콜렉션 이름 설정


# API 키 로드하기
print("환경변수 로드 ")
load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정
TMAP_API_KEY = os.environ.get("TMAP_API_KEY")
KAKAO_MAP_API_KEY = os.environ.get("KAKAO_MAP_API_KEY1")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# LLM 변수 정의 
STREAM_TOKEN_SIZE = 1 # 스트림 토큰 단위 default 125
MODEL_VERSION = "gpt-4o-mini" # "gpt-3.5-turbo"  
MAX_TOKENS_OUTPUT = 500


# 검색할 문서 로드 
file_path = 'data/ktb_data_09.md'# PDF 경로를 지정해주기 - 추후에 모든 pdf 읽도록  바꾸도록 지정하기 
try:
    retriever = my_retriever(file_path)
except OpenAIError as e:
    raise e
print("검색기 로드 끝")


"""def stream_message(text, max_tokens=STREAM_TOKEN_SIZE, delay=1): # 데이터가 청크 단위로 스트리밍 된다. 
    words = text.split()
    for i in range(0, len(words), max_tokens):
        chunk = ' '.join(words[i:i+max_tokens])
        yield f"data: {chunk}\n\n"""
def stream_message(text):  # 데이터가 1글자 단위로 스트리밍 된다.
    for char in text:
        print(char)
        yield f"data: {char}\n\n"


def stream_chatgpt(system_prompt, user_prompt, user_id, chat_id):
    print("stream_chatgpt()")
    # 기존 N개 데이터 히스토리 가져오기 
    messages = [{"role": "system", "content": system_prompt + "\n 정보를 일반 텍스트로 작성해 주세요. 굵게 표시하지 말고, 특수 형식 없이 일반 텍스트로만 작성해 주세요."},
                {"role": "user", "content": user_prompt} ]
    if user_id is not None and chat_id is not None:
        conv_history = history(user_id, chat_id, limit=2)
        for conv in conv_history:
            role = conv.get('role') # 'user' or 'system'
            content = conv.get('text')
            messages.append({"role": role, "content": content})

    print('history:', messages)
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL_VERSION,
            messages= messages,
            temperature=0.0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
            max_tokens= MAX_TOKENS_OUTPUT, # 최대 출력 토큰 개수 
            n = 1,         # 생성 답변 개수,
            stream=True
        )
        def event_stream(): #stream generator
            result_txt = ''
            for chunk in response:
                text = chunk.choices[0].delta.content
                #print("chunk.choices[0]", chunk.choices[0])
                #print("text:", text, "\n")
                if text:
                    result_txt += text
                    yield f"data: {text}\n\n"
            print("답변 결과:\n", result_txt)
            # 답변 결과 DB 에 저장
            save_conversation(user_id, chat_id, "system", result_txt)
            """ // 토큰 단위로 주는 코드 // 폐기
            result_txt = ''
            buffer_txt = ''
            word_count = 0
            
            for chunk in response:
                text = chunk.choices[0].delta.content
                print("text:", text)
                if text:
                    result_txt += text
                    buffer_txt += text
                    word_count += len(text.split())  # 새로운 텍스트의 단어 수 계산
                    #print("buffered_text: ",buffer_txt)
                    #print("current word cnt:", len(text.split()))

                    # 30단어를 넘으면 버퍼 내용 전달
                    if word_count >= STREAM_TOKEN_SIZE:
                        print("# STREAM_TOKEN_SIZE단어를 넘으면 버퍼 내용 전달")
                        print("전달된 텍스트: ", buffer_txt)
                        yield f"data: {buffer_txt}\n\n"
                        buffer_txt = ''  # 버퍼 초기화
                        word_count = 0   # 단어 수 초기화

            # 남은 텍스트가 있으면 출력
            if buffer_txt:
                print("# 남은 텍스트가 있으면 출력")
                print("전달된 텍스트: ", buffer_txt)
                yield f"data: {buffer_txt}\n\n
            
            print("답변 결과:\n", result_txt)
            # 답변 결과 DB에 저장
            save_conversation(user_id, chat_id, "system", result_txt)
            
            
            """

            

            
        return Response(event_stream(), mimetype='text/event-stream')
    except OpenAIError as e:
        logging.error(f"Error while calling chatGPT API function call: {str(e)}")
        raise e # OpenAIError
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise e # OpenAIError
    
def text_chatgpt(system_prompt, user_prompt): # text 형식으로 리턴
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL_VERSION,
            messages=[
                {"role": "system", "content": system_prompt + "\n 정보를 일반 텍스트로 작성해 주세요. 굵게 표시하지 말고, 특수 형식 없이 일반 텍스트로만 작성해 주세요."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
            max_tokens= MAX_TOKENS_OUTPUT, # 최대 출력 토큰 개수 
            n = 1,         # 생성 답변 개수,
            stream=False
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        logging.error(f"Error while calling chatGPT API function call: {str(e)}")
        raise e # OpenAIError
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise e # OpenAIError
    

def topic_classification(user_input):
    system_prompt = """
            You are a classifier. Your task is to analyze '{user_input}'.
        - If '{user_input}' is a question about the asking weather, return 'WEATHER'.
        - If '{user_input}' is a question about public transportation routes involving a specific origin and destination, return 'TRANS'.
        - If '{user_input}' does not match either of the above cases, return 'ELSE'.
        """
    return text_chatgpt(system_prompt, user_input)

def extract_arrv_dest(user_input): #user input 에서 출발지와 도착지 출력  
    system_prompt = """
            Your task is to identify the departure and destination from the user's input. 
            Follow these guidelines: 
            1. If either the departure or destination is ambiguous or unclear, mark it as unknown. 
            2. If the input refers to the user's current location, mark it as current.
            3. If the input suggests the user's home location, mark it as home. 
            4. Please return a dictionary formatted like this : {"from":departure, "to":destination}
            """
    return text_chatgpt(system_prompt =system_prompt, user_prompt= user_input )

def handle_weather_topic(user_input, user_id, chat_id):
    weather_info = get_weather_info()
    system_prompt = (f"You are a helpful assistant, and you will kindly answer questions about current weather. "
              f"한국어로 대답해야해. 현재 날씨 정보는 다음과 같아. {weather_info}, "
              "이 날씨 정보를 다 출력할 필요는 없고, 주어진 질문인 '{user_input}'에 필요한 답만 해줘 ")
    result = stream_chatgpt(system_prompt, user_input, user_id, chat_id)
    return result
    """if result is not None: return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')"""

def handle_trans_topic(user_input, user_id, chat_id):
    dict_string = extract_arrv_dest(user_input)
    from_to_dict = json.loads(dict_string)
    result_txt = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    system_prompt = f"너는 출발지에서 목적지까지 경로를 안내하는 역할이고, 한국어로 대답해야해."\
              f"사용자는 경로에 대해 요약된 텍스트를 줄거야. 너는 그걸 자연스럽게 만들어주면 돼. "\
              f"출발지는 ```{from_to_dict['from']}```이고 목적지는 ```{from_to_dict['to']}```임.  "
    user_prompt = f"다음을 자연스럽게 다시 말해줘:\n```{result_txt}``` "
    return stream_chatgpt(system_prompt, user_prompt, user_id, chat_id) 
    """if dict_string:
        from_to_dict = json.loads(dict_string)
        result = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    else:
        result = "죄송해요. 다시 한 번 질문해주세요." #error msg
        logging.error("extract_arrv_dest is None")

    return Response(stream_message(result), content_type='text/plain')"""

def handle_else_topic(user_input, user_id, chat_id):
    system_prompt = ("You are a helpful assistant."
              "사용자들은 한국어로 질문할 거고, 너도 한국어로 대답해야돼")
    result = stream_chatgpt(system_prompt, user_input, user_id, chat_id)
    return result
    """if result is not None: 
        return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')"""

def get_request_data(title=None):
    params = request.get_json()
    print("params:", params)
    if not params:  # JSON 데이터가 없는 경우
        raise BadRequest("No request body")
    # 변수가 3개 : content, user_id, chat_id
    if 'content' not in params or not isinstance(params['content'], str) or not params['content'].strip() :  # 'content' 필드가 없거나 값이 비어 있는 경우
        raise BadRequest("No content field in request body, empty value or invalid value")
    if title is None: # title은 user_id, chat_id 가 필요 없음 
        if 'user_id' not in params or not params['user_id'] or not isinstance(params['user_id'], int):  
            raise BadRequest("No user_id field in request body, empty value or invalid value")
        if 'chat_id' not in params or not params['chat_id'] or not isinstance(params['chat_id'], int): 
            raise BadRequest("No chat_id field in request body, empty value or invalid value")
    
    #content, user_id, chat_id = params['content'], params['user_id'], params['chat_id']
    #return content, user_id, chat_id 
    return params

@app.route("/conv", methods=['POST'])
def llm():
    #user_input, user_id, chat_id = get_request_data()  # 공통 함수 호출
    params = get_request_data() # request body 를 가져옴
    user_input, user_id, chat_id = params['content'], params['user_id'], params['chat_id']
    print("user_input, user_id, chat_id:", user_input, user_id, chat_id)

    save_conversation(user_id, chat_id, "user", user_input)
    print("save_conversation")



    # 동기식으로 RAG 기법 적용한 QA 체인 생성
    response = retriever.invoke(user_input)
    #print("response type:", type(response))
    print('RAG response:', response)
    #if response['result'] and not any(phrase in response['result'] for phrase in ["죄송", "모르겠습니다", "알 수 없습니다", "확인할 수 없습니다", "없습니다"])  : # 만약 
    if response and "해당 정보는 제공된 문서들에 포함되어 있지 않습니다." not in response:
        logging.info( f"RAG - user input: {user_input}")
        print("response:", response)
        # 답변 결과 DB 에 저장
        save_conversation(user_input, chat_id, "system", response)
        print("logging: RAG 답변")
        return Response(stream_message(response), mimetype='text/event-stream')
    elif not response: #  # RAG를 수행하지 못했을 때 - 예외 처리 추가하기 
        logging.error("error" "RAG를 요청 했으나 결과가 없음. 400")
        raise BadRequest("No response from RAG") # 추후 수정


    # 날씨, 교통, 그외 주제인지 분류하기 
    topic = topic_classification(user_input)
    print("topic:", topic)
    if topic == "WEATHER":
        return handle_weather_topic(user_input,user_id, chat_id)
    elif topic == "TRANS":
        return handle_trans_topic(user_input, user_id, chat_id)
    elif topic == "ELSE":
        return handle_else_topic(user_input, user_id, chat_id)
    """else:
        logging.error("chat gpt failed to classify: result is None")
        return jsonify({"error": "Topic classification failed"}), 500"""


@app.route("/test", methods=['POST'])
def test(): # whole text 만든 다음, 청크 단위로 나눠 스트림 형식으로 전달 
    params = get_request_data(title=True) # request body 를 가져옴
    user_input = params['content']
    system_prompt = """사용자의 질문에 친절하게 대답해줘."""
    result = text_chatgpt(system_prompt, user_input)
    print("result(whole text):", result)
    return Response(stream_with_context(stream_message(result)), mimetype='text/event-stream') # 'text/plain'
    #return Response(stream_message(result), mimetype='text/event-stream') # 'text/plain'

#@app.route("/test/stream", methods=['POST'])
@app.route("/test/stream", methods=['POST'])
def stream_output(): # chatGPT API 에서 실시간으로 청크 단위로 답변을 받아옴. 
    #user_input, user_id, chat_id = get_request_data()  # 공통
    params = get_request_data(title=True) # request body 를 가져옴
    user_input, user_id, chat_id  = params['content'], params['user_id'], params['chat_id']

    # 답변 가져오기 
    system_prompt = "You are a helpful assistant"
    result = stream_chatgpt(system_prompt, user_input, user_id, chat_id) # 
    return result 

# test function for error handling
@app.route("/error_handling", methods=['POST'])
def error_handle(): # 대화의 타이틀 생성 #(params)
    params = get_request_data() # request body 를 가져옴
    if not params : # json = {}
        raise BadRequest("No request body")
    elif 'content' not in params or not params['content'].strip(): # json = {'msg': "..."} or json = {'content': ""}
        raise BadRequest("No content field in request body or value for content is empty")
    return jsonify({"result": f"no error:{params['content']}"})

@app.route("/title", methods=['POST'])
def make_title(): # 대화의 타이틀 생성
    params = get_request_data(title=True)
    user_input = params['content'] 
    system_prompt = """넌 대화 타이틀을 만드는 역할이야. 챗봇에서 사용자의 첫 번째 메시지를 기반으로 해당 대화의 제목을 요약해줘."""
    title = text_chatgpt(system_prompt, user_input)

    if title is None:
        return jsonify({"error": "죄송해요. 챗 지피티가 제목을 제대로 가져오지 못했어요."})
    title = title.strip('"') # 앞뒤의 큰 따옴표 제거
    return jsonify({"title": title})


if __name__ == '__main__':
    print("app starts running")
    app.run(port=5001,debug=True)
    
    
