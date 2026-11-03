import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="외국인 인기 서울 관광지 TOP 10",
    page_icon="🗽",
    layout="wide"
)

st.title("🗽 외국인 관광객이 사랑하는 서울 명소 TOP 10")
st.write("지도 위의 마커를 클릭하여 각 관광지의 상세 정보를 확인해보세요!")

# 2. 관광지 데이터 (위도, 경도, 설명 포함)
tourist_spots = [
    {
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "desc": "조선시대 대표 궁궐로 한복 체험과 왕궁 수문장 교대식이 외국인 관광객에게 큰 인기를 끌고 있습니다."
    },
    {
        "name": "N서울타워 (남산타워)",
        "lat": 37.5512,
        "lon": 126.9882,
        "desc": "서울 도심 전경을 한눈에 볼 수 있는 랜드마크로, 케이블카와 사랑의 자물쇠가 명물입니다."
    },
    {
        "name": "명동 쇼핑가",
        "lat": 37.5636,
        "lon": 126.9822,
        "desc": "K-뷰티 화장품 쇼핑과 다양한 한국 길거리 음식을 한곳에서 맛볼 수 있는 필수 관광 코스입니다."
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9837,
        "desc": "전통 기와집 골목길이 보존된 곳으로, 한국 고유의 건축 감성을 사진으로 남기기 좋은 장소입니다."
    },
    {
        "name": "인사동",
        "lat": 37.5744,
        "lon": 126.9860,
        "desc": "전통 공예품, 찻집, 갤러리가 모여 있어 한국의 문화와 예술을 다양하게 체험할 수 있습니다."
    },
    {
        "name": "홍대 거리",
        "lat": 37.5563,
        "lon": 126.9237,
        "desc": "버스킹, 인디 음악, 개성 넘치는 카페와 클럽 문화가 어우러진 스트리트 컬처 중심지입니다."
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.5665,
        "lon": 126.1007,
        "desc": "곡선미가 돋보이는 곡선형 미래적 건축물로 패션, 디자인 전시 및 야경으로 유명합니다."
    },
    {
        "name": "이태원",
        "lat": 37.5345,
        "lon": 126.9946,
        "desc": "다국적 음식점과 다채로운 문화가 조화를 이루는 서울의 대표적인 글로벌 핫플레이스입니다."
    },
    {
        "name": "롯데월드타워 & 잠실",
        "lat": 37.5126,
        "lon": 127.1025,
        "desc": "123층 전망대 '서울스카이'에서 남한산성과 서울 시내 전체를 내려다보는 스릴을 선사합니다."
    },
    {
        "name": "반포 한강공원",
        "lat": 37.5104,
        "lon": 126.9960,
        "desc": "달빛무지개분수와 함께 한강변 라면, 피크닉 치맥 문화 등 현지인 감성을 그대로 경험할 수 있습니다."
    }
]

# DataFrame 변환
df = pd.DataFrame(tourist_spots)

# 3. Folium 지도 생성 (서울 시청 중심 coordinates)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="OpenStreetMap")

# 마커 추가
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(f"<b>{row['name']}</b>", max_width=200),
        tooltip=row['name'],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 4. 지도 화면 출력
st.subheader("📍 서울 관광지 지도")
st_folium(m, width="100%", height=500)

# 5. 지도 하단 관광지 목록 및 간략 설명
st.markdown("---")
st.subheader("📜 TOP 10 관광지 명소 설명")

# 2열 카드로 깔끔하게 구성
col1, col2 = st.columns(2)

for i, spot in enumerate(tourist_spots):
    target_col = col1 if i % 2 == 0 else col2
    with target_col:
        with st.expander(f"{i+1}. {spot['name']}", expanded=True):
            st.write(spot['desc'])
