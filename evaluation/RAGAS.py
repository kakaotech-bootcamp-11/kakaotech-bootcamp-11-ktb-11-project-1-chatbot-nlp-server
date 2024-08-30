import pandas as pd
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from ragas import evaluate
from datasets import Dataset
from pdf_retriever import *
from dotenv import load_dotenv
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)


questions = ["What did the president say about Justice Breyer?", 
             "What did the president say about Intel's CEO?",
             "What did the president say about gun violence?",
            ]
ground_truths = [["The president said that Justice Breyer has dedicated his life to serve the country and thanked him for his service."],
                ["The president said that Pat Gelsinger is ready to increase Intel's investment to $100 billion."],
                ["The president asked Congress to pass proven measures to reduce gun violence."]]
answers = []
contexts = []


load_dotenv() # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정
MODEL_VERSION = "gpt-4o-mini" # "gpt-3.5-turbo"  
pdf_path = "data/ktb_data_08.pdf"


# RAG를 위한 vectorDB와 qa chain 을 로드함. 
documents = load_pdf(pdf_path)
splitted_docs = split_docs(documents)
db = vectorDB(OPENAI_API_KEY)
db.add_documents(splitted_docs)
retriever = db.as_retriever(search_kwargs={"k": 1}) # 유사도가 높은 결과 1개 반환 

rag_chain = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)

# Inference
for query in questions:
    answers.append(rag_chain.invoke(query))
    contexts.append([docs.page_content for docs in retriever.get_relevant_documents(query)])

# To dict
data = {
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truths": ground_truth
}


# Convert dict to dataset
dataset = Dataset.from_dict(data)


result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ]
)

df = result.to_pandas()



"""from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_correctness,
    context_recall,
    context_precision,
)



class TestQaGenerator: # 질문과 정답 답변을 생성함. 
    def __init__(self, pdf_path, api_key):
        self.pdf_path = pdf_path
        self.model_version = "gpt-4o-mini"
        self.api_key = api_key

    def load_and_split_document(self, split_chunk_size = None):
        # Load the PDF document
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["Title", "\n\n", ".", " "],  # Title, 문단, 문장, 단어 순으로 분할
            chunk_size=500,  # 각 청크의 최대 크기
            chunk_overlap=20  # 청크 간 중복되는 문자 수
        )
        docs = text_splitter.split_documents(documents)
        
        if split_chunk_size is None:
            return docs
        else:
            return docs[:split_chunk_size]
        #return docs

    def generate_testset(self, test_size=10):


        # generator with openai models
        generator_llm = ChatOpenAI(model=self.model_version) #, api_key=self.api_key)
        critic_llm = ChatOpenAI(model=self.model_version) # , api_key=self.api_key)
        embeddings = OpenAIEmbeddings()

        generator = TestsetGenerator.from_langchain(
            generator_llm, 
            critic_llm,
            embeddings
        )

        splitted_docs = self.load_and_split_document(split_chunk_size = 15) # chunk size 조절하기.. test
        distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25}
        
        # generate testset
        testset = generator.generate_with_langchain_docs(splitted_docs, test_size=test_size, distributions =distributions) # 수정 test_size
        # Print the generated test set
        print("point2")
        test_df = testset.to_pandas()
        return test_df

# TEST
if __name__ == "__main__":

    # 질문 만들기 데이터 만들기 
    pdf_path = "data/ktb_data_08.pdf"  # Replace with your actual PDF file path
    load_dotenv() # .env 파일에서 환경 변수를 로드합니다
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정

    testset_generator = TestQaGenerator(pdf_path, api_key=OPENAI_API_KEY)
    test_df = testset_generator.generate_testset(test_size=5) # test_size  : 질문 개수 
    questions = test_df["question"].values.tolist()
    ground_truths = test_df["ground_truth"].values.tolist()
    source_documents = test_df["contexts"].values.tolist()

    # 평가하기 
    answers = [] # RAG chain 답변
    contexts = []
    
    # RAG 모델 정의 
    MODEL_VERSION = "gpt-4o-mini" # "gpt-3.5-turbo"  
    rag_chain = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)

    test_df.to_csv("test.csv")
    questions = ["국민취업제도 설명해줘", "어쩌라고" ] 
    for question in questions:
        response = rag_chain.invoke({"query": question})

        print('response type:', response)
        answers.append(response['result'])
    

        
    response_dataset = Dataset.from_dict({
        "question": questions,
        "answer" : answers,
        "contexts" : contexts,
        "ground_truth" : ground_truths
    })

    # 평가 
    metrics = [ faithfulness,
                context_recall,
                context_precision,
                answer_correctness ]

    result = evaluate(
        response_dataset, 
        metrics = metrics
        )
    result_df = result.to_pandas()
    result_df.to_csv('result.csv')"""

