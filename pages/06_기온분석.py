import os
import platform
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

st.set_page_config(page_title="월별 기온 분석", layout="wide")


# 1. 한글 폰트 직접 로드 (FontProperties 객체 반환 -> "가가가가" 현상 원천 차단)
def get_korean_font() -> fm.FontProperties | None:
    system_name = platform.system()

    # OS별 기본 한글 폰트 경로 후보
    if system_name == "Windows":
        font_candidates = [
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/NanumGothic.ttf",
            "C:/Windows/Fonts/gulim.ttc",
        ]
    elif system_name == "Darwin":  # macOS
        font_candidates = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/AppleGothic.ttf",
            "/Library/Fonts/NanumGothic.ttf",
        ]
    else:  # Linux / Streamlit Cloud
        font_candidates = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
        ]

    # 후보 경로 중 실제 존재하는 파일 사용
    for path in font_candidates:
        if os.path.exists(path):
            fm.fontManager.addfont(path)
            prop = fm.FontProperties(fname=path)
            plt.rcParams["font.family"] = prop.get_name()
            plt.rcParams["axes.unicode_minus"] = False
            return prop

    # 경로에 없으면 koreanize_matplotlib 폴백 시도
    try:
        import koreanize_matplotlib  # noqa: F401
        plt.rcParams["axes.unicode_minus"] = False
    except ImportError:
        pass

    return None


font_prop = get_korean_font()


# 2. 데이터 로드 및 전처리
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

    years, months = [], []
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


# 3. 메인 UI
st.title("🌡️ 기상 관측 데이터 분석 대시보드")

try:
    df = load_data("temperature.csv")
except FileNotFoundError:
    st.error("같은 폴더에 'temperature.csv' 파일이 있는지 확인해주세요.")
    st.stop()

st.sidebar.header("검색 조건 설정")
selected_month = st.sidebar.selectbox(
    "분석할 월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=7,
)

filtered_df = df[df["월"] == selected_month].dropna(subset=["최고기온(℃)", "최저기온(℃)"])

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

# 4. 꺾은선 그래프 그리기 (모든 텍스트에 fontproperties 직접 적용)
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

# 제목, 축 라벨, 범례에 font_prop 직접 지정
if font_prop is not None:
    ax.set_title("월별 기온분석", fontproperties=font_prop, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("년도", fontproperties=font_prop, fontsize=12)
    ax.set_ylabel("온도 (℃)", fontproperties=font_prop, fontsize=12)
    ax.legend(prop=font_prop, loc="best", frameon=True)
else:
    ax.set_title("월별 기온분석", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("년도", fontsize=12)
    ax.set_ylabel("온도 (℃)", fontsize=12)
    ax.legend(loc="best", fontsize=11, frameon=True)

ax.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig)

with st.expander(f"{selected_month}월 상세 데이터 보기"):
    st.dataframe(
        filtered_df[["년도", "월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
        use_container_width=True,
    )
