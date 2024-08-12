import json

# JSON 파일 읽기
with open('cities.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# country가 "KR"인 모든 이름을 추출
#kr_names = [city['name'] for city in data if city['country'] == 'KR' and city['name'].startswith('S') ]


# 결과 출력
print(kr_names)