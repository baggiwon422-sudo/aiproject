import os
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서울시 연령별 인구 분석", page_icon="📈", layout="wide"
)

# 한글 폰트 설정 (리눅스 기반 스트림릿 클라우드 환경 대응)
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


# 데이터 로드 함수 (경로 안전 장치 적용)
@st.cache_data
def load_data():
  script_dir = os.path.dirname(os.path.abspath(__file__))
  csv_path = os.path.join(script_dir, "..", "population.csv")
  if not os.path.exists(csv_path):
    csv_path = os.path.join(script_dir, "population.csv")
  if not os.path.exists(csv_path):
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
st.markdown("---")

# 공통 옵션 리스트
years = ["2020년", "2021년", "2022년", "2023년", "2024년", "2025년"]
gender_options = ["전체", "남성", "여성"]
age_brackets = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상",
]
districts = df["행정구역"].tolist()

# 메인 화면에서 분석 모드 선택 (라디오 버튼)
analysis_mode = st.radio(
    "🎯 **원하시는 분석 방식을 선택하세요**",
    ["1. 특정 구 연령별 인구 추이 (꺾은선 그래프)", "2. 연령대별 자치구 순위 비교 (막대그래프)"],
    horizontal=True,
)

st.markdown("")

# ==========================================
# 모드 1: 특정 구 연령별 인구 추이 (본문 선택형)
# ==========================================
if analysis_mode == "1. 특정 구 연령별 인구 추이 (꺾은선 그래프)":
  st.subheader("📌 조회 조건 선택")

  # 본문 내 3개 컬럼으로 나누어 나란히 배치
  c1, c2, c3 = st.columns(3)
  with c1:
    selected_district = st.selectbox("행정구역 선택", districts, key="m1_dist")
  with c2:
    selected_year = st.selectbox("연도 선택", years, key="m1_year")
  with c3:
    selected_gender = st.selectbox("성별 선택", gender_options, key="m1_gender")

  st.markdown("---")

  # 데이터 추출 및 가공
  row_data = df[df["행정구역"] == selected_district].iloc[0]

  if selected_gender == "전체":
    prefix = f"{selected_year}_거주자_"
  elif selected_gender == "남성":
    prefix = f"{selected_year}_남_거주자_"
  else:
    prefix = f"{selected_year}_여_거주자_"

  age_cols = [
      c
      for c in df.columns
      if c.startswith(prefix)
      and "총인구수" not in c
      and "연령구간인구수" not in c
  ]
  age_labels = [c.replace(prefix, "") for c in age_cols]

  population_values = []
  for c in age_cols:
    val = str(row_data[c]).replace(",", "").strip()
    population_values.append(int(val) if val.isdigit() else 0)

  chart_df = pd.DataFrame({"나이": age_labels, "인구수": population_values})

  # 결과 출력 레이아웃
  res_col1, res_col2 = st.columns([2, 1])

  with res_col1:
    st.markdown(
        f"### 📍 {selected_district} ({selected_year} / {selected_gender})"
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    # 성별 색상 지정: 전체(파란색), 남성(핑크색), 여성(초록색)
    if selected_gender == "전체":
      line_color = "#1f77b4"
    elif selected_gender == "남성":
      line_color = "#ff69b4"  # 핑크
    else:
      line_color = "#228b22"  # 초록

    ax.plot(
        chart_df["나이"],
        chart_df["인구수"],
        marker="o",
        color=line_color,
        linewidth=2.5,
        markersize=6,
    )

    ax.set_title(
        f"{selected_year} {selected_district} 연령별 인구 분포",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("나이 구간", fontsize=11)
    ax.set_ylabel("인구수 (명)", fontsize=11)

    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}명"))
    ax.grid(True, linestyle="--", alpha=0.6)

    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig)

  with res_col2:
    st.markdown("### 📋 상세 데이터 요약")
    display_df = chart_df.copy()
    display_df["인구수"] = display_df["인구수"].apply(lambda x: f"{x:,} 명")
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ==========================================
# 모드 2: 연령대별 자치구 순위 비교 (본문 선택형)
# ==========================================
else:
  st.subheader("📌 조회 조건 선택")

  # 본문 내 3개 컬럼으로 나누어 나란히 배치
  c1, c2, c3 = st.columns(3)
  with c1:
    selected_year = st.selectbox("연도 선택", years, key="m2_year")
  with c2:
    selected_gender = st.selectbox("성별 선택", gender_options, key="m2_gender")
  with c3:
    selected_age = st.selectbox("연령대 선택", age_brackets, key="m2_age")

  st.markdown("---")

  # 컬럼 이름 조합 완성
  if selected_gender == "전체":
    target_col = f"{selected_year}_거주자_{selected_age}"
  elif selected_gender == "남성":
    target_col = f"{selected_year}_남_거주자_{selected_age}"
  else:
    target_col = f"{selected_year}_여_거주자_{selected_age}"

  # 서울시 전체(첫 번째 행)를 제외한 자치구 데이터만 추출 후 정렬
  dist_df = df.iloc[1:].copy()
  dist_df["인구수"] = (
      dist_df[target_col].astype(str).str.replace(",", "").astype(int)
  )
  dist_df = dist_df.sort_values(by="인구수", ascending=False)

  # 결과 출력 레이아웃
  res_col1, res_col2 = st.columns([2, 1])

  with res_col1:
    st.markdown(
        f"### 🏆 {selected_year} {selected_gender} '{selected_age}' 인구 상위"
        " 자치구 순위"
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    # 성별에 따른 막대 색상 지정 (
