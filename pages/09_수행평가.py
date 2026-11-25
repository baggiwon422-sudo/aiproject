import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="한국인 인기 해외여행 10개국 동선 & 예산 플래너", page_icon="✈️", layout="wide")

# ---------------------------------------------------------
# 1. 10개국 종합 여행지, 환율, 예산 및 기념품 데이터베이스 (원화 기준)
# ---------------------------------------------------------
TRAVEL_DATA = {
    "1위. 일본 (오사카 · 도쿄 · 후쿠오카 · 삿포로)": {
        "summary": "근거리 접근성과 미식·쇼핑·온천이 결합된 한국인 선호 1위 국가입니다.",
        "currency_name": "엔 (JPY)",
        "rate": 8.42,  # 1엔당 원화
        "recommended_exchange": 50000, # 추천 환전액 (현지 통화 기준)
        "est_budget_text": "1인당 약 80만 원 ~ 150만 원 (3박 4일 기준)",
        "cities": {
            "오사카": [
                {"name": "도톤보리 & 글리코상", "lat": 34.6687, "lon": 135.5013, "desc": "오사카 대표 번화가이자 길거리 음식 야경 중심지", "cost": 0, "restaurants": ["이치란 라멘", "치보 오코노미야끼"], "souvenirs": ["돈키호테 곤약젤리"]},
                {"name": "오사카성 천수각", "lat": 34.6873, "lon": 135.5262, "desc": "일본 3대 명성 중 하나", "cost": 6000, "restaurants": ["도쿠마사 카레우동"], "souvenirs": ["말차 과자"]},
                {"name": "유니버설 스튜디오 재팬 (USJ)", "lat": 34.6654, "lon": 135.4323, "desc": "대형 테마파크", "cost": 105000, "restaurants": ["키노피오 카페"], "souvenirs": ["마리오 굿즈"]},
                {"name": "우메다 공중정원", "lat": 34.7059, "lon": 135.4904, "desc": "오사카 도심 야경 명소", "cost": 18000, "restaurants": ["하브스 케이크"], "souvenirs": ["한큐백화점 과자"]}
            ],
            "도쿄": [
                {"name": "센소지 (아사쿠사)", "lat": 35.7148, "lon": 139.7967, "desc": "도쿄 가장 오래된 사찰", "cost": 0, "restaurants": ["아사쿠사 규카츠"], "souvenirs": ["닌교야키"]},
                {"name": "시부야 스카이", "lat": 35.6580, "lon": 139.7016, "desc": "루프탑 전망대", "cost": 22000, "restaurants": ["미도리 스시"], "souvenirs": ["스크램블 스퀘어 굿즈"]}
            ],
            "후쿠오카": [
                {"name": "캐널시티 하카타", "lat": 33.5898, "lon": 130.4108, "desc": "복합 쇼핑몰 및 분수쇼", "cost": 0, "restaurants": ["모츠나베 오오야마"], "souvenirs": ["명란젓"]}
            ],
            "삿포로": [
                {"name": "오도리 공원", "lat": 43.0611, "lon": 141.3564, "desc": "삿포로 도심 공원", "cost": 0, "restaurants": ["스아게 스프카레"], "souvenirs": ["시로이 코이비토"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "도쿄 바나나", "price_krw": 15000, "desc": "부드러운 바나나 커스터드 케이크", "img": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400"},
            {"name": "로이스 생초콜릿", "price_krw": 11000, "desc": "입안에서 사르르 녹는 초콜릿", "img": "https://images.unsplash.com/photo-1548907040-4baa42d10919?w=400"},
            {"name": "휴족시간 & 동전파스", "price_krw": 8000, "desc": "피로 해소 의약품", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"}
        ]
    },
    "2위. 베트남 (다낭 · 나트랑)": {
        "summary": "가성비 리조트 휴양과 마사지, 로컬 푸드가 강점입니다.",
        "currency_name": "동 (VND)",
        "rate": 0.052,
        "recommended_exchange": 2000000,
        "est_budget_text": "1인당 약 60만 원 ~ 120만 원 (3박 4일 기준)",
        "cities": {
            "다낭 & 호이안": [
                {"name": "미케 비치", "lat": 16.0544, "lon": 108.2474, "desc": "세계 6대 해변", "cost": 0, "restaurants": ["목식당"], "souvenirs": ["G7 커피"]},
                {"name": "바나힐", "lat": 15.9977, "lon": 107.9881, "desc": "산상 테마파크 & 골든브릿지", "cost": 45000, "restaurants": ["바나힐 뷔페"], "souvenirs": ["수제 초콜릿"]},
                {"name": "한시장", "lat": 16.0680, "lon": 108.2248, "desc": "라탄백 및 기념품 쇼핑", "cost": 0, "restaurants": ["마담란"], "souvenirs": ["라탄백"]}
            ],
            "나트랑": [
                {"name": "빈원더스", "lat": 12.2215, "lon": 109.2422, "desc": "섬 전체 테마파크", "cost": 48000, "restaurants": ["빈펄 푸드코트"], "souvenirs": ["진주 공예품"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "G7 커피", "price_krw": 5000, "desc": "베트남 인스턴트 커피", "img": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400"},
            {"name": "라탄백", "price_krw": 12000, "desc": "휴양지 필수 수공예 가방", "img": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400"},
            {"name": "체리망고 젤리", "price_krw": 4000, "desc": "달콤 쫀득한 망고 간식", "img": "https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=400"}
        ]
    },
    "3위. 중국 (상하이 · 칭다오)": {
        "summary": "무비자 여행, 화려한 야경과 미식의 도시입니다.",
        "currency_name": "위안 (CNY)",
        "rate": 201.4,
        "recommended_exchange": 1500,
        "est_budget_text": "1인당 약 50만 원 ~ 90만 원 (2~3박 기준)",
        "cities": {
            "상하이": [
                {"name": "와이탄", "lat": 31.2397, "lon": 121.4998, "desc": "유럽풍 건축물과 마천루 야경", "cost": 0, "restaurants": ["와이포지아"], "souvenirs": ["토끼사탕"]},
                {"name": "상하이 디즈니랜드", "lat": 31.1440, "lon": 121.6570, "desc": "아시아 최대 규모 디즈니", "cost": 85000, "restaurants": ["디즈니타운 레스토랑"], "souvenirs": ["리나벨 굿즈"]}
            ],
            "칭다오": [
                {"name": "5.4 광장", "lat": 36.0632, "lon": 120.3826, "desc": "붉은 횃불 조형물과 야경", "cost": 0, "restaurants": ["메이다얼"], "souvenirs": ["맥주 효모 초콜릿"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "토끼표 밀크사탕", "price_krw": 4000, "desc": "중국 전통 우유 캐러멜", "img": "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=400"},
            {"name": "칭다오 맥주 꿀땅콩", "price_krw": 5000, "desc": "맥주 안주로 제격인 땅콩 스낵", "img": "https://images.unsplash.com/photo-1563227812-0ea4c22e6cc8?w=400"},
            {"name": "중국 차 세트", "price_krw": 15000, "desc": "보이차 및 우롱차 세트", "img": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400"}
        ]
    },
    "4위. 미국 (하와이 · 괌 · 뉴욕)": {
        "summary": "가족 휴양, 신혼여행, 쇼핑, 대도시 관광의 정석입니다.",
        "currency_name": "달러 (USD)",
        "rate": 1380.0,
        "recommended_exchange": 500,
        "est_budget_text": "1인당 약 180만 원 ~ 350만 원 이상",
        "cities": {
            "하와이 (오아후)": [
                {"name": "와이키키 해변", "lat": 21.2766, "lon": -157.8278, "desc": "서핑과 일몰 감상 명소", "cost": 0, "restaurants": ["듀크스 와이키키"], "souvenirs": ["마카다미아 초콜릿"]},
                {"name": "다이아몬드 헤드", "lat": 21.2620, "lon": -157.8054, "desc": "전경을 내려다보는 트레킹", "cost": 5000, "restaurants": ["파이어니어 살룬"], "souvenirs": ["코나 커피"]}
            ],
            "괌": [
                {"name": "투몬 비치", "lat": 13.5135, "lon": 144.8062, "desc": "에메랄드빛 해변 중심가", "cost": 0, "restaurants": ["비치인 쉬림프"], "souvenirs": ["아이러브괌 굿즈"]}
            ],
            "뉴욕": [
                {"name": "타임스 스퀘어", "lat": 40.7580, "lon": -73.9855, "desc": "세계 문화의 중심지", "cost": 0, "restaurants": ["주니어스 치즈케이크"], "souvenirs": ["M&M 월드 굿즈"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "마카다미아 너트 초콜릿", "price_krw": 18000, "desc": "고소한 하와이 초콜릿 선물", "img": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=400"},
            {"name": "고디바 프레즐 & 영양제", "price_krw": 15000, "desc": "미국 대형마트 쟁임템 단짠 간식", "img": "https://images.unsplash.com/photo-1599599810694-b5b37242c757?w=400"}
        ]
    },
    "5위. 태국 (방콕 · 치앙마이)": {
        "summary": "화려한 왕궁 사원, 호캉스, 감성 카페와 야시장 미식 여행지입니다.",
        "currency_name": "바트 (THB)",
        "rate": 38.5,
        "recommended_exchange": 10000,
        "est_budget_text": "1인당 약 60만 원 ~ 110만 원",
        "cities": {
            "방콕": [
                {"name": "왕궁 & 왓 아룬", "lat": 13.7437, "lon": 100.4889, "desc": "황금빛 왕궁과 새벽사원", "cost": 15000, "restaurants": ["팁싸마이"], "souvenirs": ["야돔"]},
                {"name": "아이콘시암", "lat": 13.7267, "lon": 100.5105, "desc": "실내 수상시장 ‘쑥시암’", "cost": 0, "restaurants": ["노스이스트"], "souvenirs": ["나라야 리본백"]}
            ],
            "치앙마이": [
                {"name": "님만해민", "lat": 18.7997, "lon": 98.9675, "desc": "트렌디한 카페 거리", "cost": 0, "restaurants": ["카오소이 님만"], "souvenirs": ["아로마 오일"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "나라야 리본백", "price_krw": 10000, "desc": "가볍고 실용적인 태국 패션 가방", "img": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400"},
            {"name": "야돔 & 타이 밀크티", "price_krw": 4000, "desc": "시원한 야돔과 달콤한 차 스틱", "img": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=400"}
        ]
    },
    "6위. 필리핀 (세부 · 보홀)": {
        "summary": "호핑 투어와 스노클링 등 해양 액티비티의 성지입니다.",
        "currency_name": "페소 (PHP)",
        "rate": 24.0,
        "recommended_exchange": 10000,
        "est_budget_text": "1인당 약 60만 원 ~ 100만 원",
        "cities": {
            "세부": [
                {"name": "막탄 뉴타운", "lat": 10.3106, "lon": 124.0150, "desc": "리조트 인접 쇼핑 및 다이닝", "cost": 0, "restaurants": ["마리바고 그릴"], "souvenirs": ["건망고"]}
            ],
            "보홀": [
                {"name": "알로나 비치", "lat": 9.5484, "lon": 123.7736, "desc": "호핑 투어 출발지 해변", "cost": 0, "restaurants": ["헤난 리조트 다이닝"], "souvenirs": ["드림캐처"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "7D 건망고 & 바나나칩", "price_krw": 5000, "desc": "장바구니 필수 달콤 바삭 간식", "img": "https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=400"},
            {"name": "코코넛 오일 & 진주 액세서리", "price_krw": 12000, "desc": "천연 보습 오일과 진주 소품", "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400"}
        ]
    },
    "7위. 대만 (타이베이 · 가오슝)": {
        "summary": "짧은 비행시간, 야시장 미식, 감성적인 근교 풍경이 매력적입니다.",
        "currency_name": "대만 달러 (TWD)",
        "rate": 43.0,
        "recommended_exchange": 10000,
        "est_budget_text": "1인당 약 60만 원 ~ 100만 원",
        "cities": {
            "타이베이": [
                {"name": "타이베이 101", "lat": 25.0339, "lon": 121.5645, "desc": "초고속 엘리베이터 전망대", "cost": 25000, "restaurants": ["딘타이펑"], "souvenirs": ["펑리수"]},
                {"name": "시먼딩", "lat": 25.0422, "lon": 121.5074, "desc": "대만의 명동 젊음의 거리", "cost": 0, "restaurants": ["아종면선 곱창국수"], "souvenirs": ["누가크래커"]}
            ],
            "가오슝": [
                {"name": "보얼 예술특구", "lat": 22.6200, "lon": 120.2816, "desc": "창고를 개조한 감성 예술 거리", "cost": 0, "restaurants": ["항원 우육면"], "souvenirs": ["디자인 엽서"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "펑리수 & 누가크래커", "price_krw": 16000, "desc": "파인애플 과자 및 단짠 누가크래커", "img": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400"},
            {"name": "3시 15분 밀크티", "price_krw": 7000, "desc": "티백 형태의 대만 국민 밀크티", "img": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400"}
        ]
    },
    "8위. 싱가포르": {
        "summary": "쾌적한 치안, 미래형 정원 야경, 다문화 미식 도시입니다.",
        "currency_name": "싱가포르 달러 (SGD)",
        "rate": 1030.0,
        "recommended_exchange": 500,
        "est_budget_text": "1인당 약 100만 원 ~ 180만 원",
        "cities": {
            "싱가포르": [
                {"name": "마리나 베이 샌즈", "lat": 1.2816, "lon": 103.8636, "desc": "슈퍼트리 쇼와 인피니티 풀", "cost": 35000, "restaurants": ["점보 시푸드"], "souvenirs": ["TWG 티"]},
                {"name": "머라이언 파크", "lat": 1.2868, "lon": 103.8545, "desc": "상징적인 머라이언 동상", "cost": 0, "restaurants": ["송파 바쿠테"], "souvenirs": ["카야잼"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "TWG 홍차 & 바샤 커피", "price_krw": 30000, "desc": "럭셔리 명품 티 및 드립백 세트", "img": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400"},
            {"name": "야쿤 카야잼", "price_krw": 7000, "desc": "달콤 고소한 싱가포르 국민 잼", "img": "https://images.unsplash.com/photo-1586015518255-cb4b9fc977b1?w=400"}
        ]
    },
    "9위. 인도네시아 (발리)": {
        "summary": "우붓의 정글 힐링과 스미냑의 비치클럽이 공존합니다.",
        "currency_name": "루피아 (IDR)",
        "rate": 0.088,
        "recommended_exchange": 2000000,
        "est_budget_text": "1인당 약 80만 원 ~ 150만 원",
        "cities": {
            "발리": [
                {"name": "우붓 왕궁 & 아트마켓", "lat": -8.5069, "lon": 115.2625, "desc": "전통 예술 중심지 공예품 시장", "cost": 0, "restaurants": ["이부 오카 바비굴링"], "souvenirs": ["라탄백"]},
                {"name": "스미냑 비치", "lat": -8.6795, "lon": 115.1455, "desc": "트렌디한 비치클럽과 선셋", "cost": 0, "restaurants": ["포테이토 헤드"], "souvenirs": ["천연 아로마 오일"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "루왁 커피 & 아로마 오일", "price_krw": 20000, "desc": "고급 원두와 천연 힐링 오일", "img": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400"},
            {"name": "센사티아 보태니컬 비누", "price_krw": 8000, "desc": "발리 천연 스킨케어 제품", "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400"}
        ]
    },
    "10위. 호주 (시드니)": {
        "summary": "오페라 하우스 항구 풍경과 대자연을 품은 남반구 여행지입니다.",
        "currency_name": "호주 달러 (AUD)",
        "rate": 910.0,
        "recommended_exchange": 500,
        "est_budget_text": "1인당 약 180만 원 ~ 300만 원 이상",
        "cities": {
            "시드니": [
                {"name": "오페라 하우스", "lat": -33.8568, "lon": 151.2153, "desc": "시드니 항구의 상징적 건축물", "cost": 40000, "restaurants": ["오페라 바"], "souvenirs": ["어그 굿즈"]},
                {"name": "본다이 비치", "lat": -33.8915, "lon": 151.2767, "desc": "서퍼들의 성지 해변", "cost": 0, "restaurants": ["빌즈 본다이"], "souvenirs": ["서핑 브랜드 굿즈"]}
            ]
        },
        "souvenirs_detail": [
            {"name": "팀탐 초콜릿 & 마누카 꿀", "price_krw": 12000, "desc": "호주 국민 간식과 건강한 꿀", "img": "https://images.unsplash.com/photo-1548907040-4baa42d10919?w=400"},
            {"name": "포포 크림 (루카스)", "price_krw": 6000, "desc": "만능 멀티 보습 연고", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"}
        ]
    }
}

# ---------------------------------------------------------
# 2. 거리 계산 함수
# ---------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def optimize_route(selected_places):
    if len(selected_places) <= 1:
        return selected_places, 0.0
    unvisited = selected_places[1:].copy()
    route = [selected_places[0]]
    total_dist = 0.0
    while unvisited:
        current = route[-1]
        nearest = min(unvisited, key=lambda p: haversine(current["lat"], current["lon"], p["lat"], p["lon"]))
        total_dist += haversine(current["lat"], current["lon"], nearest["lat"], nearest["lon"])
        route.append(nearest)
        unvisited.remove(nearest)
    return route, round(total_dist, 2)

# ---------------------------------------------------------
# 3. 화면 UI 구현
# ---------------------------------------------------------
st.title("✈️ 한국인 인기 해외여행 10개국 동선 & 예산 플래너")
st.markdown("상단에서 국가 및 세부 도시를 고르면 **실시간 환율 및 환전 비용**, **도시 옆 기념품 선택 창**, 그리고 **최종 합산 예산**이 연동됩니다.")

# [STEP 1] 상단: 국가 및 세부 도시 선택 + 환율 정보 표시
st.subheader("1️⃣ 방문할 국가 및 세부 도시 선택")
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    selected_country = st.selectbox("국가 선택 (총 10개국)", list(TRAVEL_DATA.keys()))

country_info = TRAVEL_DATA[selected_country]

with top_col2:
    selected_city = st.selectbox(
        f"세부 도시 선택 ({len(country_info['cities'])}개 도시)",
        list(country_info["cities"].keys())
    )

# 환율 및 환전 비용 안내 상단 고정 배너
rate = country_info["rate"]
rec_amt = country_info["recommended_exchange"]
calc_krw = int(rec_amt * rate)

st.info(f"💱 **[현재 환율 정보]** 1 {country_info['currency_name']} 기준 약 **{rate:,.1f}원**  |  "
        f"💡 **[추천 현지 환전 비용]** 추천 환전액 {rec_amt:,.0f} {country_info['currency_name']} 환전 시 **약 {calc_krw:,}원** 소요  |  "
        f"💰 **[전체 여행 예상 총예산]** {country_info['est_budget_text']}")

st.divider()

# [STEP 2] 레이아웃 분할: 왼쪽(관광지 선택) / 오른쪽(세부 도시 옆 기념품 고르는 창)
main_col1, main_col2 = st.columns([1.3, 1])

with main_col1:
    st.subheader(f"2️⃣ [{selected_city}] 방문할 관광지 선택")
    places = country_info["cities"][selected_city]
    
    selected_places = []
    for idx, place in enumerate(places):
        chk_key = f"chk_{selected_city}_{idx}"
        if chk_key not in st.session_state:
            st.session_state[chk_key] = True # 기본 선택
            
        with st.container(border=True):
            c_box, c_desc = st.columns([3, 1])
            with c_box:
                is_checked = st.checkbox(f"**{place['name']}** (입장료: {place['cost']:,}원)", key=chk_key)
                st.caption(place["desc"])
            with c_desc:
                st.markdown(f"**{place['cost']:,}원**")
            
            if is_checked:
                selected_places.append(place)

with main_col2:
    st.subheader(f"🛍️ [{selected_city} 옆] 기념품 고르기")
    st.caption("체크하면 최종 예산에 자동으로 합산됩니다!")
    
    selected_souvenirs = []
    for s_idx, item in enumerate(country_info["souvenirs_detail"]):
        s_key = f"souv_{selected_city}_{s_idx}"
        
        with st.container(border=True):
            sc1, sc2 = st.columns([1, 1.5])
            with sc1:
                st.image(item['img'], use_column_width=True)
            with sc2:
                s_checked = st.checkbox(f"**{item['name']}**", key=s_key)
                st.markdown(f"가격: **{item['price_krw']:,}원**")
                st.caption(item['desc'])
                
            if s_checked:
                selected_souvenirs.append(item)

st.divider()

# [STEP 3] 최종 동선 최적화 및 비용 총합 계산
st.subheader("3️⃣ 최종 맞춤 동선 및 💰 총 합산 비용 안내")

if not selected_places:
    st.warning("⚠️ 왼쪽에서 관광지를 최소 1곳 이상 선택해 주세요!")
else:
    optimized_route, total_km = optimize_route(selected_places)
    
    # 비용 합산 계산
    ticket_total = sum([p["cost"] for p in selected_places])
    souvenir_total = sum([s["price_krw"] for s in selected_souvenirs])
    
    # 임의 추정 식비/교통비 (기본 체류비)
    est_food_transport = 250000 
    
    grand_total = ticket_total + souvenir_total + est_food_transport
    
    res_c1, res_c2 = st.columns([1.2, 1])
    
    with res_c1:
        st.markdown("### 🗺️ 최적 추천 동선")
        route_arrow = " ➡️ ".join([f"**{i+1}. {p['name']}**" for i, p in enumerate(optimized_route)])
        st.success(f"{route_arrow} (총 이동거리 약 {total_km} km)")
        
        for idx, spot in enumerate(optimized_route):
            with st.expander(f"🚩 {idx+1}코스: {spot['name']}"):
                st.write(f"설명: {spot['desc']}")
                st.markdown(f"입장료: **{spot['cost']:,}원**")
                st.markdown(f"추천 맛집: {', '.join(spot['restaurants'])}")
                
    with res_c2:
        st.markdown("### 💳 관광지 돌면 드는 총 비용 합산")
        st.markdown(
            f"""
            - 🎟️ **관광지 입장료 총합:** `{ticket_total:,}원`
            - 🛍️ **고른 기념품 구매 총합:** `{souvenir_total:,}원`
            - 🍜 **예상 식비 및 현지 교통비:** `{est_food_transport:,}원` (기본 체류 추정)
            ---
            ### 🔥 **최종 합산 총비용:** \n# **`{grand_total:,}원`**
            """
        )
        
    # 지도 시각화
    st.markdown("### 📍 동선 지도 미리보기")
    avg_lat = sum(p["lat"] for p in optimized_route) / len(optimized_route)
    avg_lon = sum(p["lon"] for p in optimized_route) / len(optimized_route)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="OpenStreetMap")
    coords = []
    for idx, spot in enumerate(optimized_route):
        coords.append([spot["lat"], spot["lon"]])
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            tooltip=f"{idx+1}. {spot['name']}",
            icon=folium.Icon(color="red" if idx == 0 else "blue", icon="info-sign")
        ).add_to(m)
        
    if len(coords) > 1:
        folium.PolyLine(coords, color="#FF4B4B", weight=4, opacity=0.8).add_to(m)
        
    st_folium(m, width=1100, height=450, returned_objects=[])
