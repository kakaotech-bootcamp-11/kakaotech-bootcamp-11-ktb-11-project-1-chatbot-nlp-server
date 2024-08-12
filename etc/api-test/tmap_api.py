from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 티맵 API 키 설정
TMAP_API_KEY = os.environ.get("TMAP_API_KEY")



def get_public_transport_info(start_lat, start_lon, end_lat, end_lon):
    url = "https://apis.openapi.sk.com/transit/routes"
    
    # 헤더 정의
    headers = {
        "Content-Type": "application/json", # "application/xml": xml 형식으로 request 하고 싶으면 
        "appKey": TMAP_API_KEY # sk openapi 웹페이지에서 만든 API KEY, .env에 지정해놓음
    }
    
    params = {
        "startX": start_lon,
        "startY": start_lat,
        "endX": end_lon,
        "endY": end_lat,
        "count": 2, # 답변 출력 개수 1~10, 기본값은 10이다. 
        "lang": 0, # 출력 언어 선택 - 0: 한국어, 1: 영어
        "format": "json" # 출력 포맷 "json" or "xml"
    }

    # API 호출
    response = requests.post(url, json=params, headers=headers) # POST 명령어 사용 

    if response.status_code == 200: # 성공적으로 API 호출 성공함 
        return response.json()
        #return response
    else:
        return jsonify({'error': f'Tmap Public trans API do not respond\nerror msg:{response.json()}'})
        # response.status_code

# 데이터 저장 -> user input 
@app.route('/find_route', methods = ['GET'])
def find_route():
    start_lat, start_lon = 37.4766, 126.9816 #사당역
    #end_lat, end_lon = 37.496486063, 127.028361548 # 강남 
    #end_lat, end_lon = 37.579617, 126.977041 # 경복궁  
    end_lat, end_lon = 37.4766, 126.9816 #사당역
    result = get_public_transport_info(start_lat, start_lon, end_lat, end_lon)
    return result

if __name__ == '__main__':
    app.run(debug=True)