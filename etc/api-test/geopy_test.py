from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_lat_lon(place_name):
    try:
        geolocator = Nominatim(user_agent="my-ai-server", timeout=10)
        location = geolocator.geocode(place_name)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except GeocoderTimedOut:
        print("Geocoding service timed out")
        return None
    except GeocoderServiceError as e:
        print(f"Geocoding service error: {e}")
        return None

# 예제 사용
place_name = "유스페이스몰"
coordinates = get_lat_lon(place_name)

if coordinates:
    print(f"{place_name}의 좌표는 {coordinates[0]}, {coordinates[1]} 입니다.")
else:
    print(f"{place_name}의 좌표를 찾을 수 없습니다.")