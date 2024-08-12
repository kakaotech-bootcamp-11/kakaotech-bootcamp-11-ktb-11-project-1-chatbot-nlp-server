from bs4 import BeautifulSoup
import logging
import requests
import os 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from collections import Counter
from langchain.document_loaders import PyMuPDFLoader  # PDF 파일을 읽어오는 데 사용
from langchain.embeddings import OpenAIEmbeddings  # OpenAI의 임베딩 기능을 사용
from langchain.text_splitter import SpacyTextSplitter  # 텍스트를 적절한 크기로 나누기
from langchain.vectorstores import Chroma  # 벡터 데이터를 저장하고 검색하는 데 사용



# 로깅 설정
logging.basicConfig(
    filename='error_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)






def load_pdf(file_path): # 파일을 읽어 문서 데이터를 가져옵니다.
    loader = PyMuPDFLoader(file_path) # 클래스 정의 
    documents = loader.load()  
    print(f"Loaded {len(documents)} documents from the PDF.")
    return documents

def vectorDB(documents, api_key): # open AI embedding 기반으로 vectorDB 생성
    # 문서를 처리하기 좋은 크기의 조각으로 나누는 스플리터를 설정합니다.
    # 'ko_core_news_sm'은 한국어 처리를 위한 Spacy 모델입니다.
    text_splitter = SpacyTextSplitter(
        chunk_size=200, # 문서를 나누는 단위 
        pipeline="ko_core_news_sm"
    )

    splitted_documents = text_splitter.split_documents(documents)  # 문서를 나눕니다.
    print(f"Split into {len(splitted_documents)} document chunks.")

    # OpenAI의 임베딩 모델을 초기화합니다. 여기서는 'text-embedding-ada-002' 모델을 사용합니다.
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=api_key
    )
    vectordb = Chroma(
        persist_directory="./data",  # 데이터 저장 경로 지정
        embedding_function=embeddings  # 임베딩 함수 지정
    )
    vectordb.add_documents(splitted_documents)
    return vectordb

def create_qa_chain(retriever, model_name, api_key):
    """Create a QA chain using the retriever."""
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name=model_name, temperature=0,
                       openai_api_key=api_key),
        chain_type="stuff", #stuff,  map_reduce, refine
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain


def query_qa_chain(qa_chain, input_text, model):
    response = qa_chain(input_text)
    if not response['result']:
        # PDF에서 정보를 찾지 못한 경우 ChatGPT에게 직접 질문
        chat_model = model
        response = chat_model({"text": input_text})
        return response['choices'][0]['message']['content']
    return response['result']

def pdf_retriever(pdf_path, model_version, open_api_key):
    # RAG를 위한 vectorDB와 qa chain 을 로드함. 
    documents = ""
    vectordb = vectorDB(documents, open_api_key)
    retriever = vectordb.as_retriever(search_kwargs={"k": 1}) # 유사도가 높은 결과 1개 반환 
    qa_chain = create_qa_chain(retriever, model_version, open_api_key)
    return qa_chain

    


def collect_weather_data(): # URL 기반으로 교통 데이터를 크롤링한다. 
    # 네이버 검색 결과 URL
    # 1. 웹 페이지 요청
    url = "https://www.google.com/search?q=%EC%98%A4%EB%8A%98+%ED%8C%90%EA%B5%90%EB%82%A0%EC%94%A8+%EC%95%8C%EB%A0%A4%EC%A4%98&sca_esv=1c9cf38f255aeed1&sca_upv=1&sxsrf=ADLYWIKeeMcsc-RrBCF51vBVWdvvXwcpRg%3A1723434960027&ei=0Ie5ZrusAcfl2roPn6-5iAo&ved=0ahUKEwi71NfEx-6HAxXHslYBHZ9XDqEQ4dUDCA8&uact=5&oq=%EC%98%A4%EB%8A%98+%ED%8C%90%EA%B5%90%EB%82%A0%EC%94%A8+%EC%95%8C%EB%A0%A4%EC%A4%98&gs_lp=Egxnd3Mtd2l6LXNlcnAiHeyYpOuKmCDtjJDqtZDrgqDslKgg7JWM66Ck7KSYMgUQIRigATIFECEYoAFItDZQ3wRYwDRwEngAkAEFmAGzAaABiSuqAQQwLjM1uAEDyAEA-AEBmAIioALhFKgCEMICChAAGLADGNYEGEfCAgcQIxgnGOoCwgIUEAAYgAQYkQIYtAIYigUY6gLYAQHCAh0QLhiABBiRAhi0AhjHARjIAxiKBRjqAhivAdgBAsICBBAjGCfCAgoQIxiABBgnGIoFwgIFEAAYgATCAgsQLhiABBjRAxjHAcICBRAuGIAEwgIQEC4YgAQY0QMYQxjHARiKBcICHxAuGIAEGNEDGEMYxwEYigUYlwUY3AQY3gQY4ATYAQPCAhoQLhiABBjRAxjHARiXBRjcBBjeBBjgBNgBA8ICBxAAGIAEGArCAggQABiABBjLAcICCBAuGIAEGMsBwgILEAAYgAQYsQMYgwHCAgQQABgDwgIKEAAYgAQYQxiKBcICDRAuGIAEGEMY1AIYigXCAg0QABiABBixAxgUGIcCwgIIEAAYgAQYsQPCAgQQABgewgIGEAAYHhgPwgIGEAAYCBgewgIIEAAYCBgeGA_CAggQABgFGB4YD8ICChAAGIAEGEYYgALCAggQABiABBiiBMICCBAAGKIEGIkFwgIWEAAYgAQYRhiAAhiXBRiMBRjdBNgBBMICDBAAGIAEGA0YRhiAAsICGBAAGIAEGA0YRhiAAhiXBRiMBRjdBNgBBJgDB4gGAZAGA7oGBggBEAEYAboGBggCEAEYCLoGBggDEAEYFLoGBggEEAEYE5IHBTE4LjE2oAf81QE&sclient=gws-wiz-serp"
    response = requests.get(url)

    # 2. Beautiful Soup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')
    # 모든 텍스트 데이터 가져오기
    all_text = soup.get_text()
    print(all_text)
    return all_text




"""def collect_route_data(url, search_query): # URL 기반으로 교통 데이터를 크롤링한다. 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    #driver = webdriver.Chrome(service= Service(ChromeDriverManager(version="114.0.5735.90").install())) 

    # Chrome 브라우저를 제어하기 위한 드라이버 설정

    # 네이버 페이지로 이동
    
    driver.get(f"https://www.google.com/search?q=%EC%98%A4%EB%8A%98+%ED%8C%90%EA%B5%90%EB%82%A0%EC%94%A8+%EC%95%8C%EB%A0%A4%EC%A4%98&sca_esv=1c9cf38f255aeed1&sca_upv=1&sxsrf=ADLYWIKeeMcsc-RrBCF51vBVWdvvXwcpRg%3A1723434960027&ei=0Ie5ZrusAcfl2roPn6-5iAo&ved=0ahUKEwi71NfEx-6HAxXHslYBHZ9XDqEQ4dUDCA8&uact=5&oq=%EC%98%A4%EB%8A%98+%ED%8C%90%EA%B5%90%EB%82%A0%EC%94%A8+%EC%95%8C%EB%A0%A4%EC%A4%98&gs_lp=Egxnd3Mtd2l6LXNlcnAiHeyYpOuKmCDtjJDqtZDrgqDslKgg7JWM66Ck7KSYMgUQIRigATIFECEYoAFItDZQ3wRYwDRwEngAkAEFmAGzAaABiSuqAQQwLjM1uAEDyAEA-AEBmAIioALhFKgCEMICChAAGLADGNYEGEfCAgcQIxgnGOoCwgIUEAAYgAQYkQIYtAIYigUY6gLYAQHCAh0QLhiABBiRAhi0AhjHARjIAxiKBRjqAhivAdgBAsICBBAjGCfCAgoQIxiABBgnGIoFwgIFEAAYgATCAgsQLhiABBjRAxjHAcICBRAuGIAEwgIQEC4YgAQY0QMYQxjHARiKBcICHxAuGIAEGNEDGEMYxwEYigUYlwUY3AQY3gQY4ATYAQPCAhoQLhiABBjRAxjHARiXBRjcBBjeBBjgBNgBA8ICBxAAGIAEGArCAggQABiABBjLAcICCBAuGIAEGMsBwgILEAAYgAQYsQMYgwHCAgQQABgDwgIKEAAYgAQYQxiKBcICDRAuGIAEGEMY1AIYigXCAg0QABiABBixAxgUGIcCwgIIEAAYgAQYsQPCAgQQABgewgIGEAAYHhgPwgIGEAAYCBgewgIIEAAYCBgeGA_CAggQABgFGB4YD8ICChAAGIAEGEYYgALCAggQABiABBiiBMICCBAAGKIEGIkFwgIWEAAYgAQYRhiAAhiXBRiMBRjdBNgBBMICDBAAGIAEGA0YRhiAAsICGBAAGIAEGA0YRhiAAhiXBRiMBRjdBNgBBJgDB4gGAZAGA7oGBggBEAEYAboGBggCEAEYCLoGBggDEAEYFLoGBggEEAEYE5IHBTE4LjE2oAf81QE&sclient=gws-wiz-serp")

    # 페이지 로드 및 JavaScript 실행을 위해 잠시 대기
    time.sleep(5)

    # 원하는 요소 선택 (XPath 또는 CSS 선택자 사용 가능)
    # 예: 최적 경로에 해당하는 요소를 선택
    optimal_route = driver.find_element(By.XPATH, '//*[@id="main_pack"]/section/div/div/div/div/div[3]/div[1]/div/div[2]/ul/li[1]')

    # 요소의 텍스트 출력
    print(optimal_route.text)

    # 브라우저 종료
    driver.quit()
    return optimal_route.text
    
"""