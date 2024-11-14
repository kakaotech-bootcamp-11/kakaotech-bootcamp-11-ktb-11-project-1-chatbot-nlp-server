from utils.llama import get_llama_model
from utils.md_file_manager import handle_content
from utils.data_maker_prompt import create_persona_prompt_with_keywords
from utils.schedule_manager import handle_schedule_content
from utils.llm_response_parser import extract_category_from_response, extract_schedule_from_response
import os
from utils.input_processor import process_input



# 사용자 입력을 처리하고 전체 흐름을 진행하는 함수
def main():
    # 1. 사용자로부터 공지사항 입력 받기
    print("공지사항을 입력하세요:")
    user_input_text = input()

    # 2. JSON 파일 경로 설정
    json_file = "utils/keywords.json"

    # 3. 공지사항에서 title과 content 추출
    title, content = process_input(user_input_text)

    # 추출된 title과 content 확인
    print(f"추출된 Title: {title}")
    print(f"추출된 Content: {content}")

    # 4. 페르소나 프롬프트 생성 (공지 내용을 포함한 LLM 프롬프트 생성)
    persona_prompt = create_persona_prompt_with_keywords(user_input_text, json_file)
    
    # 5. LLaMA 모델을 통해 공지사항을 분류 (페르소나 프롬프트 사용)
    print("공지 내용을 처리 중입니다...")
    llm_response = get_llama_model(persona_prompt)
    
    # 추가된 디버깅 로그: LLaMA 응답을 출력합니다.
    print(f"LLM Response: {llm_response}")

    # 6. LLaMA 응답에서 카테고리와 일정 정보 추출 (응답 구조에 맞게 수정)
    detected_category = extract_category_from_response(llm_response)
    detected_schedule = extract_schedule_from_response(llm_response)

    # 추가된 디버깅 로그: 추출된 카테고리와 일정 정보를 출력합니다.
    print(f"Detected Category: {detected_category}")
    print(f"Detected Schedule: {detected_schedule}")

    # 7. 사용자에게 확인 후 분류 작업 진행
    print(f"공지 내용을 {detected_category}로 분류했고, 일정도 {detected_schedule}로 분류했는데 맞습니까? (y/n)")
    user_confirm = input().lower()

    if user_confirm == "y":
        # 8. 일정이 포함된 경우 스케줄 처리
        if detected_schedule:
            handle_schedule_content(user_input_text)

        # 9. 분류된 카테고리로 md 파일에 내용 추가
        handle_content(user_input_text, detected_category)
    else:
        # 10. 사용자가 분류를 다시 선택하는 로직
        print("해당 공지의 카테고리를 숫자로 입력하세요. 1. money 2. management_edu 3. others")
        category_input = input()
        category_mapping = {
            "1": "money",
            "2": "management_edu",
            "3": "others"
        }
        new_category = category_mapping.get(category_input, "others")

        # 스케줄 확인 절차
        print("해당 공지에 스케줄에 추가할 내용이 있습니까? (y/n)")
        schedule_confirm = input().lower()
        if schedule_confirm == "y":
            handle_schedule_content(user_input_text)

        # 11. 최종적으로 선택한 카테고리로 md 파일에 내용 추가
        handle_content(user_input_text, new_category)

if __name__ == "__main__":
    main()
