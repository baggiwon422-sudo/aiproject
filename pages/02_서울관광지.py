import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울 TOP 10 관광지 & 1박 2일 일정 플래너",
    page_icon="🗽",
    layout="wide"
)

# 2. 세션 상태(Session State) 초기화 (1박 2일 일정 저장용)
if "day1_plan" not in st.session_state:
    st.session_state["day1_plan"] = ["경복궁", "북촌한옥마을", "인사동", "N서울타워 (남산타워)"]

if "day2_plan" not in st.session_state:
    st.session_state["day2_plan"] = ["명동 쇼핑가", "동대문디자인플라자 (DDP)", "홍대 거리", "반포 한강공원"]

st.title("🗽 외국인 인기 서울 명소 TOP 10 & 1박 2일 추천 일정")
st.write("지도 위의 마커를 클릭하여 장소 정보를 확인하고, 나만의 1박 2일 여행 일정을 완성해 보세요!")

# 3. 관광지 데이터 (위도, 경도, 설명 포함)
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
        "desc": "곡선미가 돋보이는
    
