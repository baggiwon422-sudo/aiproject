import pandas as pd
import streamlit as st

st.set_page_config(page_title="월별 기온 분석", layout="wide")


# 1. 데이터 로드 및 전처리
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


# 2. 메인 UI
st.title("🌡️ 월별 기온분석 대시보드")

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

# 선택한 월 데이터 필터링 및 필요한 컬럼만 추출
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

st.markdown("---")
st.subheader(f"📈 월별 기온분석 ({selected_month}월)")

# 3. Streamlit 내장 꺾은선 그래프용 데이터프레임 가공
# 인덱스를 '년도'로 설정하고 최고기온, 최저기온만 남김
chart_data = filtered_df.set_index("년도")[["최고기온(℃)", "최저기온(℃)"]]
chart_data.columns = ["최고기온", "최저기온"]  # 범례 이름

# Streamlit 내장 차트 출력 (빨강/파랑 색상 지정은 불가하지만 한글이 절대 안 깨짐)
st.line_chart(chart_data, color=["#FF4B4B", "#1C83E1"])

# 상세 데이터 표
with st.expander(f"{selected_month}월 상세 데이터 보기"):
    st.dataframe(
        filtered_df[["년도", "월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
        use_container_width=True,
    )
