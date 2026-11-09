import os
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="국가 및 MBTI 유형별 분석기", page_icon="🌍", layout="wide"
)


# 데이터 로드 (pages 폴더 기준 상위 폴더의 csv 파일 경로 지정)
@st.cache_data
def load_data():
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "countriesMBTI_16types.csv"
    )
    return pd.read_csv(csv_path)


df = load_data()

st.title("🌍 국가 및 MBTI 유형별 분석 대시보드")
st.write(
    "사이드바에서 **'국가별 MBTI 분포'** 또는 **'MBTI별 국가 순위'** 모드를 선택해 확인하세요."
)

# 사이드바 분석 모드 선택
analysis_mode = st.sidebar.radio(
    "분석 모드 선택", ["국가별 MBTI 분포", "MBTI별 국가 순위 (Top/Bottom)"]
)

# 공통 색상 생성 함수 (1등: 빨강, 2등~끝: 파란색 그라데이션)
def get_custom_palette(n):
    red_color = "#E63946"  # 1위 강조용 빨간색
    blue_cmap = plt.get_cmap("Blues_r")
    if n <= 1:
        return [red_color]
    blue_colors = [
        mcolors.to_hex(blue_cmap(i)) for i in np.linspace(0.15, 0.75, n - 1)
    ]
    return [red_color] + blue_colors


# ==========================================
# 모드 1: 국가별 MBTI 분포 (기존 기능)
# ==========================================
if analysis_mode == "국가별 MBTI 분포":
    st.sidebar.markdown("---")
    countries = sorted(df["Country"].unique().tolist())
    selected_country = st.sidebar.selectbox("국가를 선택하세요", countries)

    # 데이터 전처리 및 정렬
    country_df = df[df["Country"] == selected_country].melt(
        id_vars=["Country"], var_name="MBTI", value_name="Ratio"
    )
    country_df = country_df.sort_values(by="Ratio", ascending=False).reset_index(
        drop=True
    )

    n_types = len(country_df)
    custom_palette = get_custom_palette(n_types)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader(f"📊 [{selected_country}] MBTI 유형별 순위")
        display_df = country_df.copy()
        display_df["비율 (%)"] = (display_df["Ratio"] * 100).round(2)
        display_df.index = display_df.index + 1
        st.dataframe(
            display_df[["MBTI", "비율 (%)"]],
            use_container_width=True,
            height=560,
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

        ax.set_title(
            f"{selected_country} - MBTI Distribution",
            fontsize=15,
            fontweight="bold",
        )
        ax.set_xlabel("MBTI Type", fontsize=12)
        ax.set_ylabel("Ratio", fontsize=12)
        plt.xticks(rotation=45)

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


# ==========================================
# 모드 2: MBTI별 국가 순위 (신규 기능)
# ==========================================
else:
    st.sidebar.markdown("---")
    mbti_types = [col for col in df.columns if col != "Country"]
    selected_mbti = st.sidebar.selectbox("MBTI 유형을 선택하세요", mbti_types)

    # 선택한 MBTI 기준 내림차순 정렬 (높은 나라부터 낮은 나라까지)
    mbti_df = df[["Country", selected_mbti]].sort_values(
        by=selected_mbti, ascending=False
    ).reset_index(drop=True)
    mbti_df.columns = ["Country", "Ratio"]

    n_countries = len(mbti_df)
    custom_palette = get_custom_palette(n_countries)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader(f"🏆 [{selected_mbti}] 비율이 높은 국가 순위")
        display_df = mbti_df.copy()
        display_df["비율 (%)"] = (display_df["Ratio"] * 100).round(2)
        display_df.index = display_df.index + 1
        st.dataframe(
            display_df[["Country", "비율 (%)"]],
            use_container_width=True,
            height=600,
        )

    with col2:
        st.subheader(f"📊 [{selected_mbti}] 전 세계 국가별 분포 그래프")
        st.info(
            "💡 국가 수가 많아 X축 레이블이 겹칠 수 있으므로, 주요 상위/하위 국가를 중심으로 확인하거나 표를 함께 참고해 주세요."
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        # 158개국이 모두 들어가므로 x축 글씨 크기를 조절하거나 상위권 위주로 시각화
        bars = sns.barplot(
            x="Country",
            y="Ratio",
            data=mbti_df,
            palette=custom_palette,
            ax=ax,
            hue="Country",
            legend=False,
        )

        ax.set_title(
            f"Global Ranking for {selected_mbti}",
            fontsize=15,
            fontweight="bold",
        )
        ax.set_xlabel("Country", fontsize=12)
        ax.set_ylabel("Ratio", fontsize=12)
        
        # 국가 이름이 많으므로 90도 회전
        plt.xticks(rotation=90, fontsize=6)

        st.pyplot(fig)
