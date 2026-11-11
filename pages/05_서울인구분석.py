import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서울시 연령별 인구 분석", page_icon="📈", layout="wide"
)

# 한글 폰트 설정 (리눅스 기반 스트림릿 클라우드 환경 대응)
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


# 데이터 로드 함수 (어디서 실행되든 안전하게 파일을 찾는 방식)
@st.cache_data
def load_data():
  # 현재 실행 중인 py 파일의 폴더 경로 기준
  script_dir = os.path.dirname(os.path.abspath(__file__))

  # 1. 상위 폴더(루트)에 있는 경우 시도 (pages/ 에 있을 때)
  csv_path = os.path.join(script_dir, "..", "population.csv")
  if not os.path.exists(csv_path):
    # 2. 같은 폴더에 있는 경우 시도
    csv_path = os.path.join(script_dir, "population.csv")
  if not os.path.exists(csv_path):
    # 3. 현재 작업 디렉토리 기준 시도
    csv_path = "population.csv"

  df = pd.read_csv(csv_path, encoding="cp949")
  return df


try:
  df = load_data()
except Exception as e:
  st.error(
      "데이터 파일을 불러오는 중 오류가 발생했습니다. 프로젝트 루트 폴더에"
      " 'population.csv' 파일이 존재하는지 확인해주세요.\n오류"
      f" 내용: {e}"
  )
  st.stop()

# 제목 및 설명
st.title("📊 서울시 자치구별·연도별 연령별 인구수 시각화")
st.markdown(
    "사이드바에서 **행정구역, 연도, 성별**을 선택하여 연령별 인구 변화를"
    " 확인해보세요."
)

# 사이드바 설정 (사용자 입력)
st.sidebar.header("🔍 조회 옵션 설정")

# 1. 행정구역 선택
districts = df["행정구역"].tolist()
selected_district = st.sidebar.selectbox("행정구역 선택", districts)

# 2. 연도 선택 (2020년 ~ 2025년)
years = ["2020년", "2021년", "2022년", "2023년", "2024년", "2025년"]
selected_year = st.sidebar.selectbox("연도 선택", years)

# 3. 성별 선택
gender_options = ["전체", "남성", "여성"]
selected_gender = st.sidebar.selectbox("성별 선택", gender_options)

# 데이터 추출 및 가공
row_data = df[df["행정구역"] == selected_district].iloc[0]

# 성별 및 연도에 맞는 연령별 컬럼 매핑
if selected_gender == "전체":
  prefix = f"{selected_year}_거주자_"
elif selected_gender == "남성":
  prefix = f"{selected_year}_남_거주자_"
else:
  prefix = f"{selected_year}_여_거주자_"

# 나이 구간 컬럼 추출 (총인구수, 연령구간인구수 제외)
age_cols = [
    c
    for c in df.columns
    if c.startswith(prefix)
    and "총인구수" not in c
    and "연령구간인구수" not in c
]

# 나이 라벨 정제
age_labels = [c.replace(prefix, "") for c in age_cols]

# 인구수 값 추출 및 콤마 제거 후 정수 변환
population_values = []
for c in age_cols:
  val = str(row_data[c]).replace(",", "").strip()
  population_values.append(int(val) if val.isdigit() else 0)

# 시각화 데이터프레임 생성
chart_df = pd.DataFrame({"나이": age_labels, "인구수": population_values})

# 메인 화면 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
  st.subheader(
      f"📍 {selected_district} ({selected_year} / {selected_gender})"
  )

  # 맷플롯립 꺾은선 그래프 생성
  fig, ax = plt.subplots(figsize=(10, 5))

  # 성별에 따른 그래프 선 색상 지정
  line_color = (
      "#1f77b4"
      if selected_gender == "전체"
      else ("#2ca02c" if selected_gender == "남성" else "#d62728")
  )

  ax.plot(
      chart_df["나이"],
      chart_df["인구수"],
      marker="o",
      color=line_color,
      linewidth=2.5,
      markersize=6,
  )

  # 제목 및 축 레이블
  ax.set_title(
      f"{selected_year} {selected_district} 연령별 인구 분포",
      fontsize=14,
      pad=15,
  )
  ax.set_xlabel("나이 구간", fontsize=11)
  ax.set_ylabel("인구수 (명)", fontsize=11)

  # 세로축 콤마 포맷 및 1,000명 단위 격자선(Grid) 설정
  from matplotlib.ticker import StrMethodFormatter

  ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}명"))
  ax.grid(True, linestyle="--", alpha=0.6)

  # X축 레이블 회전
  plt.xticks(rotation=30)
  plt.tight_layout()

  # 스트림릿에 그래프 출력
  st.pyplot(fig)

with col2:
  st.subheader("📋 상세 데이터 요약")
  display_df = chart_df.copy()
  display_df["인구수"] = display_df["인구수"].apply(lambda x: f"{x:,} 명")
  st.dataframe(display_df, use_container_width=True, hide_index=True)
