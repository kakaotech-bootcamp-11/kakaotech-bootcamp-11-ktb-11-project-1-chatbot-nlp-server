import json
import os 
import requests
import logging
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def transportation_API(start_lat, start_lon, end_lat, end_lon):
    url = "https://apis.openapi.sk.com/transit/routes"
    TMAP_API_KEY = os.getenv("TMAP_API_KEY")
    
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
        "count": 1, # 답변 출력 개수 1~10, 기본값은 10이다. 
        "lang": 0, # 출력 언어 선택 - 0: 한국어, 1: 영어
        "format": "json" # 출력 포맷 "json" or "xml"
    }

    # API 호출
    response = requests.post(url, json=params, headers=headers) # POST 명령어 사용 

    if response.status_code == 200: # 여기 수정 200이어도 에러 발생 가능 
        return response.json()
        #return response
    else:
        return {'error': f'Tmap Public trans API do not respond\nerror msg:{response.json()}'}
        # response.status_code


def get_lat_lon(place_name):
    try:
        geolocator = Nominatim(user_agent="my-ai-server", timeout=10)
        location = geolocator.geocode(place_name)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    # error 고쳐야함 - 한국 밖으로 매핑 되는 경ㅇ우 
    except GeocoderTimedOut:
        print("Geocoding service timed out")
        return None
    except ValueError as ve:
        print(f"No valid address '{place_name}': {ve}")
        return None
    except GeocoderServiceError as e:
        print(f"Geocoding service error: {e}")
        return None
 
def parsing_traffic(data): # 이동 정보 를 넣으면

    result = ''
    # 에러 {'result': {'message': '출발 정류장 없음', 'status': 12}}
    print(data)
    # 첫 번째 경로 정보 추출
    #itinerary = data['result']
    itinerary = data['metaData']["plan"]["itineraries"][0]
    

    # 1) 총 거리(km단위), 총 시간(시 단위 및 분 단위), 환승 횟수(지하철 및 버스 이용 횟수 포함), 총 요금(원 단위)
    total_distance_km = itinerary["totalDistance"] / 1000
    total_time_min = itinerary["totalTime"] / 60
    total_time_hr = int(total_time_min // 60)
    total_time_min = int(total_time_min % 60)
    transfer_count = itinerary["transferCount"] + 1  # 환승 횟수는 지하철 및 버스 이용 횟수 포함
    total_fare = itinerary["fare"]["regular"]["totalFare"]

    # 결과 출력
    # 결과 요약
    result = '<요약>\n'
    summary_text = (
        f"총 거리: {total_distance_km:.2f} km\n"
        f"총 시간: {total_time_hr} 시간 {total_time_min} 분\n"
        f"환승 횟수: {transfer_count} 회\n"
        f"총 요금: {total_fare} 원\n\n"
        )
    result += summary_text


    # 2) 가는 길 경로 설명
    route_description = ""
    previous_end_name = "출발지"
    for leg in itinerary["legs"]:
        if leg["mode"] == "WALK":
            route_description += f"- {previous_end_name}부터 {leg['end']['name']}까지 {leg['sectionTime'] // 60}분 걸으세요.\n"
        elif leg["mode"] == "SUBWAY":
            route_description += f"- {previous_end_name}에서 {leg['end']['name']}까지 {leg['Lane'][0]['route']}을 타고 {leg['sectionTime'] // 60}분 가세요.\n"
        elif leg["mode"] == "BUS":
            route_description += f"- {previous_end_name}에서 {leg['end']['name']}까지 {leg['route']} 버스를 타고 {leg['sectionTime'] // 60}분 가세요.\n"
        previous_end_name = leg["end"]["name"]
    result += '경로 안내\n'
    result += route_description
    return result


def get_route_description(from_to):
    
    from_str, to_str = from_to['from'], from_to['to']
    # 민약에 현재 위치가 있으면 - 현재 위치 불러옴 

    #
    addresses = { # 추후 바꿔야함 
        "home": "용산역",     #Replace with actual home address logic if available
        "current": "사당역"  # Replace with actual current address logic if available
        }

    # 장소는 home, current, unknown 이 있을 수 있다. 
    if 'unknown' in (from_str, to_str): # 목적지, 출발지가 제대로 입력되지 않은 경우 
        return None
    
    # from 
    if from_str == 'home':
        from_str = addresses['home']
    elif from_str == 'current':
        from_str =  addresses['current']
    
    # to
    if to_str == 'home':
        to_str = addresses['home']
    elif to_str == 'current':
        to_str =  addresses['current']

    # 경도 위도로 변환

    # latitude 찾을 수 없는 경우 - 알 수 없습니다..? 
    print("get_lat_lon(from_str)", get_lat_lon(from_str))
    print("get_lat_lon(to_str)", get_lat_lon(to_str))
    from_lat, from_lon = get_lat_lon(from_str)
    to_lat, to_lon = get_lat_lon(to_str)

    print("from_str, to_str", from_str, to_str)
    print(from_lat, from_lon)
    print(to_lat, to_lon)

    result = ''
    result = transportation_API(from_lat, from_lon, to_lat, to_lon)
    """try : 
        # 판교역 > pygeo 가 북한으로 매핑 시켜줌 > transportation API 인식 못합니다. 
        result = transportation_API(from_lat, from_lon, to_lat, to_lon)
        
    except Error as e:
        # 에러 메시지 인쇄 
        return None"""
    
    result = parsing_traffic(result)

    return result


    
    





    



    

