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
    hovertemplate='<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>'
)

st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 해석 구역
st.info("**이 그래프로 알 수 있는 것:** 박스오피스 상위권 영화 중 가장 큰 비중을 차지하는 주력 장르와 장르별 편수 분포를 한눈에 파악할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객수 (트리맵)
# ---------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객수 분포")

# 계층구조(장르 > 영화명) 및 타일 크기(총 관객수) 설정
fig_treemap = px.treemap(
    df,
    path=['genre', 'movieNm'],
    values='total_audi',
    title="장르 및 영화별 총 관객수 (크기: 총 관객수)"
)

# 툴팁에 영화명(또는 장르명)과 총 관객수 표시
fig_treemap.update_traces(
    hovertemplate='<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>'
)

st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 해석 구역
st.info("**이 그래프로 알 수 있는 것:** 어떤 장르가 전체 관객수를 주로 견인했는지, 그리고 각 장르 내에서 어떤 영화가 가장 큰 관객 비중을 차지했는지 직관적으로 비교할 수 있습니다.")
