import platform
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(page_title="월별 기온 분석", layout="wide")


# 2. OS별 한글 폰트 설정 (그래프 한글 깨짐 방지)
def set_korean_font():
    system_name = platform.system()
    if system_name == "Windows":
        plt.rcParams["font.family"] = "Malgun Gothic"
    elif system_name == "Darwin":  # macOS
        plt.rcParams["font.family"] = "AppleGothic"
    else:  # Linux / Streamlit Cloud (packages.txt에 fonts-nanum 설치 권장)
        font_list = [f.name for f in fm.fontManager.ttflist]
        if "NanumGothic" in font_list:
            plt.rcParams["font.family"] = "NanumGothic"
        elif "Noto Sans CJK JP" in font_list:
            plt.rcParams["font.family"] = "Noto Sans CJK JP"

    # 마이너스(-) 부호 깨짐 방지
    plt.rcParams["axes.unicode_minus"] = False


set_korean_font()


# 3. 데이터 로드 및 전처리 (인코딩 자동 처리 및 1907~2025년 실제 연도 복원)
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    df = None
    for enc in ["cp949", "euc-kr", "utf-8", "utf-8-sig"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }

    # 'Oct-07' 형태의 2자리 연도가 1907년과 2007년으로 중복되므로 순차적으로 연도 계산
    years = []
    months = []
    curr_year = 1907
    prev_month = 9

    for date_str in df["일시"]:
        m_str, _ = str(date_str).strip().split("-")
        m = month_map[m_str]
        if m < prev_month:
            curr_year += 1
        years.append(curr_year)
        months.append(m)
        prev_month = m

    df["년도"] = years
    df["월"] = months
    return df


# 4. 메인 화면 구성
st.title("🌡️ 기상 관측 데이터 분석 대시보드")

try:
    df = load_data("temperature.csv")
except FileNotFoundError:
    st.error("같은 폴더에 'temperature.csv' 파일이 있는지 확인해주세요.")
    st.stop()

# 사이드바에서 월 선택
st.sidebar.header("검색 조건 설정")
selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=7,  # 기본값: 8월
)

# 선택한 월 데이터 필터링 및 결측치 제거
filtered_df = df[df["월"] == selected_month].dropna(subset=["최고기온(℃)", "최저기온(℃)"])

# 요약 지표 표시
col1, col2, col3 = st.columns(3)
col1.metric("선택한 월", f"{selected_month}월")
col2.metric(
    f"역대 {selected_month}월 최고기온",
    f"{filtered_df['최고기온(℃)'].max():.1f} ℃",
    f"{int(filtered_df.loc[filtered_df['최고기온(℃)'].idxmax(), '년도'])}년",
)
col3.metric(
    f"역대 {selected_month}월 최저기온",
    f"{filtered_df['최저기온(℃)'].min():.1f} ℃",
    f"{int(filtered_df.loc[filtered_df['최저기온(℃)'].idxmin(), '년도'])}년",
)

# 5. 꺾은선 그래프 그리기
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    filtered_df["년도"],
    filtered_df["최고기온(℃)"],
    color="red",
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="최고기온",
)
ax.plot(
    filtered_df["년도"],
    filtered_df["최저기온(℃)"],
    color="blue",
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="최저기온",
)

# 제목, 축 라벨, 범례 설정
ax.set_title("월별 기온분석", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("년도", fontsize=12)
ax.set_ylabel("온도 (℃)", fontsize=12)
ax.legend(loc="best", fontsize=11, frameon=True)
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

# 선택된 월의 원본 데이터 표 확인
with st.expander(f"{selected_month}월 상세 데이터 보기"):
    st.dataframe(
        filtered_df[["년도", "월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
        use_container_width=True,
    )
