from utils.common_utils import append_to_file

# 텍스트를 처리하고 분류된 카테고리에 맞게 파일에 내용을 추가하는 함수
def handle_content(text, category):
    """
    텍스트를 카테고리별로 분류한 후, 해당 카테고리의 .md 파일에 내용을 추가.
    """
    file_path = f"data/{category}.md"
    append_to_file(file_path, text)
    print(f"{category} 파일에 성공적으로 추가되었습니다.")
