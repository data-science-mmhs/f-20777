import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 전처리 (세로막대 기호 '|' 구분자 처리하여 첫 번째 장르만 추출)
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0] if x else x)
    return df

df = load_data()

# ---------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
st.header("1. 장르별 영화 분포")

# 장르별 영화 수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

# 플롯리 도넛 그래프 생성
fig_donut = px.pie(
    genre_counts,
    names='genre',
    values='count',
    hole=0.4,
    title="장르별 영화 편수 비율"
)

# 툴팁에 편수와 비율 명확히 표시
fig_donut.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}'
)

st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 해석/설명 구역
st.info("**이 그래프로 알 수 있는 것:** 박스오피스 상위권 영화 중 가장 큰 비중을 차지하는 주력 장르와 장르별 편수 분포를 한눈에 파악할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 추가 분석 구역 (확장성을 위한 기본 틀)
# ---------------------------------------------------------
st.header("2. 개봉일 스크린수와 총 관객수 관계")

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    labels={
        'first_scrn': '개봉일 스크린수',
        'total_audi': '총 관객수',
        'genre': '장르'
    },
    title="개봉일 스크린수 대비 총 관객수"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** 개봉 초기의 스크린 확보 수준이 최종 관객수 흥행에 미치는 상관관계를 확인할 수 있습니다.")
