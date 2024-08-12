
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
from langchain.vectorstores import Chroma  # 벡터 데이터를 저장하고 검색하는 데 사용

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

def create_qa_chain(retriever, api_key, model):
    """Create a QA chain using the retriever."""
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0,
                       openai_api_key=api_key),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def query_qa_chain(qa_chain, input_text):
    """Query the QA chain and get the response."""
    response = qa_chain(input_text)
    print(response)
    return response['result']



if __name__ == "__main__":
    open_api_key = os.environ.get("OPENAI_API_KEY") # API 키 설정
    pdf_path = './data/data.pdf'

    documents = load_pdf(pdf_path)
    vectordb = vectorDB(documents, open_api_key)

    # QA 체인 생성 및 쿼리 
    retriever = vectordb.as_retriever(search_kwargs={"k": 1}) # 유사도가 높은 결과 1개 반환 
    qa_chain = create_qa_chain(retriever, open_api_key)
    input_text = "문재인 대통령 취임은 언제야?"
    response = query_qa_chain(qa_chain, input_text)
    print('결과: ', response)
    #documents = retriever.get_relevant_documents("현충일 제정일이 언제야??")
    
    
