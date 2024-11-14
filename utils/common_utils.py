import re

# 텍스트에서 날짜를 추출하는 함수 (일정 업데이트를 위해 사용)
def extract_date(text):
    """
    주어진 텍스트에서 날짜 정보를 추출합니다.
    예: '8월 13일' -> '8월 13일'
    """
    match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', text)
    if match:
        return f"{match.group(1)}월 {match.group(2)}일"
    return None

# 월 정보 추출을 위한 정규식 패턴
def extract_month(date_text):
    """
    주어진 날짜 텍스트에서 '월' 정보를 추출합니다.
    예: '8월 13일' -> 8 반환
    """
    month_match = re.search(r'(\d{1,2})월', date_text)
    if month_match:
        return int(month_match.group(1))
    return None

# 파일에 내용을 추가하는 함수
def append_to_file(file_path, content, is_schedule=False):
    """
    .md 파일에 내용을 추가합니다. 타이틀과 내용 사이에 구분선을 추가하여 시각적으로 구분합니다.
    
    :param file_path: 파일 경로
    :param content: 추가할 내용
    :param is_schedule: 일정 관련 내용인지 여부
    """
    with open(file_path, 'a', encoding='utf-8') as file:
        # 타이틀과 내용 사이에 구분선 또는 공백 추가
        if is_schedule:
            file.write("\n\n---\n")  # 일정 추가시 구분선 추가
        else:
            file.write("\n\n# Title : " + content.split('\n')[0] + "\n")  # 타이틀을 첫 줄로 추가
        
        # 나머지 내용 추가
        file.write(content + "\n")

# 스케줄에 추가할 내용이 있는지 먼저 물어봄
def ask_for_schedule_details():
    """
    사용자가 스케줄에 추가할 내용이 있는지 물어보고, 있으면 날짜/내용/장소를 반환.
    """
    print("해당 공지에 스케줄에 추가할 내용이 있습니까? (y/n)")
    schedule_exists = input().lower()

    # 일정이 있는 경우
    if schedule_exists == "y":
        print("해당 공지의 날짜 및 내용을 스페이스바를 기준으로 알려주세요 (예시: 8월13일 코딩테스트 장소없음)")
        schedule_input = input()

        # 스케줄 입력이 없을 경우 기본값 설정
        if not schedule_input.strip():
            schedule_input = "날짜/내용 없음"

        # 스페이스바를 기준으로 나눈 입력값 처리
        schedule_parts = schedule_input.split(" ", 1)

        if len(schedule_parts) == 2:
            date, description = schedule_parts
            place = description.split(" ", 1)[1] if len(description.split(" ", 1)) > 1 else "장소 없음"
        else:
            date = schedule_parts[0]
            place = "장소 없음"

        return f"{date} / {schedule_parts[0]} / {place}"

    return None
