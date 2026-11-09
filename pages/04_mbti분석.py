import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석기", page_icon="🌍", layout="wide"
)


# 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("countriesMBTI_16types.csv")


df = load_data()

st.title("🌍 국가별 MBTI 분포 분석기")
st.write(
    "국가를 선택하면 해당 국가의 16가지 MBTI 비율을 확인하실 수 있습니다."
)

# 사이드바 국가 선택
countries = sorted(df["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("국가를 선택하세요", countries)

# 선택한 국가 데이터 전처리 및 비율 내림차순 정렬
country_df = df[df["Country"] == selected_country].melt(
    id_vars=["Country"], var_name="MBTI", value_name="Ratio"
)
country_df = country_df.sort_values(by="Ratio", ascending=False).reset_index(
    drop=True
)

# 색상 그라데이션 설정: 1등은 빨간색, 2~16등은 진한 파란색에서 밝은 파란색으로 흐려지는 그라데이션
n_types = len(country_df)
red_color = "#E63946"  # 1위 강조용 빨간색
blue_cmap = plt.get_cmap("Blues_r")
# 2위부터 16위까지 파란색 계열 그라데이션 색상 추출
blue_colors = [
    mcolors.to_hex(blue_cmap(i)) for i in np.linspace(0.15, 0.75, n_types - 1)
]
custom_palette = [red_color] + blue_colors

# 레이아웃 구성
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader(f"📊 [{selected_country}] MBTI 유형별 순위")
    display_df = country_df.copy()
    display_df["비율 (%)"] = (display_df["Ratio"] * 100).round(2)
    display_df.index = display_df.index + 1
    st.dataframe(
        display_df[["MBTI", "비율 (%)"]], use_container_width=True, height=560
    )

with col2:
    st.subheader(f"📈 [{selected_country}] MBTI 비율 그래프")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(
        x="MBTI",
        y="Ratio",
        data=country_df,
        palette=custom_palette,
        ax=ax,
        hue="MBTI",
        legend=False,
    )

    # 그래프 세부 디자인
    ax.set_title(
        f"{selected_country} - MBTI Distribution", fontsize=15, fontweight="bold"
    )
    ax.set_xlabel("MBTI Type", fontsize=12)
    ax.set_ylabel("Ratio", fontsize=12)
    plt.xticks(rotation=45)

    # 막대 상단 퍼센트 표시
    for bar in bars.patches:
        height = bar.get_height()
        ax.annotate(
            f"{height * 100:.1f}%",
            (bar.get_x() + bar.get_width() / 2, height),
            ha="center",
            va="bottom",
            fontsize=8,
            xytext=(0, 3),
            textcoords="offset points",
        )

    st.pyplot(fig)
