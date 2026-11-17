import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 페이지 기본 설정
st.set_page_config(
    page_title="월별 평균기온 선형회귀 예측기",
    page_icon="🌡️",
    layout="wide"
)

# 1. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    # 한국 기상청 CSV 표준 인코딩(cp949) 우선 적용, 실패 시 utf-8 시도
    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8")

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()

    # '일시' 컬럼(예: Oct-07, Jan-26)에서 월(Month)과 연도(Year) 추출
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    extracted = df["일시"].astype(str).str.extract(r"^([A-Za-z]+)-(\d{2})$")
    df["월"] = extracted[0].map(month_map)
    yy = extracted[1].astype(float)

    # 1907년 10월 ~ 2026년 11월 연속 시계열 보정 (26 이하는 2000년대, 27 이상은 1900년대)
    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)

    # 결측치 제거 (평균기온 데이터가 비어있는 행 제외)
    df = df.dropna(subset=["연도", "월", "평균기온(℃)"]).copy()
    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'temperature.csv' 파일을 찾을 수 없습니다. 같은 폴더에 파일을 위치시켜 주세요.")
    st.stop()

# 2. 화면 타이틀 및 사이드바 사용자 입력
st.title("🌡️ 선형회귀(Linear Regression) 기반 월별 평균기온 예측")
st.markdown("과거 기온 데이터를 바탕으로 **선형회귀 알고리즘**이 어떻게 추세를 학습하고 미래 기온을 예측하는지 시각적으로 확인해 보세요.")

st.sidebar.header("⚙️ 예측 조건 설정")
selected_month = st.sidebar.selectbox(
    "1. 분석할 월(Month)을 선택하세요",
    options=list(range(1, 13)),
    index=7,  # 기본값: 8월
    format_func=lambda x: f"{x}월"
)

target_year = st.sidebar.number_input(
    "2. 예측할 연도(Year)를 입력하세요",
    min_value=1910,
    max_value=2150,
    value=2035,
    step=1
)

show_residuals = st.sidebar.checkbox(
    "오차(잔차) 보조선 표시하기",
    value=True,
    help="실제 기온(점)과 회귀선(직선) 사이의 거리(오차)를 점선으로 보여줍니다."
)

# 3. 선택한 월 데이터 필터링 및 선형회귀 모델 학습
month_df = df[df["월"] == selected_month].sort_values("연도").reset_index(drop=True)

X = month_df[["연도"]].values  # 독립변수 (연도)
y = month_df["평균기온(℃)"].values  # 종속변수 (평균기온)

model = LinearRegression()
model.fit(X, y)

# 학습된 가중치(기울기)와 편향(절편)
slope = model.coef_[0]
intercept = model.intercept_

# 과거 구간 추세선 값 및 사용자 입력 연도 예측값 계산
y_pred_past = model.predict(X)
predicted_temp = model.predict(np.array([[target_year]]))[0]

# 최근 10년 평균과 비교
recent_10y_avg = month_df.tail(10)["평균기온(℃)"].mean()
diff_from_recent = predicted_temp - recent_10y_avg

# 4. 핵심 요약 지표(KPI) 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label=f"🎯 {target_year}년 {selected_month}월 예측 평균기온",
    value=f"{predicted_temp:.2f} ℃",
    delta=f"최근 10년 평균 대비 {diff_from_recent:+.2f} ℃"
)
col2.metric(
    label="📈 10년당 기온 상승 추세 (기울기)",
    value=f"{slope * 10:+.3f} ℃ / 10년"
)
col3.metric(
    label="📅 학습 데이터 기간",
    value=f"{month_df['연도'].min()}년 ~ {month_df['연도'].max()}년"
)
col4.metric(
    label="📊 학습 데이터 개수",
    value=f"{len(month_df)}개"
)

# 5. 선형회귀 작동 원리 시각화 그래프 (Plotly)
fig = go.Figure()

# (1) 오차(잔차) 시각화: 실제 데이터와 회귀직선 사이의 수직 거리
if show_residuals:
    res_x = []
    res_y = []
    for yr, actual, pred in zip(month_df["연도"], y, y_pred_past):
        res_x.extend([yr, yr, None])
        res_y.extend([actual, pred, None])

    fig.add_trace(go.Scatter(
        x=res_x,
        y=res_y,
        mode="lines",
        line=dict(color="rgba(150, 150, 150, 0.45)", width=1, dash="dot"),
        name="오차(잔차): 실제값 - 예측선",
        hoverinfo="skip"
    ))

# (2) 실제 관측된 과거 평균기온 산점도 + 연도별 연결선
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=y,
    mode="markers+lines",
    marker=dict(size=7, color="#3B82F6", opacity=0.85),
    line=dict(color="rgba(59, 130, 246, 0.25)", width=1),
    name=f"실제 {selected_month}월 평균기온",
    hovertemplate="<b>%{x}년</b><br>실제 평균기온: %{y:.1f}℃<extra></extra>"
))

# (3) 과거 구간 선형회귀 추세선 (학습된 직선)
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=y_pred_past,
    mode="lines",
    line=dict(color="#EF4444", width=3),
    name="선형회귀 추세선 (학습된 직선)",
    hovertemplate="<b>%{x}년</b><br>추세선 기온: %{y:.2f}℃<extra></extra>"
))

# (4) 현재 마지막 연도부터 예측 연도까지 직선 연장선
last_year = int(month_df["연도"].max())
last_pred = y_pred_past[-1]

if target_year > last_year:
    ext_years = [last_year, target_year]
    ext_temps = [last_pred, predicted_temp]
    fig.add_trace(go.Scatter(
        x=ext_years,
        y=ext_temps,
        mode="lines",
        line=dict(color="#F59E0B", width=3, dash="dash"),
        name="미래 추세 연장선",
        hoverinfo="skip"
    ))

# (5) 사용자가 예측한 목표 연도 강조 마커
fig.add_trace(go.Scatter(
    x=[target_year],
    y=[predicted_temp],
    mode="markers+text",
    marker=dict(size=15, color="#F59E0B", symbol="star", line=dict(color="black", width=1.5)),
    text=[f"  {target_year}년 예측: {predicted_temp:.2f}℃"],
    textposition="top center",
    textfont=dict(size=13, color="#B45309", family="Arial Black"),
    name=f"{target_year}년 예측 결과",
    hovertemplate=f"<b>{target_year}년 {selected_month}월 예측</b><br>예측 평균기온: {predicted_temp:.2f}℃<extra></extra>"
))

# 수식 주석 추가
equation_text = f"학습된 예측 공식: 기온 = ({slope:.4f} × 연도) + ({intercept:.2f})"
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.02, y=0.96,
    text=f"<b>{equation_text}</b>",
    showarrow=False,
    bgcolor="rgba(255, 255, 255, 0.85)",
    bordercolor="#EF4444",
    borderwidth=1,
    font=dict(size=13, color="#1F2937")
)

fig.update_layout(
    title=f"<b>{selected_month}월 역대 평균기온 변화 및 {target_year}년 선형회귀 예측 시각화</b>",
    xaxis_title="연도 (Year)",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    height=560,
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 6. 그래프 하단: 선형회귀 알고리즘 쉬운 설명
st.divider()
st.subheader("💡 그래프 속 '선형회귀(Linear Regression)' 알고리즘 쉽게 이해하기")

st.markdown(f"""
**선형회귀(Linear Regression)**는 흩어져 있는 과거 데이터들의 전체적인 흐름을 가장 잘 대표하는 **'단 하나의 반듯한 직선(추세선)'**을 찾아내어 미래를 예측하는 인공지능·통계 알고리즘입니다.

1. **파란색 점 (실제 과거 데이터)**  
   1907년부터 지금까지 매년 **{selected_month}월의 실제 평균기온**을 찍은 점입니다. 날씨 변화 때문에 매년 위아래로 오르락내리락합니다.

2. **회색 점선 (오차/잔차)과 빨간색 실선 (최적의 추세선)**  
   선형회귀 알고리즘은 모든 파란색 점들과 직선 사이의 **세로 거리(회색 점선 = 오차)의 제곱 합이 가장 작아지는 위치**에 **빨간색 직선**을 긋습니다. 즉, 수많은 점들의 한가운데를 가장 공평하게 관통하는 평균적인 변화 방향을 찾는 과정입니다.

3. **노란색 점선 및 별표 (미래 기온 예측)**  
   찾아낸 직선의 기울기(1년마다 기온이 **`{slope:+.4f}℃`**씩 변하는 추세)를 그대로 유지한 채 **{target_year}년**까지 직선을 쭉 연장하면, 그 선이 닿는 높이(**`{predicted_temp:.2f}℃`**)가 바로 모델이 예측한 미래 기온이 됩니다.
""")

# (선택) 원본 데이터 표 확인용 접이식 메뉴
with st.expander(f"📋 {selected_month}월 전체 기온 데이터 및 모델 계산값 표로 보기"):
    display_df = month_df[["일시", "연도", "평균기온(℃)"]].copy()
    display_df["추세선 기온(℃)"] = np.round(y_pred_past, 2)
    display_df["오차(실제-추세)"] = np.round(display_df["평균기온(℃)"] - display_df["추세선 기온(℃)"], 2)
    st.dataframe(display_df, use_container_width=True)
