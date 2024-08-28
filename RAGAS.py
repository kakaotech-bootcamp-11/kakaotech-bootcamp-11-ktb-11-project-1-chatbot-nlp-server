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
from pdf_retriever import pdf_retriever
from dotenv import load_dotenv


from ragas.metrics import (
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

    def load_and_split_document(self, chunk_size):
        # Load the PDF document
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["Title :", "\n\n", ".", " "],  # Title, 문단, 문장, 단어 순으로 분할
            chunk_size=500,  # 각 청크의 최대 크기
            chunk_overlap=20  # 청크 간 중복되는 문자 수
        )
        docs = text_splitter.split_documents(documents)
        
        #return docs[:chunk_size]
        print(docs[0])
        return docs

    def generate_testset(self, test_size=10):
        # 한국어 프롬프트 템플릿 예시
        """prompt_template = PromptTemplate(
            input_variables=["context"],
            template="다음 문맥을 기반으로 질문을 생성하세요: {context}"
        )"""

        # generator with openai models
        generator_llm = ChatOpenAI(model=self.model_version) #, api_key=self.api_key)
        critic_llm = ChatOpenAI(model=self.model_version) # , api_key=self.api_key)
        embeddings = OpenAIEmbeddings(api_key=self.api_key)

        generator = TestsetGenerator.from_langchain(
            generator_llm, 
            critic_llm,
            embeddings
        )

        splitted_docs = self.load_and_split_document(chunk_size = 15) # chunk size 조절하기.. test
        distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25}

        print("point1")
        
        # generate testset
        testset = generator.generate_with_langchain_docs(splitted_docs, test_size=test_size, distributions =distributions) # 수정 test_size
        # Print the generated test set
        print("point2")
        #test_df = testset.to_pandas()
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

    #print("questions:\n", questions, '\n')
    #test_df.to_csv("test.csv")
    questions = ["국민취업제도 설명해줘", "어쩌라고" ] 
    for question in questions:
        response = rag_chain.invoke({"query": question})
        print('response type:', response)
        
        break
        answers.append(response['result'])
    

        
    """response_dataset = Dataset.from_dict({
        "question": questions,
        "answer" : answers,
        "contexts" : contexts,
        "ground_truth" : ground_truths
    })"""

    """# 평가 
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


    

    #df.to_csv('./QAexamples1.csv')
