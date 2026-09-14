import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="영화 박스오피스 분석 App",
    layout="wide",
)


# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data를 사용하면 데이터를 매번 새로 불러오지 않고 저장해두어 앱이 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치가 포함된 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환 (yyyy-mm-dd)
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 순서대로 정렬
    df = df.sort_values(by="기준일자").reset_index(drop=True)

    return df


# 데이터 로드
df = load_data()

# 앱 제목
st.title("🎬 박스오피스 데이터 분석 웹앱")
st.markdown("---")

# [3. 영화 선택 기능]
# 영화별 최대 누적관객수를 구해서 내림차순 정렬
movie_rank = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .reset_index()
    .sort_values(by="누적관객수", ascending=False)
)

# 내림차순 정렬된 전체 영화 이름 목록 추출
movie_list = movie_rank["영화명"].tolist()

# 사이드바에 영화 선택 드롭다운 생성
st.sidebar.header("🔍 옵션 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요:", movie_list)

# 선택한 영화의 데이터 필터링
filtered_df = df[df["영화명"] == selected_movie]

# --------------------------------------------------
# [구역 1] 일별 관객수 추이 (선그래프)
# --------------------------------------------------
st.header("1. 일별 관객수 추이")

# Plotly를 사용하여 기준일자별 해당일관객수 선그래프 생성
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"[{selected_movie}] 일별 관객수 변화 Trend",
    markers=True,  # 데이터 지점에 점 표시
    labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수(명)"},
)

# 그래프 화면에 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 문구
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 초기 관객 집중도 및 주말/평일 관객수 변동 패턴을 파악할 수 있습니다."
)

st.markdown("---")

# --------------------------------------------------
# [구역 2] 누적 관객수 추이 (영역 차트)
# --------------------------------------------------
st.header("2. 누적 관객수 추이")

# Plotly를 사용하여 기준일자별 누적관객수 영역 차트(Area Chart) 생성
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"[{selected_movie}] 누적 관객수 성장 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
)

# 그래프 화면에 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 문구
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 시간 흐름에 따른 {selected_movie}의 총 관객 누적 속도와 주요 관객 증가 구간(흥행 분기점)을 확인할 수 있습니다."
)

st.markdown("---")

# --------------------------------------------------
# [구역 3] 장기 흥행(20일 이상 등장) TOP 5 영화 누적관객수 비교 (수정됨)
# --------------------------------------------------
st.header("3. 장기 흥행 TOP 5 영화 누적관객수 비교")

# 1. 영화명별 등장 일수(행 수) 계산
movie_days = df.groupby("영화명").size()

# 2. 20일 이상 등장한 영화목록만 추출
movies_over_20days = movie_days[movie_days >= 20].index

# 3. 20일 이상 등장한 영화들 중 누적관객수 기준 TOP 5 선정
top5_long_run_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .nlargest(5)
    .index.tolist()
)

# 4. 해당 TOP 5 영화의 전체 데이터 필터링
top5_df = df[df["영화명"].isin(top5_long_run_movies)]

# color="영화명"을 지정하여 영화별로 다른 색상과 범례가 적용되도록 생성
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별 선 색상 분리 및 범례 생성
    title="장기 흥행(TOP 10 20일 이상 차트인) TOP 5 영화 추이 비교",
    labels={
        "기준일자": "날짜",
        "누적관객수": "누적 관객수(명)",
        "영화명": "영화 제목",
    },
)

# 그래프 화면에 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 설명 문구
st.info(
    "💡 **이 그래프로 알 수 있는 것:** TOP 10 순위에 20일 이상 머무르며 롱런(Long-run)에 성공한 핵심 상위 5개 영화의 장기 누적관객수 동원 속도와 성장 곡선을 비교할 수 있습니다."
)
