import json
import os 
import requests
import logging
from urllib.parse import quote


# 로깅 설정
logging.basicConfig(
    filename='error_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def TMAP_API(start_lat, start_lon, end_lat, end_lon, TMAP_API_KEY):
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
        "count": 1, # 답변 출력 개수 1~10, 기본값은 10이다. 
        "lang": 0, # 출력 언어 선택 - 0: 한국어, 1: 영어
        "format": "json" # 출력 포맷 "json" or "xml"
    }
    
    # API 호출 
    response = requests.post(url, json=params, headers=headers) # POST 명령어 사용 
    json = response.json()
    if 'result' in json.keys():
        error_code, error_message = json['result']['status'], json['result']['message']
        logging.error(f"TMAP_API 에러 - 에러 코드: {error_code}, 에러 메시지 :{error_message}")
        return error_message
    return response.json()
        
        
    """ # 경로 정보 추출
        # json = response.json()
        return response.json()
    except Exception as e:
        return {'error': f'Tmap Public trans API do not respond\nerror msg:{response.json()}'}
"""

def get_coord(place_name, KAKAO_MAP_API_KEY): # place 이름을 주면 위도 경도 좌표를 포함한 dict을 리턴 
  x,y=  37.3948, 127.1112 # 장소 검색 기준 좌표 - 판교역
  radius = 100 # 기준 좌표에서 몇 KM 반경으로 검색할 것인가? 
  format = "json"
  size = 1 #검색 결과 사이즈 
  sort = 'accuracy'
  print("place:", place_name)
  # KAKAO_API_KEY = "KakaoAK 4f55134dcdd4c80401cb0f0d73403f35" # 'KaKaoAK xxxxx' 형태 
  # KAKAO_MAP_API_KEY = os.getenv(KAKAO_MAP_API_KEY) # check 
  place_name = quote(place_name)
  url = f'https://dapi.kakao.com/v2/local/search/keyword.{format}?query={place_name}&x={x}&y={y}&radius={radius}&size={size}&sort={sort}'
  # KAKAO_MAP_API_KEY = "KakaoAK 4f55134dcdd4c80401cb0f0d73403f35"
  headers = {"Authorization": KAKAO_MAP_API_KEY}
  # print('api_json:\n',api_json,"\n")

  
  
  try:
    api_json = json.loads(str(requests.get(url,headers=headers).text))
    result = api_json['documents'][0]
  except IndexError as ie:
    error_msg = f"KAKAO map keyword search api: no places were searched with query input: {place_name}"
    logging.error(error_msg)
    return "NO VALID INPUT"
  except Exception as e:
    error_msg = "KAKAO map keyword search api: Undefined error " + str(e)
    logging.error(error_msg)
    return "Undefined Error"

  crd = {"lat": result['y'], "lng": result['x'], 'place_name': result['place_name'], 'road_address_name': result['road_address_name']} # 위도와 경도, 장소명, 도로명 주소 
  return crd # 
 
def parsing_tmap(data, from_place_name, to_place_name): # 이동 정보 를 넣으면
    result = ''
    # print("data:", data)
    # 경로 정보 추출
    itinerary = data['metaData']["plan"]["itineraries"][0]

    # 1) 총 거리(km단위), 총 시간(시 단위 및 분 단위), 환승 횟수(지하철 및 버스 이용 횟수 포함), 총 요금(원 단위)
    total_distance_km = itinerary["totalDistance"] / 1000
    total_time_min = itinerary["totalTime"] / 60
    total_time_hr = int(total_time_min // 60)
    total_time_min = int(total_time_min % 60)
    transfer_count = itinerary["transferCount"] + 1  # 환승 횟수는 지하철 및 버스 이용 횟수 포함
    total_fare = itinerary["fare"]["regular"]["totalFare"]
    
    result = f'{from_place_name}에서 {to_place_name}까지 가는 길을 전달해드릴게요.\n'
    result += '<요약>\n'
    summary_text = (
        f"총 소요 시간: {total_time_hr} 시간 {total_time_min} 분\n"
        f"환승 횟수: {transfer_count} 회\n"
        f"총 요금: {total_fare} 원\n\n"
        f"이동 거리: {total_distance_km:.2f} km\n"
        )
    result += summary_text
    

    # 2) 상세 경로 안내
    result += '상세 경로 안내\n'
    route_description = ""
    previous_end_name =f"{from_place_name}"
    for leg in itinerary["legs"]:
        if leg["mode"] == "WALK":
            route_description += f"- {previous_end_name}부터 {leg['end']['name']}까지 {leg['sectionTime'] // 60}분 걸으세요.\n"
        elif leg["mode"] == "SUBWAY":
            #route_description += f"- {previous_end_name}에서 {leg['end']['name']}까지 {leg['Lane'][0]['route']}을 타고 {leg['sectionTime'] // 60}분 가세요.\n"
            route_description += f"- {previous_end_name}에서 {leg['end']['name']}까지 {leg['route']}을 타고 {leg['sectionTime'] // 60}분 가세요.\n"
        elif leg["mode"] == "BUS":
            #bus_name = leg['route'].replace(":", ' ')
            route_description += f"- {previous_end_name}에서 {leg['end']['name']}까지 {leg['route']} 버스를 타고 {leg['sectionTime'] // 60}분 가세요.\n"
        previous_end_name = leg["end"]["name"]
    result += route_description
    return result


def get_route_description(from_to, TMAP_API_KEY, KAKAO_MAP_API_KEY ):
    from_str, to_str = from_to['from'], from_to['to']
    """addresses = { # 추후 바꿔야함 
        "home": "용산역",     #Replace with actual home address logic if available
        "current": "사당역"  # Replace with actual current address logic if available
        }
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
        """
    # 장소는 home, current, unknown 이 있을 수 있다. 
    if 'unknown' in (from_str, to_str): # 목적지, 출발지가 제대로 입력되지 않은 경우 
        return None
    
    # 경도 위도로 변환
    from_cord = get_coord(from_str, KAKAO_MAP_API_KEY)
    to_cord = get_coord(to_str, KAKAO_MAP_API_KEY)
    if "NO VALID INPUT" in (from_cord, to_cord): # 에러 핸들링 
        return "제대로된 출발지나 목적지가 입력되지 않았습니다. 다시 입력해주세요."
    elif "Undefined Error" in (from_cord, to_cord): 
        return "예기치 못한 에러가 발생했습니다. 다시 입력해주세요."
    from_lat, from_lon = from_cord['lat'], from_cord['lng']
    to_lat, to_lon = to_cord['lat'], to_cord['lng']
    
    route_intro_text = '' # 경로 안내 텍스트 
    route_description = TMAP_API(from_lat, from_lon, to_lat, to_lon, TMAP_API_KEY) # 
    if type(route_description) == str: # error 메시지 인경우 
        print("다음 사유 때문에, 경로 탐색이 되지 않아요")
        return f"다음 사유 때문에, 경로 탐색이 되지 않아요 : {route_description}. 다시 출발지와 목적지를 입력해주세요"
    route_intro_text = parsing_tmap(route_description,from_cord['place_name'],to_cord['place_name'] )
    return route_intro_text