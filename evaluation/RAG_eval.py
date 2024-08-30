### pdf title 단위로 데이터 생성하기 
import os 
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.evaluation.qa import QAGenerateChain
from langchain.evaluation.qa import QAEvalChain
from langchain_text_splitters import RecursiveCharacterTextSplitter, SpacyTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


from pdf_retriever import *


load_dotenv() # # .env 파일에서 환경 변수를 로드합니다
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API 키 설정
# LLM 변수 정의 
MAX_TOKENS_OUTPUT = 200
STREAM_TOKEN_SIZE = 30
MODEL_VERSION = "gpt-4o" # "gpt-3.5-turbo"  


"""def split_docs(documents):
    # 문서를 처리하기 좋은 크기의 조각으로 나누는 스플리터를 설정합니다.
    # 'ko_core_news_sm'은 한국어 처리를 위한 Spacy 모델입니다.
    text_splitter = RecursiveCharacterTextSplitter(
        # 청크 크기를 매우 작게 설정합니다. 예시를 위한 설정입니다.
        chunk_size=250,
        # 청크 간의 중복되는 문자 수를 설정합니다.
        chunk_overlap=30,
        # 문자열 길이를 계산하는 함수를 지정합니다.
        length_function=len,
        # 구분자로 정규식을 사용할지 여부를 설정합니다.
        is_separator_regex=False
    )

    splitted_documents = text_splitter.split_documents(documents)  # 문서를 나눕니다.
    print(f"Split into {len(splitted_documents)} document chunks.")
    return splitted_documents"""




def paragraphWiseDocumentReading(pdf_path):
    documents = load_pdf(pdf_path)
    splitted_documents = split_docs(documents, SpacyTextSplitter)
    """for doc in splitted_documents[:50]:
        print(doc)
        print("-------")"""



def create_QA_examples(splitted_documents): # 문서에 대해서 질문과 모범답안 생성해주는 함수 
    llm = ChatOpenAI(model=MODEL_VERSION)
    #prompt = PromptTemplate(
    #    input_variables=["doc"],
    #    template = "한국어로 질문과 텍스트를 만들어줘: {doc}"
    #)
   # LLMChain 생성
    #llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    # QAGenerateChain 생성 (llm_chain을 인자로 전달)
    QA_generation_chain = QAGenerateChain.from_llm(llm)  # QA 체인 생성 

    splitted_documents = [t.page_content if hasattr(t, 'page_content') else str(t) for t in splitted_documents]
    #QA_examples = QA_generation_chain.apply_and_parse(
    QA_examples = QA_generation_chain.apply(
        [{"doc": t} for t in splitted_documents]
    )
    QA_examples = [item['qa_pairs'] for item in QA_examples]
    print("QA_examples:\n", QA_examples)
    
    return QA_examples
        

def QA_evaluation(retrieval_qa, QA_examples):
    llm = ChatOpenAI(temperature = 0.0, model=MODEL_VERSION)
    predictions = retrieval_qa.apply(QA_examples) # 예측값 생성
    eval_chain = QAEvalChain.from_llm(llm = llm) # 평가 chain 생성

    graded_outputs = eval_chain.evaluate(QA_examples, predictions)
    num_correct = 0
    for i, qa_pair in enumerate(QA_examples):
        print(f"Example {i}:")
        print("Question: " + predictions[i]['query'])
        print("Real Answer: " + predictions[i]['answer'])
        print("Predicted Answer: " + predictions[i]['result'])
        print("Predicted Grade: " + graded_outputs[i]['results'])
        print("-"*10)
        if graded_outputs[i]['results'] == "CORRECT":
            num_correct += 1
    print('accuracy:', num_correct/len(QA_examples)*100)

if __name__ == "__main__":
    pdf_path = './data/ktb_data_07_3.pdf'
    retrieval_qa = pdf_retriever(pdf_path, MODEL_VERSION, OPENAI_API_KEY)
    
    documents = load_pdf(pdf_path)
    splitted_documents = split_docs(documents, SpacyTextSplitter) 
    QA_examples = create_QA_examples(splitted_documents[:10])
    QA_evaluation(retrieval_qa, QA_examples)
