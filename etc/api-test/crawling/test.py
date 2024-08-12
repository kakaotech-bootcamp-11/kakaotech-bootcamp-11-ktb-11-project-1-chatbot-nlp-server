from langchain_community.document_loaders import WebBaseLoader

# user_input()을 받음 
# 데이터를 긁어옴 
# 웹에서 검색함. query: 시흥신천역에서 강남역 가는 길 알려줘
# chatGPT 에서 RAG 모델을 생성한다. 
user_input = "시흥신천역에서 강남역 가는 길 알려줘"

url1 = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=시흥신천역에서+강남역+가는+길+알려줘"
loader = WebBaseLoader(web_path = (url1))

docs = loader.load()
len(docs)
print(docs)

