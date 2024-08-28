
# langchain 라이브러리에서 필요한 모듈들을 가져옵니다.
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
from langchain.vectorstores import Chroma  
from openai import OpenAIError# 벡터 데이터를 저장하고 검색하는 데 사용
from dotenv import load_dotenv



def load_pdf(file_path): # 파일을 읽어 문서 데이터를 가져옵니다.
    loader = PyMuPDFLoader(file_path) # 클래스 정의 
    documents = loader.load()  
    print(f"Loaded {len(documents)} documents from the PDF.")
    return documents


"""def split_docs(documents):
    # 문서를 처리하기 좋은 크기의 조각으로 나누는 스플리터를 설정합니다.
    # 'ko_core_news_sm'은 한국어 처리를 위한 Spacy 모델입니다.
    text_splitter = SpacyTextSplitter(
        chunk_size=200, # 문서를 나누는 단위 
        pipeline="ko_core_news_sm"
    )"""

def split_docs(documents):
    # 문서를 처리하기 좋은 크기의 조각으로 나누는 스플리터를 설정합니다.
    # 'ko_core_news_sm'은 한국어 처리를 위한 Spacy 모델입니다.
    """text_splitter = Splitter(
        chunk_size=200, # 문서를 나누는 단위 
        pipeline="ko_core_news_sm"
    )"""

    # parameter  정의 : pdf 경로 및 chu
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["Title :", "\n", "\n\n", ".", " "],  # Title, 문단, 문장, 단어 순으로 분할
        chunk_size=500,  # 각 청크의 최대 크기
        chunk_overlap=50  # 청크 간 중복되는 문자 수
    ) # test 용 
    splitted_documents = text_splitter.split_documents(documents)  # 문서를 나눕니다.
    print(f"Split into {len(splitted_documents)} document chunks.")
    return splitted_documents

def vectorDB(api_key): # vectorDB 생성
    # OpenAI의 임베딩 모델을 초기화합니다. 여기서는 'text-embedding-ada-002' 모델을 사용합니다.
    embedding_function = OpenAIEmbeddings(
        model= "text-embedding-3-small", #"text-embedding-3-large", "text-embedding-ada-002",
        openai_api_key=api_key
    )
    db = None
    if os.path.exists("data/chroma.db"): # 이전에 존재한 경우 
        print("이미 벡터 db 존재")
        db = Chroma(persist_directory="data/chroma.db", embedding_function=embedding_function)
    else:
        print("새롭게 만들기")
        db = Chroma(
            persist_directory="data/chroma.db",  # 데이터 저장 경로 지정
            embedding_function=embedding_function  # 임베딩 함수 지정
        )
    return db 


def create_qa_chain(retriever, model_name, api_key):
    """Create a QA chain using the retriever."""
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name=model_name, temperature=0,
                       openai_api_key=api_key),
        chain_type="stuff", #stuff,  map_reduce, refine, map_rerank
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs = {
        "document_separator": "<<<<>>>>>"
        }
    )
    return qa_chain


def pdf_retriever(pdf_path, model_version, OPENAI_API_KEY): #, open_api_key): # test
    open_api_key = OPENAI_API_KEY # API 키 설정
    
    # RAG를 위한 vectorDB와 qa chain 을 로드함. 
    documents = load_pdf(pdf_path)
    splitted_docs = split_docs(documents)
    db = vectorDB(open_api_key)
    db.add_documents(splitted_docs)
    retriever = db.as_retriever(search_kwargs={"k": 1}) # 유사도가 높은 결과 1개 반환 
    qa_chain = create_qa_chain(retriever, model_version, open_api_key)
    return qa_chain

"""
## ==== test ===========
if __name__ == "__main__":
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    pdf_path = './data/data.pdf' # PDF 경로를 지정해주기 -

    documents = load_pdf(pdf_path)
    vectordb = vectorDB(documents, open_api_key)
    model_version = "gpt-3.5-turbo"

    # QA 체인 생성 및 쿼리 
    retriever = vectordb.as_retriever(search_kwargs={"k": 1}) # 유사도가 높은 결과 1개 반환 
    qa_chain = create_qa_chain(retriever, open_api_key)
    # input_text = "문재인 대통령 취임은 언제야?"
    input_text = "오늘 판교 날씨 알려줘"
    response = query_qa_chain(qa_chain, input_text, model_version)
    print('결과: ', response)
    #documents = retriever.get_relevant_documents("현충일 제정일이 언제야??")

## ==== test ===========
# """
    
