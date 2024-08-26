import openai
import json
import logging
import warnings
import os
from flask import Flask, request, jsonify, Response, abort
from dotenv import load_dotenv
from openai import OpenAIError


# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY2") # API 키 설정
MAX_TOKENS_OUTPUT = 600
MODEL_VERSION = "gpt-4o" # "gpt-3.5-turbo"  

def stream_chatgpt(system_prompt, user_prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL_VERSION,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
            max_tokens= MAX_TOKENS_OUTPUT, # 최대 출력 토큰 개수 
            n = 1,         # 생성 답변 개수,
            stream=True
        )
        def event_stream(): #stream generator
            print("response", response)
            for chunk in response:
                text = chunk.choices[0].delta.get('content')
                if len(text):
                    yield text
                    print(text)
        return Response(event_stream(), mimetype='text/event-stream')
    except Exception as e:
        print(f"Error while calling chatGPT API function call: {str(e)}")
        logging.error(f"Error while calling chatGPT API function call: {str(e)}")
        abort(500)
        # return None
    
# 동기식 chatGPT 함수
def cls_chatgpt(system_prompt, user_prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL_VERSION,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
            max_tokens= MAX_TOKENS_OUTPUT, # 최대 출력 토큰 개수 
            n = 1,         # 생성 답변 개수,
            stream=True
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error while calling chatGPT API function call: {str(e)}")
        logging.error(f"Error while calling chatGPT API function call: {str(e)}")
        raise e # OpenAIError
    

"""def test():
    system_prompt = "you are a helpful assistant "
    user_prompt = "한국 전래 동화 3개만 알려줘"
    stream_chatgpt(system_prompt, user_prompt)

test()
"""
    

