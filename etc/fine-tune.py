## 주어진 텍스트 가지고 fine-tuning 하는 방식을 선택

import os 
import openai
from dotenv import load_dotenv


# .env 환경 변수 설정 하기 
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 파인 튜닝 모델 학습 
def train_model(input_data): 
    # 클라이언트 정의 
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    client = openai.OpenAI(api_key=open_api_key) # 클라이언트 객체 생성
    train_file = client.files.create( # 클라이언트에 학습 데이터 업로드 
        #file = open("./train_data/train_v1.jsonl", 'rb'),
        file = open(input_data, 'rb'),
        purpose="fine-tune"
    )

    file_id = train_file.id
    # 미세 조정된 모델 만들기 
    fine_tune_model = client.fine_tuning.jobs.create(
        training_file= file_id, #"file-1st", 
        model="gpt-3.5-turbo"
    )

    print(f"Fine-tune job created with ID: {fine_tune_model.id}")

    

def model_list(): # 파인 튜닝된 모델 리스트를 생성함. 
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    client = openai.OpenAI(api_key=open_api_key) # 클라이언트 객체 생성
    print(client.fine_tuning.jobs.list(limit=10))


if __name__ == "__main__":
    input_path = "./train_data/train_v1.jsonl"
    model_name = "test1"
    train_model(input_data = input_path)
    model_list()


    

