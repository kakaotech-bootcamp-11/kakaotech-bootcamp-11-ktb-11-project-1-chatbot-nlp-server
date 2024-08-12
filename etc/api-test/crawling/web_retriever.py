"""from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup

# user_input()을 받음 
# 데이터를 긁어옴 
# 웹에서 검색함. query: 시흥신천역에서 강남역 가는 길 알려줘
# chatGPT 에서 RAG 모델을 생성한다. 
user_input = "시흥신천역에서 강남역 가는 길 알려줘"

url1 = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=시흥신천역에서+강남역+가는+길+알려줘"
loader = WebBaseLoader(web_path = (url1))

docs = loader.load()
len(docs)
print(docs)"""


import requests
from bs4 import BeautifulSoup

# Step 1: Send a GET request to the Naver search URL
url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=%EC%8B%9C%ED%9D%A5%EC%8B%A0%EC%B2%9C%EC%97%AD%EC%97%90%EC%84%9C+%EA%B0%95%EB%82%A8%EC%97%AD+%EA%B0%80%EB%8A%94+%EA%B8%B8+%EC%95%8C%EB%A0%A4%EC%A4%98&oquery=%EC%8B%9C%ED%9D%A5%EC%8B%A0%EC%B2%9C%EC%97%AD%EC%97%90%EC%84%9C+%EA%B0%95%EB%82%A8%EC%97%AD+%EA%B0%80%EB%8A%94+%EA%B8%B8+%EC%95%8C%EB%A0%A4%EC%A4%98%22&tqi=irDAFsqo15Vss5BnfkdssssstW0-175331"
response = requests.get(url)

# Step 2: Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Step 3: Locate the element that contains the "최적의 경로" information
# You will need to inspect the HTML of the Naver search page to find the exact class or id
optimal_route = soup.find('div', class_='optimal_route_class')  # Replace 'optimal_route_class' with the actual class name

# Step 4: Extract and print the relevant data
if optimal_route:
    print(optimal_route.get_text())
else:
    print("Could not find the optimal route data.")


