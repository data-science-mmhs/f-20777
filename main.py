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

st.divider()

# ---------------------------------------------------------
# 세 번째 그래프: 총 관객수 히스토그램 (Histogram)
# ---------------------------------------------------------
st.header("3. 총 관객수 분포 (히스토그램)")

# 히스토그램 생성
fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    labels={'total_audi': '총 관객수', 'count': '영화 수'},
    title="영화별 총 관객수 구간 분포"
)

fig_hist.update_traces(
    hovertemplate='<b>관객수 구간: %{x}</b><br>영화 수: %{y}편<extra></extra>'
)

fig_hist.update_layout(
    yaxis_title="영화 수",
    xaxis_title="총 관객수"
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 관객수가 많은 영화 정보 자동 추출
top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

# 그래프 해석 구역
st.info(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 관객수 하위 구간(약 100만~200만 명 이하)에 집중되어 있는 반면, "
    f"가장 많은 관객을 동원한 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,}명)으로 극소수의 흥행작이 상위 구간에 위치함을 볼 수 있습니다."
)

st.divider()

# ---------------------------------------------------------
# 네 번째 그래프: 개봉일 스크린수 vs 총 관객수 (산점도)
# ---------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객수의 관계")

# 산점도 생성
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
    title="개봉일 스크린수 대비 총 관객수 (장르별 구분)"
)

# 툴팁 설정 (마우스 올리면 영화명, 장르, 개봉일 스크린수, 총 관객수 표시)
fig_scatter.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>장르: %{fullData.name}<br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>'
)

st.plotly_chart(fig_scatter, use_container_width=True)

# 그래프 해석 구역
st.info("**이 그래프로 알 수 있는 것:** 개봉일 스크린 확보 수준이 최종 흥행(총 관객수)에 미치는 상관관계를 확인할 수 있으며, 장르별 선호도와 배급 규모 간의 특성을 비교해 볼 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 다섯 번째 그래프: 주력 장르별 총 관객수 분포 (상자 그림 / Boxplot)
# ---------------------------------------------------------
st.header("5. 주요 장르별 총 관객수 분포 (10편 이상 장르)")

# 영화 수 10편 이상인 장르 필터링
genre_counts_series = df['genre'].value_counts()
main_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
df_filtered = df[df['genre'].isin(main_genres)]

# 박스플롯 생성 (outliers 표시 포함)
fig_box = px.box(
    df_filtered,
    x='genre',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    points='outliers',  # 아웃라이어(이상치) 점 표시
    labels={
        'genre': '장르',
        'total_audi': '총 관객수'
    },
    title="주요 장르별 총 관객수 상자 그림 (영화 수 10편 이상 대상)"
)

# 툴팁에 영화명 및 총 관객수 표시
fig_box.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>총 관객수: %{y:,}명<extra></extra>'
)

st.plotly_chart(fig_box, use_container_width=True)

# 그래프 해석 구역
st.info("**이 그래프로 알 수 있는 것:** 주요 장르별 흥행의 중간값(중앙값)과 범위를 한눈에 비교할 수 있으며, 상자 밖의 점(이상치)을 통해 동일 장르 내에서 이례적으로 대흥행을 거둔 작품을 확인할 수 있습니다.")
