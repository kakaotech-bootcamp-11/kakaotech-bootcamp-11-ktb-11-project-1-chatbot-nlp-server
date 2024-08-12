# == flask GET POST 기능 테스트 하기 위한 함수 =====
from flask import Flask, request, jsonify
import os 
import openai
from flask_cors import CORS


app = Flask(__name__)


# get: 데이터를 그냥 가져옴 
# post: 데이터를 가져와서 어떤 작업을 수행해야할 떄(e.g. 내용 변경/삭제)

@app.route("/", methods = ["GET", 'POST']) 
def func1():
    if request.method == "GET":
        return "GET request"

@app.route("/post", methods=['POST'])
def func2():
    params = request.get_json()
    if not params:
        return jsonify({"error": "No input data provided"}), 400

    msg = {
        "name": params['name'],
        "text": params['text'],
        "roomname": params['roomname']
    }
    return jsonify(msg)

@app.route("/llm1", methods=['POST'])
def func2():
    params = request.get_json()
    if not params:
        return jsonify({"error": "No input data provided"}), 400

    input_msg = params['msg']
    

    # 챗 지피티 클라이언트 정의 
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    client = openai.OpenAI(api_key=open_api_key)

    # CHAT GPT API 객체 생성 -  답변을 받아옴 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role":"system", "content": "You are a helpful assistant, and you will kindly answer questions about the Kakao Bootcamp in the future. 사용자들은 한국어로 질문할 거고, 너도 한국어로 대답해야돼"}, 
            {"role": "user", "content": input_msg},
        ],
        temperature=0, # 출력의 다양성 조절 (0~1), 높을 수록 창의적인 대답
        #top_p =       # 출력의 다양성 조절 (0~1), 확률의 누적 분포 기반
        max_tokens=100, # 최대 출력 토큰 개수 
        n = 1,            # 생성 답변 개수 
        stop= None      #
    )

    text_output =  response.choices[0].message.content
    return text_output

if __name__ == '__main__':
    app.run(port=5001,debug=True )