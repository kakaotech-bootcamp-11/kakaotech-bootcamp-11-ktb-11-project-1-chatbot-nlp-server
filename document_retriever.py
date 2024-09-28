from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from conversation_history import history
from mongo_client import get_mongo_client

import pprint
import json
import logging, os
import ssl
from dotenv import load_dotenv

def load_md_files(file_path): # file path 내의 모든 md 파일을 읽어 문서 데이터를 가져온다.
    # 해당 폴더 내의 모든 .md 파일을 가져오기
    loader = TextLoader(file_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from the MD.")
    print("len(docs):", len(documents) )

    return documents

def split_docs(documents):

    # 단계 1: 문서 로드(Load Documents)
    assert len(documents) == 1 # 수정 - 파일 여러 개일 떄
    assert isinstance(documents[0], Document) # 수정 - 파일 여러 개일 때
    readme_content = documents[0].page_content

    """# 단계 2: 문서 분할(Split Documents)"""
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    splitted_md = markdown_splitter.split_text(readme_content)
    return splitted_md

def create_bm25_retriever(splitted_docs): # vectorDB 생성
    bm25_retriever = BM25Retriever.from_documents(
        splitted_docs,
        )
    bm25_retriever.k = 1  # BM25Retriever의 검색 결과 개수를 1로 설정합니다.
    print("bm25 retriever created")
    return bm25_retriever

def create_FAISS_retriever(splitted_docs): # vectorDB 생성
    embedding_function = OpenAIEmbeddings()
    faiss_db = None
    faiss_index_path = "data/retrievers/faiss_index"  # FAISS 인덱스를 저장할 디렉토리 경로
    index_faiss_file, index_pkl_file = os.path.join(faiss_index_path, "index.faiss"), os.path.join(faiss_index_path, "index.pkl")

    if os.path.exists(index_faiss_file) and os.path.exists(index_pkl_file):  # Check if both files exist
        print("이미 FAISS index 존재")
        faiss_db = FAISS.load_local(
            faiss_index_path,
            embeddings=embedding_function,
            allow_dangerous_deserialization=True  # 역직렬화 혀용
        )
    else:
        print("새롭게 FAISS index 만들기")
        # 새로운 문서 리스트를 생성하거나 불러와서 FAISS 벡터스토어를 초기화
        faiss_db = FAISS.from_documents(splitted_docs, embedding=embedding_function)
        faiss_db.save_local(faiss_index_path) # FAISS 인덱스를 로컬에 저장

    # results = faiss_db.similarity_search_with_score(query, top_k = 3)
    # # for 문을 사용하여 결과 출력
    # for idx, (document, score) in enumerate(results):
    #     print(f"Result {idx + 1}:")
    #     #print(f"Document: {document}")
    #     print(f"Similarity Score: {score}")
    #     print("-" * 50)  # 구분선 출력
    faiss_retriever = faiss_db.as_retriever(search_kwargs={"score_threshold": 0.7})
    # faiss_retriever.score
    return faiss_retriever, faiss_db

def create_ensemble_retriever(retrievers): # retrievers: lst
    ensemble_retriever = EnsembleRetriever(
        retrievers= retrievers,
        weights=[0.7, 0.3],
    )
    print("Retriever created.")

    return ensemble_retriever


def create_qa_chain(ensemble_retriever):
    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved context to answer the question. 
        Consider the intent behind the question to provide the most relevant and accurate response. 
        Remember to compare the specific time in the question with the time mentioned in the context to determine the correct answer.
        If you don't know answer, just give me an answer based on your basic knowledge in detail.
        #Question: 
        {question} 
        #Context: 
        {context} 
        #Previous Chat History:
        {chat_history} 
        #Answer:"""
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0, streaming=True)# , max_tokens = 150)
    multiquery_retriever = MultiQueryRetriever.from_llm(  #
        retriever=ensemble_retriever,
        llm=llm,
    )

    print("LLM created.")
    """Create a QA chain using the retriever."""
    rag_chain = (
        {"context": multiquery_retriever, "question": RunnablePassthrough(), "chat_history": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

def my_retriever(file_path):
    ssl._create_default_https_context = ssl._create_unverified_context
    load_dotenv() # api key 정보 로드

    # RAG를 위한 vectorDB와 qa chain 을 로드함.
    documents = load_md_files(file_path)
    splitted_docs = split_docs(documents)
    bm25_retriever = create_bm25_retriever(splitted_docs)
    faiss_retriever, faiss_db = create_FAISS_retriever(splitted_docs)
    ensemble_retriever = create_ensemble_retriever([bm25_retriever, faiss_retriever])
    rag_chain = create_qa_chain(ensemble_retriever)
    return rag_chain, faiss_db

# ==== test ======
"""if __name__ == "__main__":
    rag_chain = my_retriever('data/ktb_data_09.md')   
    question = '8월에 며칠 이상 출석해야 훈련 장려금 받을 수 있어?'
    print("question:\n", question)
    response = rag_chain.invoke(question)
    print('response:\n', response)
"""