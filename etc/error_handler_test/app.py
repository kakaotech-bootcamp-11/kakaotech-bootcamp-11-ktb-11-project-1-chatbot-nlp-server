import openai
import json
import logging
import warnings
import os
from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS
from dotenv import load_dotenv
from error_handler import register_error_handlers
from openai import OpenAIError
from chatgpt_api import cls_chatgpt, stream_chatgpt
from generate_openaiapi_error import OpenAIErrorSimulator
from werkzeug.exceptions import BadRequest


# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# 플라스크 앱 정의
app = Flask(__name__)
CORS(app)
register_error_handlers(app) # flask error handler 등록 


"""
# API 키 로드하기
print("환경변수 로드 ")
load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY2") # API 키 설
"""

@app.route("/error_test", methods=['get'])
def error_test():
    #params = request.get_json()  # 공통 함수 호출
    #user_input = params['content']
    """system_prompt = "you are a helpful assistant "
    user_prompt = "한국 전래 동화 3개만 알려줘"
    result = cls_chatgpt(system_prompt, user_prompt)
    return jsonify({"result": result})"""

    load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정


    simulator = OpenAIErrorSimulator(api_key=OPENAI_API_KEY)

    # 특정 에러를 발생시키고 싶다면 -  OpenAIErrorSimulator의 메소드 중 1개를 호출 
    simulator.trigger_bad_request_error()
    return None


if __name__ == '__main__':
    print("app.run 시작")
    app.run(port=5001,debug=True)
