from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 티맵 API 키 설정
#WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")



#def get_weather(start_lat, start_lon, end_lat, end_lon):

"""def get_weather_script(): # API 구독이 필요함 
    WEATHER_API_KEY, LOCATION = os.environ.get("WEATHER_API_KEY"), os.environ.get("LOCATION")
    base_url = f'http://api.openweathermap.org/data/3.0/onecall/overview?q={LOCATION}&appid={WEATHER_API_KEY}'

    # API 호출
    response = requests.post(base_url) # POST 명령어 사용 

    if response.status_code == 200: # 성공적으로 API 호출 성공함 
        return response.json()
        #return response
    else:
        return jsonify({'error': f'weather API do not respond\nerror msg:{response.json()}'})
        # response.status_code"""

    
def get_weather_info():
    WEATHER_API_KEY, LOCATION = os.environ.get("WEATHER_API_KEY"), os.environ.get("LOCATION")
    LOCATION ="Seongnam-si"
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={WEATHER_API_KEY}'
    #base_url = f"http://api.openweathermap.org/data/2.5/forecast?lat=37.40013636554196&lon=127.1067841722373&appid=5b7e01bc69a35c65d46e126ec2b5a5d5&units=metric&lang=KR"


    # API 호출
    #response = requests.post(base_url) # POST 명령어 사용 
    response = requests.get(base_url) # POST 명령어 사용 

    if response.status_code == 200: # 성공적으로 API 호출 성공함 
        return response.json()
    else:
        return jsonify({'error': f'weather API do not respond\nerror msg:{response.json()}'})

@app.route('/weather_info', methods = ['GET'])
def weather_info():
    result= get_weather_info()
    return result

"""@app.route('/weather_script', methods = ['GET'])
def weather_script():
    result= get_weather_script()
    return result"""
if __name__ == '__main__':
    app.run(debug=True)
