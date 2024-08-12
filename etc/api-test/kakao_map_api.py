# 카카오맵 키워드 주소 검색 API 
# # API 테스트 : https://developers.kakao.com/tool/rest-api/open/get/v2-local-search-keyword.%7Bformat%7D
# # API 문서 : 

# 로깅 설정
import logging

# 로깅 설정
logging.basicConfig(
    filename='error_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 카카오API를 사용하여 주소->좌표 변환
import requests, json
KAKAO_API_KEY = "KakaoAK 4f55134dcdd4c80401cb0f0d73403f35" # 'KaKaoAK xxxxx' 형태 
def get_location(place_name):
  x,y=  37.3948, 127.1112 # 장소 검색 기준 좌표 
  radius = 100 # 기준 좌표에서 몇 KM 반경으로 검색할 것인가? 
  format = "json"
  size = 1 #검색 결과 사이즈 
  sort = 'accuracy'
  url = f'https://dapi.kakao.com/v2/local/search/keyword.{format}?query={place_name}&x={x}&y={y}&radius={radius}&size={size}&sort={sort}'
 
  headers = {"Authorization": KAKAO_API_KEY}
  api_json = json.loads(str(requests.get(url,headers=headers).text))
  # print('api esult:\n',api_json,"\n")


  try:
    result = api_json['documents'][0]
  except IndexError as ie:
    error_msg = f"KAKAO map keyword search api: no places were searched with query input: {place_name}"
    logging.error(error_msg)
    return None
  except Exception as e:
    error_msg = "KAKAO map keyword search api: Undefined error " + str(e)
    logging.error(error_msg)
    return None

  crd = {"lat": result['y'], "lng": result['x'], 'place_name': result['place_name'], 'road_address_name': result['road_address_name']} # 위도와 경도, 장소명, 도로명 주소 

  return crd # 

place_crd = get_location("강남역")
