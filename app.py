import streamlit as st
import pandas as pd
import plotly.express as px

# ===== 페이지 설정 및 데이터 불러오기 =====
# 가장 먼저 실행되는 st 명령으로 페이지 제목과 레이아웃 설정 # [추가]
st.set_page_config(page_title="Titanic 대시보드", layout="wide")  # [추가]

# 캐싱을 적용하여 titanic.csv 파일을 한 번만 읽어오기
@st.cache_data
def load_data():
    return pd.read_csv("titanic.csv")

df = load_data()

# ===== 데이터 처리 및 그래프 함수 =====
# 조건에 맞는 승객만 필터링하는 함수
def filter_data(df, sexes, classes, age_range):
    min_age, max_age = age_range
    cond_sex = df["sex"].isin(sexes)
    cond_class = df["pclass"].isin(classes)
    cond_age = df["age"].between(min_age, max_age)
    return df[cond_sex & cond_class & cond_age]

# 승객 수, 생존율, 평균 나이를 계산하는 KPI 함수
def kpi(df):
    if df.empty:
        return (0, 0, 0)
    passenger_count = len(df)
    survival_rate = round(df["survived"].mean() * 100, 1)
    mean_age_val = df["age"].mean()
    avg_age = round(mean_age_val, 1) if pd.notna(mean_age_val) else 0
    return (passenger_count, survival_rate, avg_age)

# 객실 등급별 생존율(%) 막대그래프 생성 함수
def class_rate_bar(df):
    rate_df = df.groupby("pclass", as_index=False)["survived"].mean()
    rate_df["survival_rate"] = (rate_df["survived"] * 100).round(1)
    rate_df["pclass"] = rate_df["pclass"].astype(str) + "등급"
    
    fig = px.bar(
        rate_df,
        x="pclass",
        y="survival_rate",
        text="survival_rate",
        title="객실 등급별 생존율(%)",
        labels={"pclass": "객실 등급", "survival_rate": "생존율 (%)"}
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_yaxes(range=[0, 110])
    return fig

# 생존 여부별 나이 히스토그램 생성 함수
def age_hist(df):
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 나이 분포",
        labels={"age": "나이", "survived": "생존 여부 (0: 사망, 1: 생존)"}
    )
    return fig

# ===== 사이드바 필터 =====
st.sidebar.header("검색 조건 필터")

# 성별 다중 선택 (기본값: 전체 선택)
sex_options = df["sex"].unique().tolist()
selected_sexes = st.sidebar.multiselect("성별 선택", options=sex_options, default=sex_options)

# 객실 등급 다중 선택 (기본값: 전체 선택, 정렬)
class_options = sorted(df["pclass"].unique().tolist())
selected_classes = st.sidebar.multiselect("객실 등급 선택", options=class_options, default=class_options)

# 나이 범위 슬라이더 (0~80세)
selected_age_range = st.sidebar.slider("나이 범위", min_value=0, max_value=80, value=(0, 80))

# 사이드바 조건을 적용해 데이터 필터링
filtered_df = filter_data(df, selected_sexes, selected_classes, selected_age_range)

# ===== 본문 화면 =====
st.title("타이타닉, 누가 살아남았나?")

# 필터링된 데이터로 KPI 3개 계산
count, rate, avg_age = kpi(filtered_df)

# 3개의 열로 나누어 KPI 숫자 카드 배치
col1, col2, col3 = st.columns(3)
col1.metric("승객 수", f"{count}명")
col2.metric("생존율", f"{rate}%")
col3.metric("평균 나이", f"{avg_age}세")

# KPI 아래 2개의 열로 나누어 Plotly 차트 배치 # [추가]
chart_col1, chart_col2 = st.columns(2)  # [추가]
with chart_col1:  # [추가]
    st.plotly_chart(class_rate_bar(filtered_df), use_container_width=True)  # [추가]
with chart_col2:  # [추가]
    st.plotly_chart(age_hist(filtered_df), use_container_width=True)  # [추가]

# 맨 아래 접기 영역 안에 필터링된 데이터 표 출력 # [추가]
with st.expander("데이터 보기"):  # [추가]
    st.dataframe(filtered_df)  # [추가]
