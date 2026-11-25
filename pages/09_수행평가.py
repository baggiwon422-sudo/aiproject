import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# 페이지 설정
st.set_page_config(page_title="한국인 인기 해외여행 동선 플래너", page_icon="✈️", layout="wide")

# ---------------------------------------------------------
# 1. 여행지 내장 데이터 (별도 지도/CSV 파일 없이 바로 작동)
# ---------------------------------------------------------
TRAVEL_DATA = {
    "1위. 일본 (오사카 · 도쿄 · 후쿠오카)": {
        "summary": "근거리 및 쇼핑·미식 천국으로 한국인 해외여행 부동의 1위 국가입니다.",
        "cities": {
            "오사카": [
                {
                    "name": "도톤보리 & 글리코상",
                    "lat": 34.6687, "lon": 135.5013,
                    "desc": "오사카 대표 번화가이자 길거리 음식과 야경의 중심지",
                    "restaurants": ["이치란 라멘 도톤보리점 (돈코츠 라멘)", "치보 오코노미야끼", "앗치치혼포 (타코야끼)"],
                    "souvenirs": ["돈키호테 도톤보리점 (의약품·곤약젤리)", "마츠모토 키요시 (드럭스토어)"]
                },
                {
                    "name": "오사카성 천수각",
                    "lat": 34.6873, "lon": 135.5262,
                    "desc": "일본 3대 명성 중 하나로 성곽 산책과 시내 전망이 인기",
                    "restaurants": ["도쿠마사 모리노미야점 (카레우동)", "오사카성 공원 롯코산 말차 아이스크림"],
                    "souvenirs": ["천수각 1층 공식 기념품샵", "미라이자 오사카성 (말차 쿠키·자석)"]
                },
                {
                    "name": "유니버설 스튜디오 재팬 (USJ)",
                    "lat": 34.6654, "lon": 135.4323,
                    "desc": "슈퍼 닌텐도 월드와 해리포터 테마존이 있는 대형 테마파크",
                    "restaurants": ["키노피오 카페 (파크 내 버섯 피자)", "레드 랍스터 시티워크점"],
                    "souvenirs": ["유니버설 스튜디오 스토어 (마리오·미니언즈 굿즈)", "점프 샵"]
                },
                {
                    "name": "우메다 공중정원",
                    "lat": 34.7059, "lon": 135.4904,
                    "desc": "360도 파노라마로 오사카 도심을 내려다보는 야경 명소",
                    "restaurants": ["키지 우메다 스카이빌딩점 (오코노미야끼)", "하브스 다이마루점 (밀크레이프)"],
                    "souvenirs": ["한큐 백화점 식품관 (바통도르·손수건)", "로프트(LOFT) 우메다점"]
                },
                {
                    "name": "구로몬 시장",
                    "lat": 34.6655, "lon": 135.5063,
                    "desc": "신선한 해산물, 와규 꼬치, 과일을 즉석에서 즐기는 재래시장",
                    "restaurants": ["마구로야 쿠로긴 (참치 덮밥)", "구로몬 산페이 (성게알·대게 구이)"],
                    "souvenirs": ["시장 내 일본 전통 찻집 (녹차·말차)", "화과자 전문점"]
                }
            ],
            "도쿄": [
                {
                    "name": "센소지 (아사쿠사)",
                    "lat": 35.7148, "lon": 139.7967,
                    "desc": "도쿄에서 가장 오래된 사찰과 나카미세 전통 기념품 거리",
                    "restaurants": ["아사쿠사 규카츠 (소고기 커틀릿)", "소메타로 (전통 오코노미야끼)"],
                    "souvenirs": ["나카미세 거리 (닌교야키·부채·기모노 소품)", "아사쿠사 실크 푸딩"]
                },
                {
                    "name": "시부야 스카이 & 스크램블 교차로",
                    "lat": 35.6580, "lon": 139.7016,
                    "desc": "도쿄 전경과 후지산 뷰까지 감상할 수 있는 루프탑 전망대",
                    "restaurants": ["미도리 스시 시부야점 (초밥)", "츠루동탄 (세숫대야 우동)"],
                    "souvenirs": ["시부야 스크램블 스퀘어 1층 디저트관", "메가 돈키호테 시부야 본점"]
                },
                {
                    "name": "신주쿠 오모이데 요코초",
                    "lat": 35.6938, "lon": 139.7034,
                    "desc": "레트로 감성의 꼬치구이 골목과 대형 백화점 쇼핑 구역",
                    "restaurants": ["후운지 (진한 츠케멘)", "오모이데 요코초 야키토리 골목"],
                    "souvenirs": ["이세탄 백화점 신주쿠점 (디저트·손수건)", "빅카메라 신주쿠점"]
                },
                {
                    "name": "도쿄 타워 & 롯폰기 힐즈",
                    "lat": 35.6586, "lon": 139.7454,
                    "desc": "도쿄를 상징하는 붉은 철탑과 세련된 미술관·복합몰",
                    "restaurants": ["아후리 롯폰기점 (유자 시오 라멘)", "우카이 테이 (두부 요리)"],
                    "souvenirs": ["도쿄 타워 풋타운 3층 공식 샵", "츠타야 서점 롯폰기"]
                }
            ]
        }
    },
    "2위. 베트남 (다낭 · 호이안)": {
        "summary": "가성비 높은 휴양, 마사지, 한국인 입맛에 잘 맞는 로컬 음식이 강점입니다.",
        "cities": {
            "다낭 & 호이안": [
                {
                    "name": "미케 비치",
                    "lat": 16.0544, "lon": 108.2474,
                    "desc": "끝없이 펼쳐진 고운 백사장과 오션뷰 카페 거리가 있는 대표 해변",
                    "restaurants": ["목식당 (가리비·새우 해산물 요리)", "에스코 비치 바"],
                    "souvenirs": ["다낭 롯데마트 (G7 커피·망고 젤리·캐슈넛)", "엘스토어 (코코넛 과자)"]
                },
                {
                    "name": "바나힐 (골든브릿지)",
                    "lat": 15.9977, "lon": 107.9881,
                    "desc": "거대한 손 모양 다리와 유럽풍 테마마을이 있는 산상 테마파크",
                    "restaurants": ["바나힐 비어 플라자 뷔페", "브라세리 레스토랑"],
                    "souvenirs": ["바나힐 정상 기념품샵 (수제 초콜릿·테마 굿즈)"]
                },
                {
                    "name": "한시장 & 다낭 대성당",
                    "lat": 16.0680, "lon": 108.2248,
                    "desc": "아오자이 맞춤 제작, 라탄백 쇼핑, 핑크 성당 기념사진 필수 코스",
                    "restaurants": ["마담란 (반쎄오·분짜)", "콩카페 1호점 (코코넛 스무디 커피)"],
                    "souvenirs": ["한시장 1~2층 (라탄백·아오자이·건망고)", "트리플 스윗 (다낭 자석·소품)"]
                },
                {
                    "name": "호이안 올드타운",
                    "lat": 15.8774, "lon": 108.3261,
                    "desc": "형형색색의 연등 야경과 투본강 소원배 체험으로 유명한 고도시",
                    "restaurants": ["모닝글로리 (화이트로즈·까오러우)", "반미 프엉 (베트남 샌드위치)"],
                    "souvenirs": ["호이안 야시장 (수제 연등·가죽 공예품)", "리칭 아웃 찻집"]
                }
            ]
        }
    },
    "3위. 중국 (상하이)": {
        "summary": "무비자 정책 이후 주말 단기 여행과 야경·미식 코스로 인기가 급상승했습니다.",
        "cities": {
            "상하이": [
                {
                    "name": "와이탄 & 동방명주 전망",
                    "lat": 31.2397, "lon": 121.4998,
                    "desc": "유럽풍 근대 건축물과 화려한 마천루 야경을 한눈에 담는 대표 명소",
                    "restaurants": ["와이포지아 (동파육·마파두부)", "하이드라 상하이 (루프탑 레스토랑)"],
                    "souvenirs": ["난징동루 제일식품상점 (나비파이·토끼사탕)", "상하이 기념품 플래그십 스토어"]
                },
                {
                    "name": "예원 (위위안) & 옛거리",
                    "lat": 31.2272, "lon": 121.4921,
                    "desc": "명나라 시대 전통 정원과 화려한 야경, 육즙 샤오롱바오의 본고장",
                    "restaurants": ["난샹만두점 (샤오롱바오)", "녹파랑 (상하이 전통 요리)"],
                    "souvenirs": ["예원 상점가 (중국 전통 차·실크 부채·배즙 캔디)"]
                },
                {
                    "name": "신천지 & 대한민국 임시정부 청사",
                    "lat": 31.2198, "lon": 121.4754,
                    "desc": "역사적 의미가 깊은 임시정부 청사와 세련된 노천 카페 거리",
                    "restaurants": ["딘타이펑 신천지점", "점도덕 (홍미창펀·딤섬)"],
                    "souvenirs": ["티엔즈팡 공예품 골목 (수제 차·기념 자석)", "신천지 편집샵"]
                },
                {
                    "name": "상하이 디즈니랜드",
                    "lat": 31.1440, "lon": 121.6570,
                    "desc": "아시아 최대 규모 디즈니 파크 및 주토피아 테마 구역",
                    "restaurants": ["로열 뱅큇 홀", "디즈니타운 치즈케이크 팩토리"],
                    "souvenirs": ["월드 오브 디즈니 스토어 (주토피아·리나벨 굿즈)"]
                }
            ]
        }
    },
    "4위. 미국 (하와이)": {
        "summary": "가족 휴양, 신혼여행, 쇼핑, 해양 액티비티를 모두 즐길 수 있는 휴양지입니다.",
        "cities": {
            "하와이 (오아후)": [
                {
                    "name": "와이키키 해변 & 칼라카우아 거리",
                    "lat": 21.2766, "lon": -157.8278,
                    "desc": "서핑과 일몰 감상, 명품 쇼핑과 레스토랑이 모인 하와이의 중심",
                    "restaurants": ["듀크스 와이키키 (훌라파이·스테이크)", "마루가메 우동 와이키키"],
                    "souvenirs": ["ABC 스토어 (마카다미아 초콜릿·하와이안 셔츠)", "호놀룰루 쿠키 컴퍼니"]
                },
                {
                    "name": "다이아몬드 헤드 분화구",
                    "lat": 21.2620, "lon": -157.8054,
                    "desc": "와이키키 전경과 태평양을 내려다보는 대표 트레킹 명소",
                    "restaurants": ["파이어니어 살룬 (플레이트 런치)", "보가스 카페 (아사이볼)"],
                    "souvenirs": ["KCC 파머스 마켓 (하와이산 꿀·코나 커피)"]
                },
                {
                    "name": "알라모아나 센터",
                    "lat": 21.2911, "lon": -157.8435,
                    "desc": "세계 최대 규모의 야외 쇼핑몰",
                    "restaurants": ["치즈케이크 팩토리", "부바 검프 슈림프"],
                    "souvenirs": ["빅 아일랜드 캔디즈", "타겟(Target) 알라모아나점 (스낵·선크림)"]
                }
            ]
        }
    },
    "5위. 태국 (방콕)": {
        "summary": "화려한 왕궁 사원, 5성급 호캉스, 야시장 먹거리가 조화로운 동남아 대표 도시입니다.",
        "cities": {
            "방콕": [
                {
                    "name": "왕궁 & 왓 아룬 (새벽사원)",
                    "lat": 13.7437, "lon": 100.4889,
                    "desc": "짜오프라야 강변의 황금빛 왕궁과 야경이 아름다운 대표 사원",
                    "restaurants": ["촘 아룬 (왓 아룬 뷰 레스토랑)", "팁싸마이 (오리지널 팟타이)"],
                    "souvenirs": ["타티엔 선착장 주변 코끼리 바지·야돔 상점"]
                },
                {
                    "name": "아이콘시암 (ICONSIAM)",
                    "lat": 13.7267, "lon": 100.5105,
                    "desc": "실내 수상시장 ‘쑥시암’과 명품관이 결합된 초대형 복합몰",
                    "restaurants": ["쑥시암 푸드코트 (망고밥·국수)", "노스이스트 (땡모반·푸팟퐁커리)"],
                    "souvenirs": ["나라야(NaRaYa) 리본백 매장", "고메 마켓 (건망고·벤또·태국 밀크티)"]
                },
                {
                    "name": "쩟페어 야시장 (Jodd Fairs)",
                    "lat": 13.7567, "lon": 100.5663,
                    "desc": "랭쎕(등뼈찜)과 생과일 주스 등 젊은 감성의 먹거리 야시장",
                    "restaurants": ["디아오 마에 클롱 (랭쎕)", "야시장 내 생과일 스무디 가판대"],
                    "souvenirs": ["야시장 수공예 비누·여권 케이스 샵", "빅씨(Big C) 마트 라차담리점"]
                }
            ]
        }
    }
}

# ---------------------------------------------------------
# 2. 거리 계산 및 최단 동선 정렬 알고리즘
# ---------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def optimize_route(selected_places):
    if len(selected_places) <= 1:
        return selected_places, 0.0
    
    # 첫 번째 선택한 장소를 출발점으로 고정 후 가장 가까운 다음 장소로 순차 연결
    unvisited = selected_places[1:].copy()
    route = [selected_places[0]]
    total_dist = 0.0
    
    while unvisited:
        current = route[-1]
        nearest = min(
            unvisited,
            key=lambda p: haversine(current["lat"], current["lon"], p["lat"], p["lon"])
        )
        total_dist += haversine(current["lat"], current["lon"], nearest["lat"], nearest["lon"])
        route.append(nearest)
        unvisited.remove(nearest)
        
    return route, round(total_dist, 2)

# ---------------------------------------------------------
# 3. 화면 구성 (UI)
# ---------------------------------------------------------
st.title("✈️ 한국인 인기 해외여행지 맞춤 동선 플래너")
st.markdown("나라와 도시를 선택하고 가고 싶은 명소를 고르면 **최적 이동 동선, 추천 맛집, 기념품 샵, 지도 경로**를 자동으로 생성합니다.")

# 사이드바: 국가, 도시, 관광지 선택
with st.sidebar:
    st.header("🌍 1. 여행지 선택")
    selected_country = st.selectbox("방문할 국가 선택", list(TRAVEL_DATA.keys()))
    country_info = TRAVEL_DATA[selected_country]
    st.info(country_info["summary"])
    
    selected_city = st.selectbox("세부 도시 선택", list(country_info["cities"].keys()))
    places = country_info["cities"][selected_city]
    
    st.divider()
    st.header("📍 2. 관광지 선택")
    st.caption("첫 번째로 선택한 장소가 출발 기준점이 됩니다.")
    
    place_names = [p["name"] for p in places]
    selected_names = st.multiselect(
        "동선에 넣을 관광지를 선택하세요:",
        options=place_names,
        default=place_names[:3]  # 기본 3곳 선택 상태
    )

# 선택된 장소 객체 추출
place_dict = {p["name"]: p for p in places}
selected_places = [place_dict[name] for name in selected_names]

# 메인 화면: 좌측(동선·맛집·기념품) / 우측(지도)
col1, col2 = st.columns([1.15, 1])

with col1:
    st.subheader(f"📌 {selected_city} 추천 동선 및 맛집·기념품")
    
    if not selected_places:
        st.warning("왼쪽 사이드바에서 방문할 관광지를 1곳 이상 선택해 주세요!")
    else:
        optimized_route, total_km = optimize_route(selected_places)
        
        # 동선 요약 표시
        route_arrow = " ➡️ ".join([f"{idx+1}. {p['name']}" for idx, p in enumerate(optimized_route)])
        st.success(f"**추천 이동 순서 (총 직선 이동거리 약 {total_km} km)**\n\n{route_arrow}")
        
        # 코스별 상세 카드
        for idx, spot in enumerate(optimized_route):
            with st.expander(f"🚩 {idx+1}코스: {spot['name']}", expanded=True):
                st.write(f"**특징:** {spot['desc']}")
                
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    st.markdown("**🍽️ 근처 인기 맛집**")
                    for r in spot["restaurants"]:
                        st.markdown(f"- {r}")
                with sub_col2:
                    st.markdown("**🛍️ 가볼만한 기념품·쇼핑 샵**")
                    for s in spot["souvenirs"]:
                        st.markdown(f"- {s}")

with col2:
    st.subheader("🗺️ 한눈에 보는 동선 지도")
    if selected_places:
        optimized_route, _ = optimize_route(selected_places)
        avg_lat = sum(p["lat"] for p in optimized_route) / len(optimized_route)
        avg_lon = sum(p["lon"] for p in optimized_route) / len(optimized_route)
        
        # OpenStreetMap 기본 타일 사용 (API 키 불필요)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="OpenStreetMap")
        coords = []
        
        for idx, spot in enumerate(optimized_route):
            coords.append([spot["lat"], spot["lon"]])
            popup_html = f"""
            <div style="width:200px;">
                <b>{idx+1}코스: {spot['name']}</b><br>
                <small>{spot['desc']}</small><br><br>
                <b>추천 맛집:</b> {spot['restaurants'][0]}<br>
                <b>기념품:</b> {spot['souvenirs'][0]}
            </div>
            """
            folium.Marker(
                location=[spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{idx+1}. {spot['name']}",
                icon=folium.Icon(color="red" if idx == 0 else "blue", icon="info-sign")
            ).add_to(m)
            
        if len(coords) > 1:
            folium.PolyLine(coords, color="#FF4B4B", weight=4, opacity=0.8).add_to(m)
            
        st_folium(m, width=600, height=520, returned_objects=[])
    else:
        st.info("관광지를 선택하면 지도에 핀과 이동 경로가 표시됩니다.")
