import openai
import json
import logging
import warnings
import os
from flask import Flask, request, jsonify, Response, abort, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from pdf_retriever import pdf_retriever
from get_weather import get_weather_info
from find_routes_v2 import get_route_description
from error_handler import register_error_handlers
from openai import OpenAIError


from werkzeug.exceptions import BadRequest

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


# API 키 로드하기
print("환경변수 로드 ")
load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정
TMAP_API_KEY = os.environ.get("TMAP_API_KEY")
KAKAO_MAP_API_KEY = os.environ.get("KAKAO_MAP_API_KEY1")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# LLM 변수 정의 
STREAM_TOKEN_SIZE = 30
MODEL_VERSION = "gpt-4o-mini" # "gpt-3.5-turbo"  
MAX_TOKENS_OUTPUT = 500


# pdf 로드 

pdf_path = './data/ktb_data_08.pdf'  # PDF 경로를 지정해주기 - 추후에 모든 pdf 읽도록  바꾸도록 지정하기 
#retriever = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)
try:
    retriever = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)
except OpenAIError as e:
    raise e
print("PDF 검색기 로드 끝")


"""def split_text_into_tokens(text, max_tokens=STREAM_TOKEN_SIZE): # max_tokens : 스트림 1번에 보낼  토큰 단위를 지정 
    # 텍스트를 공백을 기준으로 토큰화
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield ' '.join(words[i:i+max_tokens])

def stream_message(text, max_tokens=STREAM_TOKEN_SIZE, delay=1): # 데이터가 청크 단위로 스트리밍 된다. 
    
    for chunk in split_text_into_tokens(text, max_tokens):
        yield f"data: {chunk}\n\n"  # 이 부분을 메시지 전송 로직으로 대체할 수 있습니다.

"""

def stream_message(text, max_tokens=STREAM_TOKEN_SIZE, delay=1): # 데이터가 청크 단위로 스트리밍 된다. 
    words = text.split()
    for i in range(0, len(words), max_tokens):
        chunk = ' '.join(words[i:i+max_tokens])
        yield f"data: {chunk}\n\n"
    """for chunk in split_text_into_tokens(text, max_tokens):
        yield f"data: {chunk}\n\n"  # 이 부분을 메시지 전송 로직으로 대체할 수 있습니다."""



def stream_chatgpt(system_prompt, user_prompt):
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

def handle_weather_topic(user_input):
    weather_info = get_weather_info()
    system_prompt = (f"You are a helpful assistant, and you will kindly answer questions about current weather. "
              f"한국어로 대답해야해. 현재 날씨 정보는 다음과 같아. {weather_info}, "
              "이 날씨 정보를 다 출력할 필요는 없고, 주어진 질문인 '{user_input}'에 필요한 답만 해줘 ")
    result = stream_chatgpt(system_prompt, user_input)
    return result
    """if result is not None: return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')"""

def handle_trans_topic(user_input):
    dict_string = extract_arrv_dest(user_input)
    from_to_dict = json.loads(dict_string)
    result_txt = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    system_prompt = f"너는 출발지에서 목적지까지 경로를 안내하는 역할이고, 한국어로 대답해야해."\
              f"사용자는 경로에 대해 요약된 텍스트를 줄거야. 너는 그걸 자연스럽게 만들어주면 돼. "\
              f"출발지는 ```{from_to_dict['from']}```이고 목적지는 ```{from_to_dict['to']}```임.  "
    user_prompt = f"다음을 자연스럽게 다시 말해줘:\n```{result_txt}``` "
    return stream_chatgpt(user_prompt) 
    """if dict_string:
        from_to_dict = json.loads(dict_string)
        result = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    else:
        result = "죄송해요. 다시 한 번 질문해주세요." #error msg
        logging.error("extract_arrv_dest is None")

    return Response(stream_message(result), content_type='text/plain')"""

def handle_else_topic(user_input):
    system_prompt = ("You are a helpful assistant."
              "사용자들은 한국어로 질문할 거고, 너도 한국어로 대답해야돼")
    result = stream_chatgpt(system_prompt, user_input)
    return result
    """if result is not None: 
        return result # 비동기식 response 형식 
    else:
        result = "죄송해요. 챗 지피티가 답변을 가져오지 못했어요."
        return Response(stream_message(result), content_type='text/plain')"""

def validate_request_data():
    params = request.get_json()
    if not params:  # JSON 데이터가 없는 경우
        raise BadRequest("No request body")
    elif 'content' not in params or not params['content'].strip():  # 'content' 필드가 없거나 값이 비어 있는 경우
        raise BadRequest("No content field in request body or value for content is empty")
    return params

@app.route("/conv", methods=['POST'])
def llm():
    params = validate_request_data()  # 공통 함수 호출
    user_input = params['content']

    # 동기식으로 RAG 기법 적용한 QA 체인 생성
    response = retriever(user_input)
    print('RAG response:', response)
    if response['result'] and not any(phrase in response['result'] for phrase in ["죄송", "모르겠습니다", "알 수 없습니다", "확인할 수 없습니다", "없습니다."])  : # 만약 
        logging.info( f"RAG - user input: {user_input}")
        print("logging: RAG 답변 ")
        #return Response(stream_message(response['result']), content_type='text-event') # here
        return Response(stream_message(response['result']), mimetype='text/event-stream')
    elif not response['result']: #  # RAG를 수행하지 못했을 때 - 예외 처리 추가하기 
        logging.error("error" "RAG를 요청 했으나 결과가 없음. 400")
        raise BadRequest("No response from RAG") # 추후 수정


    # 날씨, 교통, 그외 주제인지 분류하기 
    topic = topic_classification(user_input)
    print("topic:", topic)
    if topic == "WEATHER":
        return handle_weather_topic(user_input)
    elif topic == "TRANS":
        return handle_trans_topic(user_input)
    elif topic == "ELSE":
        return handle_else_topic(user_input)
    """else:
        logging.error("chat gpt failed to classify: result is None")
        return jsonify({"error": "Topic classification failed"}), 500"""


@app.route("/test", methods=['POST'])
def test(): # whole text 만든 다음, 청크 단위로 나눠 스트림 형식으로 전달 
    params = validate_request_data()
    user_input = params['content'] 
    system_prompt = """사용자의 질문에 친절하게 대답해줘."""
    result = text_chatgpt(system_prompt, user_input)
    print("result(whole text):", result)
    return Response(stream_with_context(stream_message(result)), mimetype='text/event-stream') # 'text/plain'
    #return Response(stream_message(result), mimetype='text/event-stream') # 'text/plain'

#@app.route("/test/stream", methods=['POST'])
@app.route("/test/stream", methods=['POST'])
def stream_output(): # chatGPT API 에서 실시간으로 청크 단위로 답변을 받아옴. 
    params = validate_request_data()
    # 답변 가져오기 
    user_input = params['content']
    user_input = "뮤지컬에 대해서 알려줘"
    system_prompt = "You are a helpful assistant"
    result = stream_chatgpt(system_prompt, user_input) # 
    return result 

# test function for error handling
@app.route("/error_handling", methods=['POST'])
def error_handle(): # 대화의 타이틀 생성 #(params)
    params = request.get_json()
    if not params : # json = {}
        raise BadRequest("No request body")
    elif 'content' not in params or not params['content'].strip(): # json = {'msg': "..."} or json = {'content': ""}
        raise BadRequest("No content field in request body or value for content is empty")
        #abort(500, description="No request body ---- ")
    return jsonify({"result": f"no error:{params['content']}"})



# TEST 
def iter_file_lines(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line

@app.route('/textfile')
def stream_text_file():
    return Response(iter_file_lines('test.txt'), mimetype='text/event-stream')

if __name__ == '__main__':
    print("app.run 시작")
    print("PDF 검색기 로드 시작")
    
    app.run(port=5001,debug=True)
