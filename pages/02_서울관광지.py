import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울 TOP 10 관광지 & 맛집/교통 1박 2일 플래너",
    page_icon="🗽",
    layout="wide"
)

# 2. 세션 상태(Session State) 초기화 (1박 2일 일정 저장용)
if "day1_plan" not in st.session_state:
    st.session_state["day1_plan"] = ["경복궁", "북촌한옥마을", "인사동", "N서울타워 (남산타워)"]

if "day2_plan" not in st.session_state:
    st.session_state["day2_plan"] = ["명동 쇼핑가", "동대문디자인플라자 (DDP)", "홍대 거리", "반포 한강공원"]

st.title("🗽 외국인 인기 서울 명소 TOP 10 & 1박 2일 맞춤 플래너")
st.write("지도 위의 마커를 클릭해 상세 정보를 확인하고, 맛집과 교통편이 포함된 완벽한 일정을 확인해 보세요!")

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
        "lon": 126.9785,
        "desc": "곡선미가 돋보이는 미래적 건축물로 패션, 디자인 전시 및 야경으로 유명합니다."
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

df = pd.DataFrame(tourist_spots)

# 4. Folium 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="OpenStreetMap")

# 마커 추가
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(f"<b>{row['name']}</b>", max_width=200),
        tooltip=row['name'],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 5. 지도 화면 출력
st.subheader("📍 서울 관광지 지도 (마커 클릭 시 상세설명 표출)")
map_data = st_folium(m, width="100%", height=500)

# 6. 마커 클릭 이벤트에 따른 정보 표출
st.markdown("---")
clicked_spot_name = map_data.get("last_object_clicked_tooltip")

if clicked_spot_name:
    selected_info = df[df['name'] == clicked_spot_name]
    if not selected_info.empty:
        spot_data = selected_info.iloc[0]
        st.subheader(f"🔍 선택한 명소: {spot_data['name']}")
        st.info(spot_data['desc'])
        
        # 일정에 추가할 수 있는 버튼 제공
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"➕ '{spot_data['name']}' -> Day 1 일정에 추가"):
                if spot_data['name'] not in st.session_state["day1_plan"]:
                    st.session_state["day1_plan"].append(spot_data['name'])
                    st.success("Day 1에 추가되었습니다!")
        with btn_col2:
            if st.button(f"➕ '{spot_data['name']}' -> Day 2 일정에 추가"):
                if spot_data['name'] not in st.session_state["day2_plan"]:
                    st.session_state["day2_plan"].append(spot_data['name'])
                    st.success("Day 2에 추가되었습니다!")
else:
    st.info("💡 **팁:** 지도 위의 빨간 마커를 클릭하면 해당 장소의 설명과 1박 2일 일정 추가 버튼이 나타납니다.")

# 7. 지도 하단 1박 2일 추천 코스 + 맛집 및 교통편 가이드
st.markdown("---")
st.subheader("🗓️ 맛집 & 교통 가이드가 포함된 1박 2일 추천 여행 일정표")

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("### 🟢 **DAY 1: 전통 문화 & 대표 랜드마크**")
    st.caption("고궁 탐방부터 서울 전체 야경 감상까지")
    
    for idx, name in enumerate(st.session_state["day1_plan"]):
        spot_match = df[df['name'] == name]
        desc_text = spot_match.iloc[0]['desc'] if not spot_match.empty else ""
        with st.expander(f"📍 {idx + 1}단계: {name}", expanded=True):
            st.write(desc_text)
            
    # Day 1 맛집 및 교통 정보 추가
    st.markdown("---")
    st.markdown("#### 🍴 Day 1 추천 맛집 & 교통편")
    st.info(
        "**🚇 교통편 가이드:**\n"
        "- 공항철도 및 지하철 3호선(안국역, 경복궁역) 활용 추천 (T-money 카드 필수)\n\n"
        "**🍜 추천 맛집:**\n"
        "- **토속촌 삼계탕 (경복궁 인근):** 외국인 관광객에게 가장 유명한 보양식 맛집\n"
        "- **명동교자 (명동 인근):** 미슐랭 가이드에 오른 칼국수와 마늘 김치 맛집"
    )
            
    if st.button("🗑️ Day 1 일정 초기화"):
        st.session_state["day1_plan"] = []
        st.rerun()

with col_d2:
    st.markdown("### 🔵 **DAY 2: K-컬처, 쇼핑 & 한강 힐링**")
    st.caption("트렌디한 거리 탐방과 한강 야경 피크닉")
    
    for idx, name in enumerate(st.session_state["day2_plan"]):
        spot_match = df[df['name'] == name]
        desc_text = spot_match.iloc[0]['desc'] if not spot_match.empty else ""
        with st.expander(f"📍 {idx + 1}단계: {name}", expanded=True):
            st.write(desc_text)
            
    # Day 2 맛집 및 교통 정보 추가
    st.markdown("---")
    st.markdown("#### 🍴 Day 2 추천 맛집 & 교통편")
    st.info(
        "**🚇 교통편 가이드:**\n"
        "- 지하철 2호선(홍대입구역, 잠실역) 및 9호선 라인 중심 이동 편리\n\n"
        "**🍜 추천 맛집:**\n"
        "- **광장시장 (동대문/종로 인근):** 빈대떡, 마약김밥 등 다양한 길거리 K-푸드 체험\n"
        "- **한강 편의점 라면 & 배달 치킨 (반포 한강공원):** 현지인처럼 즐기는 한강 야외 피크닉 낭만"
    )
            
    if st.button("🗑️ Day 2 일정 초기화"):
        st.session_state["day2_plan"] = []
        st.rerun()
