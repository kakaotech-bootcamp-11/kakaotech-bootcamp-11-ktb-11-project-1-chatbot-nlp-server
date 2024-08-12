import asyncio 
from dotenv import load_dotenv
import logging
import os 
import openai 
from openai import AsyncOpenAI



MAX_TOKENS_OUTPUT = 200
MODEL_VERSION = "gpt-4o" # "gpt-3.5-turbo"	
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# PDF에서 자료를 찾을 수 없을 때, chatGPT 에서 생성한 정답을 리턴하도록 한다. 
async def fetch_response(client, prompt):
    response_text = ""
    # CHAT GPT API 객체 생성
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "한국어로 대답해줘"},
            {"role": "user", "content": prompt}
            ],
        stream=True,
    )
    async for chunk in response:
        response_text += chunk.choices[0].delta.content or ""
        # print(f"Prompt: {prompt}\nResponse: {response_text}***\n")  # 디버깅을 위한 출력
    return response_text

async def main():
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

    prompts = ["대한민국의 수도는 어디야?", "오늘 서울 날씨는 어때?", "농담 하나 던져줘"]

    tasks = [fetch_response(client, prompt) for prompt in prompts]
    
    responses = await asyncio.gather(*tasks)
    
    return responses

if __name__ == "__main__":
    result_list = asyncio.run(main())
    print(result_list)  # 리스트 출력


load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정



