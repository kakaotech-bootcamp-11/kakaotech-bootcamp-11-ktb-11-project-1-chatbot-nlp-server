import re
import json
from models.llama import get_llama_model
import os
from collections import Counter

# JSON 파일에서 키워드를 불러오는 함수

keywords_path = os.path.join(os.path.dirname(__file__), 'keywords.json')

def load_keywords():
    with open(keywords_path, 'r', encoding='utf-8') as file:
        keywords = json.load(file)
    return keywords

# 날짜와 관련된 정보를 추출하는 함수
def extract_date(text):
    match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', text)
    if match:
        return f"{match.group(1)}월 {match.group(2)}일"
    return None

# 키워드 기반으로 title을 추출하는 함수 (날짜가 우선)
def extract_title(text, keywords):
    # 1. 날짜 먼저 추출
    date = extract_date(text)
    
    # 2. 스케줄 관련 키워드를 JSON 파일에서 제외
    schedule_keywords = keywords.get("schedule", [])
    
    # 3. 스케줄 키워드를 제외한 나머지 카테고리에서 키워드를 추출
    keyword_count = Counter()

    # 4. 모든 카테고리에서 키워드의 빈도를 카운트
    for category, keyword_list in keywords.items():
        if category != "schedule":  # 스케줄 관련 키워드는 제외
            for keyword in keyword_list:
                keyword_count[keyword] += text.count(keyword)

    # 5. 빈도수가 가장 높은 키워드 선택
    if keyword_count:
        keyword_found = keyword_count.most_common(1)[0][0]
    else:
        keyword_found = None

    # 6. 최종 타이틀 생성: 날짜와 가장 많이 등장한 키워드를 결합
    if date and keyword_found:
        return f"{date} {keyword_found} 안내"
    elif date:
        return f"{date} 안내"
    elif keyword_found:
        return f"{keyword_found} 안내"
    
    # 7. 키워드가 없는 경우 None 반환
    return None


# 공지 내용에서 content를 추출하는 함수
def extract_content(text):
    lines = text.split('\n')
    content = "\n".join(line for line in lines if line.strip())  # 빈 줄 제거
    return content

# LLM을 사용해 키워드를 생성하는 함수
def generate_keywords_with_llm(text):
    prompt = f"Extract keywords from the following text and classify it into categories: {text}"
    llm_response = get_llama_model(prompt)
    # LLM 응답을 처리해 키워드로 변환 (예시)
    return llm_response

# 최종적으로 title과 content를 추출하여 반환하는 함수
def process_input(text):
    # 키워드를 JSON 파일에서 로드
    keywords = load_keywords()
    
    # JSON 기반으로 타이틀 추출
    title = extract_title(text, keywords)
    
    # 타이틀을 JSON 키워드로 찾지 못하면 LLM을 통해 생성
    if not title:
        print("키워드를 찾지 못했습니다. LLM에게 생성을 요청합니다...")
        title = generate_keywords_with_llm(text)
    
    # 공지 내용 추출
    content = extract_content(text)
    
    return title, content
