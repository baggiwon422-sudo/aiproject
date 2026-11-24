import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# 1. 페이지 설정
st.set_page_config(
    page_title="Iris 다중 모델 비교 예측 앱", page_icon="🌸", layout="centered"
)

st.title("🌸 붓꽃(Iris) 다중 알고리즘 비교 예측 앱")
st.write(
    "아래의 슬라이더로 **꽃잎 길이**와 **꽃잎 너비**를 입력하면, 3가지 머신러닝 분류 모델이 각각 어떤 예측을 내놓는지 비교할 수 있습니다!"
)

# 2. 데이터 로드 및 모델 3개 학습 (캐싱 활용)
@st.cache_data
def load_data_and_models():
  iris = load_iris()
  df = pd.DataFrame(iris.data, columns=iris.feature_names)
  df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
  df["species"] = iris.target_names[iris.target]

  X = df[["petal_length", "petal_width"]]
  y = iris.target

  # 3가지 분류 알고리즘 정의
  models = {
      "랜덤 포레스트 (Random Forest)": RandomForestClassifier(random_state=42),
      "서포트 벡터 머신 (SVM)": SVC(probability=True, random_state=42),
      "K-최근접 이웃 (KNN)": KNeighborsClassifier(n_neighbors=5),
  }

  # 각 모델 학습
  fitted_models = {}
  for name, model in models.items():
    model.fit(X, y)
    fitted_models[name] = model

  return df, fitted_models, iris.target_names


df, models, target_names = load_data_and_models()

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

input_data = pd.DataFrame(
    [[user_petal_length, user_petal_width]],
    columns=["petal_length", "petal_width"],
)

# 4. 3개 알고리즘 예측 결과 비교 출력
st.subheader("🎯 3개 알고리즘 예측 결과 비교")

results = []
for name, model in models.items():
  pred_idx = model.predict(input_data)[0]
  pred_species = target_names[pred_idx]
  results.append({"알고리즘": name, "예측 품종": pred_species})

results_df = pd.DataFrame(results)
st.table(results_df)

# 5. 시각화 (그래프 내부 글자 깨짐 방지를 위해 축 이름은 안전한 영문 사용)
st.subheader("📊 특징 분포 및 내 입력 위치")
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

# 6. 3개 알고리즘 작동 원리 설명 탭/아코디언 제공
st.subheader("📖 알고리즘별 작동 원리 안내")

tab1, tab2, tab3 = st.tabs(
    ["🌲 랜덤 포레스트", "📐 서포트 벡터 머신 (SVM)", "📍 K-최근접 이웃 (KNN)"]
)

with tab1:
  st.markdown("""
    * **작동 원리:** 수많은 **결정 트리(Decision Tree)**를 숲처럼 여러 개 모아서 구성하는 앙상블 학습 모델입니다.
    * **특징:** 각 나무들이 내린 예측 결과들 중에서 **다수결(Voting)** 방식으로 최종 품종을 결정하기 때문에 과적합이 적고 정확도가 매우 높습니다.
    """)

with tab2:
  st.markdown("""
    * **작동 원리:** 데이터들을 공간에 점으로 찍고, 서로 다른 품종의 데이터들을 가장 안전하게 갈라놓을 수 있는 **최적의 경계선(Decision Boundary / 초평면)**을 찾는 알고리즘입니다.
    * **특징:** 경계선과 가장 가까운 데이터(서포트 벡터)를 기준으로 마진을 극대화하여 분류 능력이 뛰어납니다.
    """)

with tab3:
  st.markdown("""
    * **작동 원리:** 새로운 데이터가 들어왔을 때, 공간상에서 **가장 가까이에 있는 K개의 이웃 데이터**를 찾아서 그중 가장 많은 분포를 가진 품종으로 따라가는 방식입니다.
    * **특징:** 복잡한 수학적 학습 없이 직관적으로 주변 데이터를 참고하므로 이해하기 쉽고 직관적입니다.
    """)
