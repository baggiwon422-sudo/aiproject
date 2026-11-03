import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="부산 TOP 10 관광지 & 맛집/교통 1박 2일 플래너",
    page_icon="🌊",
    layout="wide"
)

# 2. 세션 상태(Session State) 초기화
if "day1_plan" not in st.session_state:
    st.session_state["day1_plan"] = [
        "해운대 해수욕장",
        "해운대 블루라인파크 (미포철길)",
        "광안리 해수욕장 (광안대교 야경)",
        "센텀시티 & 신세계백화점"
    ]

if "day2_plan" not in st.session_state:
    st.session_state["day2_plan"] = [
        "감천문화마을",
        "자갈치시장",
        "BIFF 광장",
        "용두산공원 (부산타워)"
    ]

st.title("🌊 외국인 관광객이 사랑하는 부산 명소 TOP 10 & 1박 2일 맞춤 플래너")
st.write("지도 위의 마커를 클릭해 상세 정보를 확인하고, 맛집과 교통편이 포함된 완벽한 부산 여행 일정을 완성해 보세요!")

# 3. 부산 주요 관광지 데이터
tourist_spots = [
    {
        "name": "해운대 해수욕장",
        "lat": 35.1587,
        "lon": 129.1603,
        "desc": "한국을 대표하는 최고 해변 명소로 넓은 백사장과 현대적인 고층 빌딩 스카이라인이 어우러진 해변입니다."
    },
    {
        "name": "광안리 해수욕장 (광안대교 야경)",
        "lat": 35.1532,
        "lon": 129.1189,
        "desc": "밤이 되면 화려한 조명이 빛나는 광안대교 야경과 감성적인 오션뷰 카페거리로 유명합니다."
    },
    {
        "name": "감천문화마을",
        "lat": 35.0975,
        "lon": 129.0107,
        "desc": "알록달록한 계단식 집들과 미로 같은 골목길, 그리고 아름다운 벽화가 가득한 대표 명소입니다."
    },
    {
        "name": "해운대 블루라인파크 (미포철길)",
        "lat": 35.1605,
        "lon": 129.1711,
        "desc": "해변을 따라 달리는 해변열차와 스카이캡슐을 타고 동해 바다를 만끽할 수 있는 곳입니다."
    },
    {
        "name": "자갈치시장",
        "lat": 35.0977,
        "lon": 129.0305,
        "desc": "한국 최대 규모의 수산시장으로, 싱싱한 해산물을 직접 고르고 맛볼 수 있는 활기찬 명소입니다."
    },
    {
        "name": "태종대",
        "lat": 35.0519,
        "lon": 129.0863,
        "desc": "기암절벽과 탁 트인 푸른 바다가 빚어내는 장엄한 절경을 감상할 수 있는 영도의 대표 자연공원입니다."
    },
    {
        "name": "BIFF 광장",
        "lat": 35.0988,
        "lon": 129.0274,
        "desc": "부산국제영화제의 발상지로, 쇼핑과 함께 명물인 씨앗호떡 등 다양한 길거리 음식을 즐길 수 있습니다."
    },
    {
        "name": "용두산공원 (부산타워)",
        "lat": 35.1006,
        "lon": 129.0330,
        "desc": "도심 속 언덕에 위치해 부산항과 시내를 한눈에 조망할 수 있는 부산의 상징적인 공원입니다."
    },
    {
        "name": "해동용궁사",
        "lat": 35.1916,
        "lon": 129.2230,
        "desc": "파도치는 바닷가 바로 바위에 지어진 독특하고 아름다운 해상 사찰입니다."
    },
    {
        "name": "센텀시티 & 신세계백화점",
        "lat": 35.1691,
        "lon": 129.1293,
        "desc": "세계 최대 규모의 백화점으로 쇼핑, 스파(스파랜드), 엔터테인먼트를 한곳에서 즐길 수 있습니다."
    }
]

df = pd.DataFrame(tourist_spots)

# 4. Folium 지도 생성
m = folium.Map(location=[35.1540, 129.0900], zoom_start=11, tiles="OpenStreetMap")

for idx, row in df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(f"<b>{row['name']}</b>", max_width=200),
        tooltip=row["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# 5. 지도 화면 출력
st.subheader("📍 부산 TOP 10 관광지 지도 (마커 클릭 시 상세설명 표출)")
map_data = st_folium(m, width="100%", height=500)

# 6. 마커 클릭 이벤트 처리
st.markdown("---")
clicked_spot_name = map_data.get("last_object_clicked_tooltip")

if clicked_spot_name:
    selected_info = df[df["name"] == clicked_spot_name]
    if not selected_info.empty:
        spot_data = selected_info.iloc[0]
        st.subheader(f"🔍 선택한 부산 명소: {spot_data['name']}")
        st.info(spot_data["desc"])
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"➕ '{spot_data['name']}' -> Day 1 일정 추가"):
                if spot_data["name"] not in st.session_state["day1_plan"]:
                    st.session_state["day1_plan"].append(spot_data["name"])
                    st.success("Day 1에 추가되었습니다!")
        with btn_col2:
            if st.button(f"➕ '{spot_data['name']}' -> Day 2 일정 추가"):
                if spot_data["name"] not in st.session_state["day2_plan"]:
                    st.session_state["day2_plan"].append(spot_data["name"])
                    st.success("Day 2에 추가되었습니다!")
else:
    st.info("💡 **팁:** 지도 위의 파란색 마커를 클릭하면 부산 명소의 상세 설명과 일정 추가 버튼이 나옵니다.")

# 7. 1박 2일 추천 코스 + 맛집 및 교통 정보
st.markdown("---")
st.subheader("🗓️ 맛집 & 교통 가이드가 포함된 1박 2일 부산 여행 일정표")

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("### 🟢 **DAY 1: 해운대 & 동부산 오션뷰 코스**")
    st.caption("바다 전망, 테마 열차 및 야경 감상")
    
    for idx, name in enumerate(st.session_state["day1_plan"]):
        spot_match = df[df["name"] == name]
        desc_text = spot_match.iloc[0]["desc"] if not spot_match.empty else ""
        with st.expander(f"📍 {idx + 1}단계: {name}", expanded=True):
            st.write(desc_text)
            
    st.markdown("---")
    st.markdown("#### 🍴 Day 1 추천 맛집 & 교통편")
    st.info("🚇 **교통편:** 부산 지하철 2호선(해운대역, 센텀시티역) 이용 및 교통카드 추천\n\n🍜 **추천 맛집:** 해운대 가야밀면(밀면 명가), 광안리 민락수변공원 횟집(야경 오션뷰)")
            
    if st.button("🗑️ Day 1 일정 초기화"):
        st.session_state["day1_plan"] = []
        st.rerun()

with col_d2:
    st.markdown("### 🔵 **DAY 2: 원도심 문화 & 로컬 미식 코스**")
    st.caption("알록달록한 아기자기한 마을과 활기찬 수산시장")
    
    for idx, name in enumerate(st.session_state["day2_plan"]):
        spot_match = df[df["name"] == name]
        desc_text = spot_match.iloc[0]["desc"] if not spot_match.empty else ""
        with st.expander(f"📍 {idx + 1}단계: {name}", expanded=True):
            st.write(desc_text)
            
    st.markdown("---")
    st.markdown("#### 🍴 Day 2 추천 맛집 & 교통편")
    st.info("🚇 **교통편:** 부산 지하철 1호선(자갈치역, 남포역, 토성역) 이용\n\n🍜 **추천 맛집:** 자갈치 신동아시장 회센터(싱싱한 활어회), 남포동 부평깡통시장(씨앗호떡, 비빔당면)")
            
    if st.button("🗑️ Day 2 일정 초기화"):
        st.session_state["day2_plan"] = []
        st.
