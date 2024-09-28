import json
import os 
import requests
from dotenv import load_dotenv
import logging


logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def weather_api():
    # 환경 변수 받아오기
    load_dotenv()
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
    LOCATION = os.environ.get("LOCATION1")
    """# Print the values to verify they are correctly retrieved
    print("WEATHER_API_KEY:", WEATHER_API_KEY)
    print("LOCATION:", LOCATION)"""
    

    if not WEATHER_API_KEY or not LOCATION: # WEATHER_API_KEY와 LOCATION이 로딩 안됐을 때
        logging.error('API key or location is not loaded')
        return {'error': 'API key or location is not set in environment variables.'}
    
    # 날씨 API 요청하기
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={WEATHER_API_KEY}&units=metric'
    #print("base_url:", base_url)
    
    try:
        response = requests.post(base_url) 
        response = response.json()
        if response['cod'] != 200:
            logging.error(f'open weather map api err code: {response['cod']}, err msg {response['message']}\n - WEATHER_API_KEY:{WEATHER_API_KEY}, LOCATION:{LOCATION} ')
            return {'error': f'err code: {response['cod']}, err msg: {response['message']}'}
        #return response.json()
        return response
        
    except requests.exceptions.HTTPError as http_err:
        return {'error': f'HTTP error occurred: {http_err}'}
    except Exception as err:
        return {'error': f'Other error occurred: {err}'}

def weather_data_prompt(data): # data는 json 형식으로 날씨 정보를 담고 있음. 
    # overview of weather - data의 weather 오브젝트에 관련 정보가 있음. 
    main_weather_info = "주요 기상 상태:  "
    #print("weather data", data)
    for weather in data['weather']:
        weather_main = weather['main']
        weather_description = weather['description']
        main_weather_info += f"{weather_main}:{weather_description}. "
    main_weather_info += '\n'

    # 디테일한 정보 
    temp_celsius = data['main']['temp']
    feels_like_celsius = data['main']['feels_like'] # 체감 온도
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    clouds_all = data['clouds']['all']
    rain_1h = data.get('rain', {}).get('1h', 0) # 지난 1시간의 rain 강수량, 없으면 0 리턴 
    snow_1h = data.get('snow', {}).get('1h', 0)

    # Create the desired string

    detailed_weather_info = (
        f"세부 정보: "
        f"온도: {temp_celsius:.2f}°C,"
        f"체감 온도: {feels_like_celsius:.2f}°C,"
        f"기압: {pressure} hPa,"
        f"습도: {humidity}%,"
        f"풍속: {wind_speed} m/s,"
        f"구름 양: {clouds_all}%,"
    )
    if rain_1h > 0:
        detailed_weather_info += f"강우량(지난 1시간): {rain_1h} mm,"
    if snow_1h > 0:
        detailed_weather_info += f"강설량(지난 1시간): {snow_1h} mm,"

    # Print the weather information
    result = main_weather_info+detailed_weather_info
    return result

def get_weather_info():
    data = weather_api() # API를 통해서 날씨 정보 받아옴, json 형식  
    #print("weather api key data:", data)
    if 'error' in data.keys(): # API 키와 LOCATION이 환경 변수 파일에서 잘 로드가 안됨 
        # logging 
        prompt = "죄송해요, 시스템 오류가 있어요. 다시 말해줄래요? "
    else: 
        prompt = weather_data_prompt(data) #필요한 정보만 받아서, prompt로 생성 
    return prompt





"""
# TEST 
if __name__ == "__main__":
    json = get_weather_info()
    #json = {'coord': {'lon': 21.0118, 'lat': 52.2298}, 'weather': [{'id': 500, 'main': 'Clouds', 'description': 'light cloud', 'icon': '10d'}, {'id': 500, 'main': 'Rain', 'description': 'light rain', 'icon': '10d'}], 'base': 'stations', 'main': {'temp': 291.1, 'feels_like': 291.01, 'temp_min': 289.62, 'temp_max': 292.51, 'pressure': 1009, 'humidity': 79, 'sea_level': 1009, 'grnd_level': 995}, 'visibility': 10000, 'wind': {'speed': 4.47, 'deg': 20, 'gust': 0}, 'rain': {'1h': 0.11}, 'clouds': {'all': 100}, 'dt': 1722668540, 'sys': {'type': 2, 'id': 2092919, 'country': 'PL', 'sunrise': 1722654022, 'sunset': 1722709427}, 'timezone': 7200, 'id': 756135, 'name': 'Warsaw', 'cod': 200}
    print(parsing_weather_info(json))"""




