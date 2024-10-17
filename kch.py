import streamlit as st
from streamlit.components.v1 import html
import requests

# Kakao JavaScript API 키 설정
KAKAO_API_KEY = "d693cf4169b24f12ec19b0a6713f58f4"
KAKAO_REST_API_KEY = "8741ff3930e0c669e15cf0781c95c8a6"

# HTML 코드 작성 (Kakao 지도)
def kakao_map_html(lat, lon, places):
    places_script = ""
    for place in places:
        places_script += f"""
        var marker = new kakao.maps.Marker({{
            map: map,
            position: new kakao.maps.LatLng({place['y']}, {place['x']})
        }});
        kakao.maps.event.addListener(marker, 'click', function() {{
            alert('이름: {place['place_name']}\\n주소: {place['road_address_name']}\\n전화번호: {place['phone']}');
        }});
        """

    return f"""
    <div id="map" style="width:100%;height:400px;"></div>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}"></script>
    <script>
        var container = document.getElementById('map');
        var options = {{
            center: new kakao.maps.LatLng({lat}, {lon}),
            level: 3
        }};
        var map = new kakao.maps.Map(container, options);
        {places_script}
    </script>
    """

# Kakao API를 사용하여 주소를 좌표로 변환
def fetch_coordinates(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        documents = response.json().get('documents', [])
        if documents:
            return float(documents[0]['y']), float(documents[0]['x'])
        else:
            st.error("주소를 찾을 수 없습니다.")
    else:
        st.error(f"지오코딩 API 요청 실패: {response.status_code}, 응답: {response.text}")
    return None, None

# Kakao API를 사용하여 주변 음식점 검색
def fetch_restaurants(lat, lon):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {
        "query": "음식점",
        "x": lon,
        "y": lat,
        "radius": 2000  # 반경 2km 내 검색
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('documents', [])
    else:
        st.error(f"음식점 정보 API 요청 실패: {response.status_code}, 응답: {response.text}")
        return []

# Streamlit 앱
st.title("Kakao 지도 API와 Streamlit")

# 주소 입력 받기
address = st.text_input("주소를 입력하세요:")

if st.button("음식점 검색"):
    lat, lon = fetch_coordinates(address)
    
    if lat is not None and lon is not None:
        restaurants = fetch_restaurants(lat, lon)
        
        if restaurants:
            map_html = kakao_map_html(lat, lon, restaurants)
            html(map_html, height=400)
        else:
            st.write("음식점을 찾을 수 없습니다.")