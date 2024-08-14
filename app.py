import openai
import json
import logging
import warnings
import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from pdf_retriever import pdf_retriever
from get_weather import get_weather_info
from find_routes_v2 import get_route_description
from openai import AsyncOpenAI

# 플라스크 앱 정의
app = Flask(__name__)
CORS(app)

# 모든 경고를 무시
warnings.filterwarnings("ignore")

# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# flask 앱 정의 
app = Flask(__name__) 

# API 키 로드하기
print("환경변수 로드 ")
load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정
TMAP_API_KEY = os.environ.get("TMAP_API_KEY")
KAKAO_MAP_API_KEY = os.environ.get("KAKAO_MAP_API_KEY1")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")


# LLM 변수 정의 
MAX_TOKENS_OUTPUT = 200
STREAM_TOKEN_SIZE = 30
MODEL_VERSION = "gpt-4o" # "gpt-3.5-turbo"  
print("PDF 검색기 로드 시작")
pdf_path = './data/ktb_data_07_3.pdf'  # PDF 경로를 지정해주기 - 추후에 모든 pdf 읽도록  바꾸도록 지정하기 
retriever = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)
print("PDF 검색기 로드 끝")

def split_text_into_tokens(text, max_tokens=STREAM_TOKEN_SIZE):
    # 텍스트를 공백을 기준으로 토큰화
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield ' '.join(words[i:i+max_tokens])

def stream_message(text, max_tokens=STREAM_TOKEN_SIZE, delay=1): # 데이터가 청크 단위로 스트리밍 된다. 
    for chunk in split_text_into_tokens(text, max_tokens):
        yield chunk  # 이 부분을 메시지 전송 로직으로 대체할 수 있습니다.


# 동기식 chatGPT 함수
def chatgpt(system_prompt, user_prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
            max_tokens= MAX_TOKENS_OUTPUT, # 최대 출력 토큰 개수 
            n = 1         # 생성 답변 개수 
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error while calling chatGPT API function call: {str(e)}")
        return None


def topic_classification(user_input):
    system_prompt = """
            You are a classifier. Your task is to analyze '{user_input}'.
        - If '{user_input}' is a question about the asking weather, return 'WEATHER'.
        - If '{user_input}' is a question about public transportation routes involving a specific origin and destination, return 'TRANS'.
        - If '{user_input}' does not match either of the above cases, return 'ELSE'.
        """
    return chatgpt(system_prompt, user_input )

def extract_arrv_dest(user_input): #user input 에서 출발지와 도착지 출력  
    system_prompt = """
            Your task is to identify the departure and destination from the user's input. 
            Follow these guidelines: 
            1. If either the departure or destination is ambiguous or unclear, mark it as unknown. 
            2. If the input refers to the user's current location, mark it as current.
            3. If the input suggests the user's home location, mark it as home. 
            4. Please return a dictionary formatted like this : {"from":departure, "to":destination}
            """
    return chatgpt(system_prompt =system_prompt, user_prompt= user_input )

def handle_weather_topic(user_input):
    weather_info = get_weather_info()
    system_prompt = (f"You are a helpful assistant, and you will kindly answer questions about current weather. "
              f"한국어로 대답해야해. 현재 날씨 정보는 다음과 같아. {weather_info}, "
              "이 날씨 정보를 다 출력할 필요는 없고, 주어진 질문인 '{user_input}'에 필요한 답만 해줘 ")
    result = chatgpt(system_prompt, user_input)
    if result is not None: return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')


# 동기식으로 TRANS 주제 처리
def handle_trans_topic(user_input):
    dict_string = extract_arrv_dest(user_input)
    result = ""
    if dict_string:
        from_to_dict = json.loads(dict_string)
        result = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    else:
        result = "죄송해요. 다시 한 번 질문해주세요." #error msg
        logging.error("extract_arrv_dest is None")

    return Response(stream_message(result), content_type='text/plain')

def handle_else_topic(user_input):
    system_prompt = ("You are a helpful assistant."
              "사용자들은 한국어로 질문할 거고, 너도 한국어로 대답해야돼")
    result = chatgpt(system_prompt, user_input)
    if result is not None: 
        return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')

@app.route("/conv", methods=['POST'])
def llm():
    params = request.get_json()
    if not params:
        return jsonify({"error": "No input data provided"}), 400
    user_input = params['content']

    # 동기식으로 RAG 기법 적용한 QA 체인 생성
    response = retriever(user_input)
    print('RAG response:', response)
    if response['result'] and not any(phrase in response['result'] for phrase in ["죄송", "모르겠습니다", "알 수 없습니다", "확인할 수 없습니다", "없습니다."])  : # 만약 
        logging.info( f"RAG - user input: {user_input}")
        print("logging: RAG 답변 ")
        return Response(stream_message(response['result']), content_type='text/plain')
    
    elif not response['result']:
        # RAG를 수행하지 못했을 때 - 에러 메시지 
        logging.error("error" "RAG를 요청 했으나 결과가 없음. 400")
        return jsonify({"error": "No response from RAG"}), 400 # 로깅으로 바꾸기


    # 날씨, 교통, 그외 주제인지 분류하기 
    topic = topic_classification(user_input)
    print("topic:", topic)
    if topic == "WEATHER":
        return handle_weather_topic(user_input)
    elif topic == "TRANS":
        return handle_trans_topic(user_input)
    elif topic == "ELSE":
        return handle_else_topic(user_input)
    else:
        logging.error("chat gpt failed to classify: result is None")
        return jsonify({"error": "Topic classification failed"}), 500


@app.route("/title", methods=['POST'])
def make_title(): # 대화의 타이틀 생성
    params = request.get_json()
    if not params: # 입력이 없을 경우 에러 메시지 출력 
        logging.error("error - No valid request")
        return jsonify({"error": "No valid request"})
    # 답변 가져오기 
    user_input = params['content'] 
    system_prompt = """넌 대화 타이틀을 만드는 역할이야. 챗봇에서 사용자의 첫 번째 메시지를 기반으로 해당 대화의 제목을 요약해줘."""
    title = chatgpt(system_prompt, user_input)
    
    if title is None:
        return jsonify({"error": "죄송해요. 챗 지피티가 제목을 제대로 가져오지 못했어요."})
    title = title.strip('"') # 앞뒤의 큰 따옴표 제거
    return jsonify({"title": title})


@app.route("/test", methods=['POST'])
def stream_output(): # 대화의 타이틀 생성
    params = request.get_json()
    if not params: # 입력이 없을 경우 에러 메시지 출력 
        logging.error("error - No valid request")
        return jsonify({"error": "No valid request"})
    # 답변 가져오기 
    user_input = params['content'] 
    system_prompt = "You are a helpful assistant"
    result =  chatgpt(system_prompt, user_input)
    return Response(stream_message(result), content_type='text/plain') # STREAM_TOKEN_SIZE 조절을 통해서, stream 청크 사이즈를 조절할 수 있음. 



if __name__ == '__main__':
    print("app.run 시작")
    app.run(port=5001,debug=True)
