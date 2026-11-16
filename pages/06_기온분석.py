import pandas as pd
import streamlit as st

st.set_page_config(page_title="서울 기상 관측 대시보드", layout="wide")


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


try:
    df = load_data("temperature.csv")
except FileNotFoundError:
    st.error("같은 폴더에 'temperature.csv' 파일이 있는지 확인해주세요.")
    st.stop()

st.title("🌡️ 서울 기상 관측 데이터 분석 대시보드")

# ==========================================
# 본문 상단: 분석 메뉴 선택창
# ==========================================
menu = st.selectbox(
    "🔍 원하는 분석 메뉴를 선택하세요",
    [
        "1. 특정 월의 연도별 최고/최저기온 추이",
        "2. 서울 월별 평균기온 (1~12월)",
        "3. 특정 연도의 월별 최고/최저기온",
        "4. 두 개 연도 월별 평균기온 비교",
    ],
)

st.markdown("---")

all_years = sorted(df["년도"].unique())

# ==========================================
# 기능 1: 특정 월 선택 -> 연도별 최고/최저기온 그래프
# ==========================================
if menu == "1. 특정 월의 연도별 최고/최저기온 추이":
    st.subheader("📈 월별 기온분석 (연도별 최고·최저기온)")

    selected_month = st.selectbox(
        "📅 분석할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월",
        index=7,
    )

    filtered_df = df[df["월"] == selected_month].dropna(subset=["최고기온(℃)", "최저기온(℃)"])

    chart_data = filtered_df.set_index("년도")[["최고기온(℃)", "최저기온(℃)"]]
    chart_data.columns = ["최고기온", "최저기온"]

    st.line_chart(chart_data, color=["#FF4B4B", "#1C83E1"])

    with st.expander(f"{selected_month}월 상세 데이터 보기"):
        st.dataframe(
            filtered_df[["년도", "월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
            use_container_width=True,
        )


# ==========================================
# 기능 2: 가로축 1~12월, 서울 월별 평균기온 그래프
# ==========================================
elif menu == "2. 서울 월별 평균기온 (1~12월)":
    st.subheader("📊 서울 월별 평균기온 분석 (1월 ~ 12월)")

    monthly_avg = df.groupby("월")["평균기온(℃)"].mean().reset_index()
    monthly_avg.columns = ["월", "평균기온"]
    monthly_avg["월_표시"] = monthly_avg["월"].apply(lambda x: f"{x:02d}월")

    chart_data = monthly_avg.set_index("월_표시")[["평균기온"]]

    st.line_chart(chart_data, color=["#FF7F0E"])

    with st.expander("상세 데이터 보기"):
        st.dataframe(monthly_avg[["월", "평균기온"]].reset_index(drop=True), use_container_width=True)


# ==========================================
# 기능 3: 연도 1개 선택 -> 해당 연도 최고/최저기온 그래프
# ==========================================
elif menu == "3. 특정 연도의 월별 최고/최저기온":
    st.subheader("📈 특정 연도 월별 최고 및 최저기온 추이")

    selected_year = st.selectbox(
        "📅 분석할 연도를 선택하세요",
        options=all_years,
        index=len(all_years) - 1,
    )

    year_df = df[df["년도"] == selected_year].sort_values("월").copy()
    year_df["월_표시"] = year_df["월"].apply(lambda x: f"{x:02d}월")

    chart_data = year_df.set_index("월_표시")[["최고기온(℃)", "최저기온(℃)"]]
    chart_data.columns = ["최고기온", "최저기온"]

    st.line_chart(chart_data, color=["#FF4B4B", "#1C83E1"])

    with st.expander(f"{selected_year}년 상세 데이터 보기"):
        st.dataframe(
            year_df[["월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
            use_container_width=True,
        )


# ==========================================
# 기능 4: 연도 2개 선택 -> 2개 연도 비교 그래프
# ==========================================
elif menu == "4. 두 개 연도 월별 평균기온 비교":
    st.subheader("⚖️ 두 개 연도 평균기온 비교 분석")

    col_y1, col_y2 = st.columns(2)
    with col_y1:
        year1 = st.selectbox(
            "📅 첫 번째 연도 선택",
            options=all_years,
            index=len(all_years) - 2,
        )
    with col_y2:
        year2 = st.selectbox(
            "📅 두 번째 연도 선택",
            options=all_years,
            index=len(all_years) - 1,
        )

    df_y1 = df[df["년도"] == year1][["월", "평균기온(℃)"]].rename(columns={"평균기온(℃)": f"{year1}년"})
    df_y2 = df[df["년도"] == year2][["월", "평균기온(℃)"]].rename(columns={"평균기온(℃)": f"{year2}년"})

    comparison_df = pd.merge(df_y1, df_y2, on="월", how="outer").sort_values("월")
    comparison_df["월_표시"] = comparison_df["월"].apply(lambda x: f"{x:02d}월")

    chart_data = comparison_df.set_index("월_표시")[[f"{year1}년", f"{year2}년"]]

    st.line_chart(chart_data, color=["#2ca02c", "#d62728"])

    with st.expander("비교 상세 데이터 보기"):
        st.dataframe(
            comparison_df[["월", f"{year1}년", f"{year2}년"]].reset_index(drop=True),
            use_container_width=True,
        )
