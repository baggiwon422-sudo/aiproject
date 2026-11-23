import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 1. 페이지 설정
st.set_page_config(
    page_title="Iris 품종 예측 앱", page_icon="🌸", layout="centered"
)

st.title("🌸 붓꽃(Iris) 품종 예측 및 시각화 앱")
st.write(
    "사이드바에서 **꽃잎 길이**와 **꽃잎 너비**를 조절하여 어떤 품종인지 예측하고, 산소 분포도에서 위치를 확인해보세요!"
)

# 2. 데이터 로드 및 모델 학습 (캐싱 활용)
@st.cache_data
def load_data_and_model():
  iris = load_iris()
  # 보기 편하도록 데이터프레임 구성 (열 이름 매핑)
  df = pd.DataFrame(iris.data, columns=iris.feature_names)
  df.columns = ["꽃받침 길이", "꽃받침 너비", "꽃잎 길이", "꽃잎 너비"]
  df["품종"] = iris.target_names[iris.target]

  # 시각화와 예측을 위해 꽃잎 길이, 너비 및 품종만 활용
  X = df[["꽃잎 길이", "꽃잎 너비"]]
  y = iris.target

  # 랜덤 포레스트 분류 모델 학습
  model = RandomForestClassifier(random_state=42)
  model.fit(X, y)

  return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 3. 사이드바 사용자 입력 (입력 가능 범위 반영)
st.sidebar.header("🔍 입력 변수 설정")
st.sidebar.markdown("사용 가능한 값의 범위를 참고하여 조절하세요.")

user_petal_length = st.sidebar.slider(
    "꽃잎 길이 (cm)",
    min_value=float(df["꽃잎 길이"].min()),
    max_value=float(df["꽃잎 길이"].max()),
    value=float(df["꽃잎 길이"].mean()),
    step=0.1,
)

user_petal_width = st.sidebar.slider(
    "꽃잎 너비 (cm)",
    min_value=float(df["꽃잎 너비"].min()),
    max_value=float(df["꽃잎 너비"].max()),
    value=float(df["꽃잎 너비"].mean()),
    step=0.1,
)

# 4. 예측 수행
input_data = pd.DataFrame(
    [[user_petal_length, user_petal_width]], columns=["꽃잎 길이", "꽃잎 너비"]
)
prediction = model.predict(input_data)[0]
prediction_proba = model.predict_proba(input_data)[0]

predicted_species = target_names[prediction]

# 5. 결과 출력
st.subheader("🎯 예측 결과")
st.success(
    f"입력하신 조건에 따른 예측 품종은 **[{predicted_species}]** 입니다!"
)

# 확률 바차트 표시
proba_df = pd.DataFrame(
    {"품종": target_names, "확률": prediction_proba * 100}
).set_index("품종")
st.write("품종별 예측 확률:")
st.bar_chart(proba_df)

# 6. 시각화 (가로: 꽃잎 길이, 세로: 꽃잎 너비, 노란 별 표시)
st.subheader("📊 꽃잎 특징 분포 및 입력 위치")
fig, ax = plt.subplots(figsize=(8, 6))

# 데이터 분포 산점도 그리기
sns.scatterplot(
    data=df,
    x="꽃잎 길이",
    y="꽃잎 너비",
    hue="품종",
    palette="Set2",
    s=70,
    alpha=0.8,
    ax=ax,
)

# 사용자가 입력한 위치를 노란색 별(*)로 표시
ax.scatter(
    user_petal_length,
    user_petal_width,
    color="gold",
    marker="*",
    s=300,
    edgecolor="black",
    linewidth=1.2,
    label="내 입력값",
    zorder=5,
)

ax.set_title("꽃잎 길이 vs 꽃잎 너비 (분포 및 입력 위치)", fontsize=14)
ax.set_xlabel("꽃잎 길이 (cm)", fontsize=12)
ax.set_ylabel("꽃잎 너비 (cm)", fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)
