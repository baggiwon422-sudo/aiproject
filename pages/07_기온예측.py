import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeRegressor

# 페이지 기본 설정
st.set_page_config(
    page_title="기온 예측 알고리즘 비교기",
    page_icon="🌡️",
    layout="wide"
)

# 1. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8")

    df.columns = df.columns.str.strip()

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    extracted = df["일시"].astype(str).str.extract(r"^([A-Za-z]+)-(\d{2})$")
    df["월"] = extracted[0].map(month_map)
    yy = extracted[1].astype(float)

    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)
    df = df.dropna(subset=["연도", "월", "평균기온(℃)"]).copy()
    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'temperature.csv' 파일을 찾을 수 없습니다. 같은 폴더에 파일을 위치시켜 주세요.")
    st.stop()

# 2. 타이틀 및 사이드바 설정
st.title("🌡️ 머신러닝 알고리즘별 월별 평균기온 예측 및 비교")
st.markdown("3가지 대표 머신러닝 알고리즘(**선형회귀**, **다항회귀**, **의사결정나무**)을 선택해 미래 기온을 예측하고 작동 방식의 차이를 비교해 보세요.")

st.sidebar.header("⚙️ 예측 및 비교 설정")

selected_month = st.sidebar.selectbox(
    "1. 분석할 월(Month) 선택",
    options=list(range(1, 13)),
    index=7,  # 기본값: 8월
    format_func=lambda x: f"{x}월"
)

target_year = st.sidebar.number_input(
    "2. 예측할 연도(Year) 입력",
    min_value=1910,
    max_value=2150,
    value=2035,
    step=1
)

algo_options = [
    "선형회귀 (Linear Regression)",
    "다항회귀 - 2차 곡선 (Polynomial Regression)",
    "의사결정나무 (Decision Tree)"
]

selected_algo = st.sidebar.radio(
    "3. 메인으로 자세히 볼 알고리즘 선택",
    options=algo_options,
    index=0
)

compare_all = st.sidebar.checkbox(
    "🔥 3개 알고리즘 그래프 한눈에 동시 비교하기",
    value=True,
    help="체크하면 선택한 알고리즘과 나머지 2개 알고리즘의 예측선을 한 그래프에서 동시에 비교할 수 있습니다."
)

show_residuals = st.sidebar.checkbox(
    "선택한 알고리즘의 오차(잔차) 점선 표시",
    value=True
)

# 3. 데이터 필터링 및 3가지 모델 학습
month_df = df[df["월"] == selected_month].sort_values("연도").reset_index(drop=True)
X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

last_year = int(month_df["연도"].max())
min_year = int(month_df["연도"].min())

# 미래까지 이어지는 연속 연도 배열 생성 (곡선과 계단을 매끄럽게 그리기 위함)
max_plot_year = max(last_year, target_year)
X_grid = np.arange(min_year, max_plot_year + 1).reshape(-1, 1)

# 모델 1: 선형회귀
model_lr = LinearRegression()
model_lr.fit(X, y)

# 모델 2: 다항회귀 (2차 곡선)
model_poly = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
model_poly.fit(X, y)

# 모델 3: 의사결정나무 (깊이 4로 제한하여 구간별 평균 시각화)
model_dt = DecisionTreeRegressor(max_depth=4, random_state=42)
model_dt.fit(X, y)

models_info = {
    "선형회귀 (Linear Regression)": {
        "model": model_lr,
        "color": "#EF4444",  # 빨강
        "dash": "solid",
        "pred_past": model_lr.predict(X),
        "pred_grid": model_lr.predict(X_grid),
        "pred_target": model_lr.predict([[target_year]])[0],
        "short_name": "선형회귀 (직선)"
    },
    "다항회귀 - 2차 곡선 (Polynomial Regression)": {
        "model": model_poly,
        "color": "#10B981",  # 초록
        "dash": "solid",
        "pred_past": model_poly.predict(X),
        "pred_grid": model_poly.predict(X_grid),
        "pred_target": model_poly.predict([[target_year]])[0],
        "short_name": "다항회귀 (곡선)"
    },
    "의사결정나무 (Decision Tree)": {
        "model": model_dt,
        "color": "#8B5CF6",  # 보라
        "dash": "solid",
        "pred_past": model_dt.predict(X),
        "pred_grid": model_dt.predict(X_grid),
        "pred_target": model_dt.predict([[target_year]])[0],
        "short_name": "의사결정나무 (계단)"
    }
}

current_info = models_info[selected_algo]
recent_10y_avg = month_df.tail(10)["평균기온(℃)"].mean()

# 4. 상단 KPI 카드: 3개 알고리즘 예측 결과 한눈에 비교
st.subheader(f"🎯 {target_year}년 {selected_month}월 알고리즘별 예측 기온 비교")
col1, col2, col3 = st.columns(3)

for col, (name, info) in zip([col1, col2, col3], models_info.items()):
    pred_val = info["pred_target"]
    diff = pred_val - recent_10y_avg
    is_selected = " ✅ (현재 선택)" if name == selected_algo else ""
    col.metric(
        label=f"{info['short_name']}{is_selected}",
        value=f"{pred_val:.2f} ℃",
        delta=f"최근 10년 평균 대비 {diff:+.2f} ℃"
    )

# 5. 그래프 시각화 (Plotly)
fig = go.Figure()

# (1) 선택한 알고리즘의 오차(잔차) 표시
if show_residuals:
    res_x, res_y = [], []
    for yr, actual, pred in zip(month_df["연도"], y, current_info["pred_past"]):
        res_x.extend([yr, yr, None])
        res_y.extend([actual, pred, None])

    fig.add_trace(go.Scatter(
        x=res_x,
        y=res_y,
        mode="lines",
        line=dict(color="rgba(150, 150, 150, 0.45)", width=1, dash="dot"),
        name=f"오차(잔차): {current_info['short_name']}",
        hoverinfo="skip"
    ))

# (2) 실제 관측된 과거 평균기온
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=y,
    mode="markers+lines",
    marker=dict(size=6, color="#3B82F6", opacity=0.75),
    line=dict(color="rgba(59, 130, 246, 0.2)", width=1),
    name=f"실제 {selected_month}월 평균기온",
    hovertemplate="<b>%{x}년</b><br>실제 기온: %{y:.1f}℃<extra></extra>"
))

# (3) 알고리즘 예측선 그리기
years_flat = X_grid.flatten()
past_mask = years_flat <= last_year
future_mask = years_flat >= last_year

for name, info in models_info.items():
    if not compare_all and name != selected_algo:
        continue

    is_main = (name == selected_algo)
    line_width = 3.5 if is_main else 2.0
    line_opacity = 1.0 if is_main else 0.55

    # 과거 학습 구간 선
    fig.add_trace(go.Scatter(
        x=years_flat[past_mask],
        y=info["pred_grid"][past_mask],
        mode="lines",
        line
