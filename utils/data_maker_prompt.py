from langchain.prompts import PromptTemplate

import json

# JSON 파일에서 키워드 로드하는 함수
def load_keywords_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        keywords = json.load(file)
    return keywords

# JSON에서 키워드를 로드하여 페르소나 프롬프트를 생성하는 함수
def create_persona_prompt_with_keywords(content, json_file):
    keywords = load_keywords_from_json(json_file)
    
    # 카테고리별 키워드 텍스트 생성
    money_keywords = ", ".join(keywords.get("money", []))
    management_edu_keywords = ", ".join(keywords.get("management_edu", []))
    others_keywords = ", ".join(keywords.get("others", []))
    schedule_keywords = ", ".join(keywords.get("schedule", []))  # 스케줄 관련 키워드 추가

    # 동적으로 페르소나 프롬프트 생성
    persona_prompt_template = f"""
    당신은 일정, 돈, 교육 관리, 기타 공지사항을 관리하는 전문가입니다.
    사용자가 제공하는 텍스트에서 적절한 키워드를 추출하고, 이를 4가지 카테고리 (money, management_edu, schedule, others) 중 하나로 분류합니다. 
    각 카테고리에 맞는 키워드는 다음과 같습니다:

    - money: {money_keywords}
    - management_edu: {management_edu_keywords}
    - others: {others_keywords}

    당신의 역할은 제공된 텍스트에서 정확한 키워드를 추출하고, 적절한 카테고리로 분류하는 것입니다. 
    '{schedule_keywords}'과 관련된 키워드가 포함된 텍스트는 "schedule"에 따로 추가해야 합니다.
    """

    # 템플릿을 LLM에 제공할 텍스트로 포맷팅
    full_prompt = persona_prompt_template + f"\n\n다음 텍스트를 분류하세요: '{content}'"
    
    return full_prompt


# 테스트 예시
if __name__ == "__main__":
    test_content = """
    
    """
    
    # 키워드 JSON 파일 경로
    keywords_file = "keywords.json"
    
    # 페르소나 프롬프트 생성 및 출력
    result_prompt = create_persona_prompt_with_keywords(test_content, keywords_file)
    print(result_prompt)
