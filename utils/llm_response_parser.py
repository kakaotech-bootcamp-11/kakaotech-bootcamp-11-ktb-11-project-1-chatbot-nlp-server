import re

def extract_category_from_response(llm_response):
    """
    LLaMA 모델의 응답에서 카테고리 정보를 추출하는 함수.
    예시 응답에 따라 적절하게 카테고리 추출 로직을 추가해야 합니다.
    """
    if "money" in llm_response:
        return "money"
    elif "management" in llm_response:
        return "management_edu"
    else:
        return "others"

def extract_schedule_from_response(llm_response):
    """
    LLaMA 모델의 응답에서 일정 정보를 추출하는 함수.
    예시 응답에 따라 적절하게 일정 정보를 추출해야 합니다.
    """
    match = re.search(r'\d{1,2}월\s*\d{1,2}일', llm_response)
    if match:
        return match.group(0)
    return None
