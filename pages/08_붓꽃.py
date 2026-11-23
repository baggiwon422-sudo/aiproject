import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 1. Page Configuration
st.set_page_config(
    page_title="Iris Prediction App", page_icon="🌸", layout="centered"
)

st.title("🌸 Iris Species Prediction App")
st.write("Adjust the sliders below to predict the Iris species!")

# 2. Load Data and Train Model (Cached)
@st.cache_data
def load_data_and_model():
  iris = load_iris()
  df = pd.DataFrame(iris.data, columns=iris.feature_names)
  df.columns = [
      "sepal length",
      "sepal width",
      "petal length",
      "petal width",
  ]
  df["species"] = iris.target_names[iris.target]

  X = df[["petal length", "petal width"]]
  y = iris.target

  model = RandomForestClassifier(random_state=42)
  model.fit(X, y)

  return df, model, iris.target_names


df, model, target_names = load_data_and_model()

# 3. Input Controls (Sliders in Main Body)
st.subheader("🔍 Input Features")
col1, col2 = st.columns(2)

with col1:
  user_petal_length = st.slider(
      "Petal Length (cm)",
      min_value=float(df["petal length"].min()),
      max_value=float(df["petal length"].max()),
      value=float(df["petal length"].mean()),
      step=0.1,
  )

with col2:
  user_petal_width = st.slider(
      "Petal Width (cm)",
      min_value=float(df["petal width"].min()),
      max_value=float(df["petal width"].max()),
      value=float(df["petal width"].mean()),
      step=0.1,
  )

# 4. Prediction
input_data = pd.DataFrame(
    [[user_petal_length, user_petal_width]],
    columns=["petal length", "petal width"],
)
prediction = model.predict(input_data)[0]
predicted_species = target_names[prediction]

# 5. Result Output
st.subheader("🎯 Prediction Result")
st.success(f"Predicted Species: **[{predicted_species}]**")

# 6. Visualization (Scatter Plot without any text/labels)
st.subheader("📊 Visualization")
fig, ax = plt.subplots(figsize=(8, 6))

# Scatter plot of dataset (legend=False로 범례 제거)
sns.scatterplot(
    data=df,
    x="petal length",
    y="petal width",
    hue="species",
    palette="Set2",
    s=70,
    alpha=0.8,
    ax=ax,
    legend=False,
)

# Mark user input with a gold star
ax.scatter(
    user_petal_length,
    user_petal_width,
    color="gold",
    marker="*",
    s=300,
    edgecolor="black",
    linewidth=1.2,
    zorder=5,
)

# 그래프 내부의 모든 글자(제목, 축 레이블 등) 제거
ax.set_title("")
ax.set_xlabel("")
ax.set_ylabel("")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)
