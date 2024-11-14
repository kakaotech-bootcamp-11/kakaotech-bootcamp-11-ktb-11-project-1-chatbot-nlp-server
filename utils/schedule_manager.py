from utils.common_utils import extract_date, append_to_file, ask_for_schedule_details

def handle_schedule_content(text):
    """
    스케줄 관련 내용을 처리하여 schedule.md 파일에 추가합니다.
    """
    schedule_entry = ask_for_schedule_details()
    
    if schedule_entry:
        append_to_file("data/schedule.md", schedule_entry, is_schedule=True)
        print("일정이 성공적으로 추가되었습니다.")
    else:
        print("일정 정보가 없어 schedule.md에 추가하지 않았습니다.")
