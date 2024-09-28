import openai
import logging
from flask import request, Response
# from get_weather import get_weather_info
# from find_routes_v2 import get_route_description
from conversation_history import save_conversation, history
from openai import OpenAIError
from werkzeug.exceptions import BadRequest
import time
import os

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

def stream_message(text):  # 데이터가 한 글자 단위로 스트리밍 된다.
    for char in text:
        yield f"data: {char}\n\n"

def stream_chatgpt(system_prompt, user_prompt, user_id, chat_id):
    print("stream_chatgpt()")
    first = time.time()
    print(f"first: {first}")
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
    second = time.time()
    print(f"second: {second}")
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
                print("- text:", text, "\n")
                if text:
                    result_txt += text
                    yield f"data: {text}\n\n"

            print("답변 결과:\n", result_txt)
            # 답변 결과 DB 에 저장
            save_conversation(user_id, chat_id, "system", result_txt)
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

""" def handle_weather_topic(user_input, user_id, chat_id):
    weather_info = get_weather_info()
    system_prompt = (f"You are a helpful assistant, and you will kindly answer questions about current weather. "
              f"한국어로 대답해야해. 현재 날씨 정보는 다음과 같아. {weather_info}, "
              "이 날씨 정보를 다 출력할 필요는 없고, 주어진 질문인 '{user_input}'에 필요한 답만 해줘 ")
    result = stream_chatgpt(system_prompt, user_input, user_id, chat_id)
    return result"""

""" def handle_trans_topic(user_input, user_id, chat_id):
    dict_string = extract_arrv_dest(user_input)
    from_to_dict = json.loads(dict_string)
    result_txt = get_route_description(from_to_dict, TMAP_API_KEY, KAKAO_MAP_API_KEY)
    system_prompt = f"너는 출발지에서 목적지까지 경로를 안내하는 역할이고, 한국어로 대답해야해."\
              f"사용자는 경로에 대해 요약된 텍스트를 줄거야. 너는 그걸 자연스럽게 만들어주면 돼. "\
              f"출발지는 ```{from_to_dict['from']}```이고 목적지는 ```{from_to_dict['to']}```임.  "
    user_prompt = f"다음을 자연스럽게 다시 말해줘:\n```{result_txt}``` "
    return stream_chatgpt(system_prompt, user_prompt, user_id, chat_id)"""

def handle_else_topic(user_input, user_id, chat_id):
    system_prompt = ("You are a helpful assistant."
              "사용자들은 한국어로 질문할 거고, 너도 한국어로 대답해야돼")
    result = stream_chatgpt(system_prompt, user_input, user_id, chat_id)
    return result

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