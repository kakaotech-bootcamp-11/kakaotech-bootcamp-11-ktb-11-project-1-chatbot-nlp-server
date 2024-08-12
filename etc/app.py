from flask import Flask, request, jsonify
import os 
import openai
from flask_cors import CORS
app = Flask(__name__)

def train_model(train_file, model_name): 
    # 클라이언트 정의 
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    client = openai.OpenAI(api_key=open_api_key) # 클라이언트 객체 생성
    client.files.create( # 클라이언트에 학습 데이터 업로드 
        #file = open("./train_data/train_v1.jsonl", 'rb'),
        file = open(train_file, 'rb'),
        purpose="fine-tune"
    )
    # 미세 조정된 모델 만들기 
    client.fine_tuning.jobs.create(
    training_file= model_name, #"file-1st", 
    model="gpt-3.5-turbo"
)

# 모델 활용하기 
@app.route('/', methods = ['GET'])
def use_model(model_name, sample_user_input):
    # 클라이언트 정의 
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    client = openai.OpenAI(api_key=open_api_key) # 클라이언트 객체 생성

    # 파인튜닝한 모델 가져오기 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
         {"role": "user", "content": f"출석 기준은 어떻게 돼?"},
        ],
        temperature=0,
        max_tokens=100
    )

    text_output =  response.choices[0].message.content
    return text_output
    

    # CHAT GPT API 객체 생성 -  답변을 받아옴 
    

    
    #@app.route('/', methods = ['GET'])



if __name__ == '__main__':
    app.run(port=5000,debug=True )