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
    "아래의 슬라이더를 조절하여 **꽃잎 길이**와 **꽃잎 너비**를 입력하면, 머신러닝 모델이 품종을 예측해 드립니다!"
)

st.info(
    "🤖 **사용된 알고리즘:** 앙상블 학습 기반의 **랜덤 포레스트 (Random Forest"
    " Classifier)**"
)

# 2. 데이터 로드 및 모델 학습 (캐싱 활용)
@st.cache_data
def load_data_and_model():
  iris = load_iris()
  df = pd.DataFrame(iris.data, columns=iris.feature_names)
  df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
  df["species"] = iris.target_names[iris.target]

  X = df[["petal_length", "petal_width"]]
  y = iris.target

  model = RandomForestClassifier(random_state=42)
  model.fit(X, y)

  return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 3. 본문 영역에 입력 컨트롤(슬라이더) 배치
st.subheader("🔍 입력 변수 설정")
col1, col2 = st.columns(2)

with col1:
  user_petal_length = st.slider(
      "꽃잎 길이 (Petal Length, cm)",
      min_value=float(df["petal_length"].min()),
      max_value=float(df["petal_length"].max()),
      value=float(df["petal_length"].mean()),
      step=0.1,
  )

with col2:
  user_petal_width = st.slider(
      "꽃잎 너비 (Petal Width, cm)",
      min_value=float(df["petal_width"].min()),
      max_value=float(df["petal_width"].max()),
      value=float(df["petal_width"].mean()),
      step=0.1,
  )

# 4. 예측 수행
input_data = pd.DataFrame(
    [[user_petal_length, user_petal_width]],
    columns=["petal_length", "petal_width"],
)
prediction = model.predict(input_data)[0]
predicted_species = target_names[prediction]

# 5. 결과 출력
st.subheader("🎯 예측 결과")
st.success(
    f"입력하신 조건(꽃잎 길이: **{user_petal_length}cm**, 꽃잎 너비:"
    f" **{user_petal_width}cm**)에 따른 예측 품종은 **[{predicted_species}]**"
    " 입니다!"
)

# 6. 시각화 (그래프 내부 글자 깨짐 방지를 위해 축 이름은 영문으로 깔끔하게 처리)
st.subheader("📊 꽃잎 특징 분포 및 내 입력 위치")
fig, ax = plt.subplots(figsize=(8, 6))

sns.scatterplot(
    data=df,
    x="petal_length",
    y="petal_width",
    hue="species",
    palette="Set2",
    s=70,
    alpha=0.8,
    ax=ax,
)

ax.scatter(
    user_petal_length,
    user_petal_width,
    color="gold",
    marker="*",
    s=300,
    edgecolor="black",
    linewidth=1.2,
    label="My Input",
    zorder=5,
)

ax.set_title("Petal Length vs Petal Width", fontsize=14)
ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)
