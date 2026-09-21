import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 - 분포와 관계")
st.markdown("1년간 박스오피스 10위권에 든 영화 중 개봉작 216편의 데이터 분석 및 시각화 앱입니다.")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 전처리: 결측값(NaN/float)을 먼저 처리한 후 첫 번째 장르만 추출
    if 'genre' in df.columns:
        df['genre'] = (
            df['genre']
            .fillna('기타')
            .astype(str)
            .apply(lambda x: x.split('|')[0].strip() if x else '기타')
        )
        
    # 개봉월 전처리: openDt(또는 release_date) 컬럼에서 월(Month) 정보 추출
    date_col = 'openDt' if 'openDt' in df.columns else ('release_date' if 'release_date' in df.columns else None)
    if date_col:
        df['open_month'] = pd.to_datetime(df[date_col].astype(str), errors='coerce').dt.month
        df['open_month_str'] = df['open_month'].apply(lambda x: f"{int(x)}월" if pd.notnull(x) else "미상")
    else:
        df['open_month_str'] = "미상"
        
    return df

try:
    df = load_data()
    
    # 첫 번째 그래프: 장르별 영화 편수 도넛 그래프
    st.subheader("1. 장르별 영화 편수 분포")
    
    # 장르별 빈도 계산
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '영화 편수']
    
    # Plotly 도넛 그래프 생성
    fig1 = px.pie(
        genre_counts, 
        values='영화 편수', 
        names='장르', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 툴팁 및 레이아웃 설정 (마우스 호버 시 편수 및 비율 표시)
    fig1.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
    )
    
    fig1.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend_title_text='장르'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 1 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("박스오피스 상위권 영화 중 특정 주요 장르가 차지하는 비중과 전체적인 장르 다양성 분포를 한눈에 확인할 수 있습니다.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 두 번째 그래프: 장르 및 영화별 총 관객 수 트리맵
    st.subheader("2. 장르 및 영화별 총 관객 수 분포 (트리맵)")
    
    fig2 = px.treemap(
        df,
        path=[px.Constant("전체"), 'genre', 'movieNm'],
        values='total_audi',
        color='genre',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig2.update_traces(
        hovertemplate="<b>영화명/구분:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명<extra></extra>"
    )
    
    fig2.update_layout(
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 그래프 2 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("장르별 총 관객 수의 규모와 각 장르 내에서 어떤 영화가 박스오피스 흥행을 주도했는지 한눈에 비교할 수 있습니다.")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 세 번째 그래프: 총 관객 수 히스토그램
    st.subheader("3. 총 관객 수(total_audi) 분포 히스토그램")
    
    fig3 = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        labels={'total_audi': '총 관객 수 (명)', 'count': '영화 수'},
        color_discrete_sequence=['#636EFA']
    )
    
    fig3.update_traces(
        hovertemplate="<b>관객 수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
    )
    
    fig3.update_layout(
        xaxis_title="총 관객 수 (명)",
        yaxis_title="영화 수 (편)",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # 데이터 기반 분석 문구 동적 계산 (최대 관객 영화 정보)
    top_movie = df.loc[df['total_audi'].idxmax()]
    top_movie_name = top_movie['movieNm']
    top_movie_audi = top_movie['total_audi']
    
    # 그래프 3 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info(
            f"대부분의 영화가 총 관객 수 **200만 명 이하**의 하위 구간에 모여 있으며, "
            f"가장 관객 수가 많은 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,}명)입니다."
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 네 번째 그래프: 개봉일 스크린수 vs 총 관객 수 산점도
    st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)")
    
    fig4 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        hover_data={'first_scrn': ':,', 'total_audi': ':,', 'genre': True},
        labels={'first_scrn': '개봉일 스크린 수 (개)', 'total_audi': '총 관객 수 (명)', 'genre': '장르'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig4.update_traces(
        hovertemplate="<b>%{hovertext}</b><br><br><b>장르:</b> %{customdata[0]}<br><b>개봉일 스크린 수:</b> %{x:,}개<br><b>총 관객 수:</b> %{y:,}명<extra></extra>"
    )
    
    fig4.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # 그래프 4 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("개봉일 스크린 수가 많을수록 총 관객 수가 증가하는 경향을 보이지만, 스크린 수가 적음에도 높은 흥행을 기록한 영화나 스크린 수에 비해 관객 수가 적은 영화 등 장르별 차이를 함께 확인할 수 있습니다.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 다섯 번째 그래프: 영화 10편 이상 장르의 총 관객 수 상자 그림(Boxplot)
    st.subheader("5. 영화 10편 이상 장르별 총 관객 수 분포 (상자 그림)")
    
    # 영화 편수가 10편 이상인 장르 필터링
    genre_counts_series = df['genre'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index
    df_major_genres = df[df['genre'].isin(major_genres)]
    
    fig5 = px.box(
        df_major_genres,
        x='genre',
        y='total_audi',
        color='genre',
        hover_name='movieNm',
        points='outliers',
        labels={'genre': '장르', 'total_audi': '총 관객 수 (명)'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig5.update_traces(
        hovertemplate="<b>영화명:</b> %{hovertext}<br><b>총 관객 수:</b> %{y:,}명<extra></extra>"
    )
    
    fig5.update_layout(
        xaxis_title="장르 (10편 이상)",
        yaxis_title="총 관객 수 (명)",
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    
    # 그래프 5 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("주요 장르별 관객 수의 중앙값과 대다수 영화의 관객 수 범위를 비교할 수 있으며, 상자 밖의 점(이상치)을 통해 해당 장르에서 압도적인 흥행을 기록한 대표 영화들을 한눈에 확인할 수 있습니다.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 여섯 번째 그래프: 개봉 첫 주 관객 수가 반영된 버블 차트
    st.subheader("6. 개봉일 스크린 수, 총 관객 수, 개봉 첫 주 관객 수의 관계 (버블 차트)")
    
    fig6 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        size='first_week_audi',
        color='genre',
        hover_name='movieNm',
        hover_data={'first_scrn': ':,', 'total_audi': ':,', 'first_week_audi': ':,', 'genre': True},
        labels={
            'first_scrn': '개봉일 스크린 수 (개)', 
            'total_audi': '총 관객 수 (명)', 
            'first_week_audi': '개봉 첫 주 관객 수 (명)',
            'genre': '장르'
        },
        size_max=50,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig6.update_traces(
        hovertemplate="<b>%{hovertext}</b><br><br><b>장르:</b> %{customdata[0]}<br><b>개봉일 스크린 수:</b> %{x:,}개<br><b>총 관객 수:</b> %{y:,}명<br><b>개봉 첫 주 관객 수:</b> %{marker.size:,}명<extra></extra>"
    )
    
    fig6.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    
    # 그래프 6 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("버블의 크기(개봉 첫 주 관객 수)를 통해 초반 흥행 화제성(초반 집객력)이 최종 총 관객 수 및 개봉일 스크린 수 확보와 얼마나 밀접하게 연관되어 있는지 입체적으로 비교 분석할 수 있습니다.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 일곱 번째 그래프: 제작 국가 -> 장르 선버스트 그래프 (영화 편수 기반)
    st.subheader("7. 제작 국가 및 장르별 영화 편수 분포 (선버스트)")
    
    # 국가별, 장르별 영화 편수 집계
    df_nation_genre = df.groupby(['nation', 'genre']).size().reset_index(name='movie_count')
    
    fig7 = px.sunburst(
        df_nation_genre,
        path=['nation', 'genre'],
        values='movie_count',
        color='nation',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig7.update_traces(
        hovertemplate="<b>구분:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>상위 계층 대비 비율:</b> %{percentParent:.1%}<extra></extra>"
    )
    
    fig7.update_layout(
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig7, use_container_width=True)
    
    # 그래프 7 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("제작 국가별 전체 영화 수의 비중과 함께, 각 국가 내부에서 주로 제작·수입된 장르별 구성 비율을 다층 원형 구조로 한눈에 탐색할 수 있습니다.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 여덟 번째 그래프: 개봉월별 장르 분포 (히트맵)
    st.subheader("8. 개봉월별 장르 분포 (밀도 히트맵)")
    
    # 월 순서 정렬을 위한 데이터 정리
    df_valid_month = df[df['open_month'].notnull()].copy()
    df_valid_month['open_month'] = df_valid_month['open_month'].astype(int)
    
    # 개봉월과 장르 조합별 영화 편수 계산
    month_genre_counts = df_valid_month.groupby(['open_month', 'genre']).size().reset_index(name='movie_count')
    month_genre_counts['month_label'] = month_genre_counts['open_month'].apply(lambda x: f"{x}월")
    
    # 1월부터 12월까지 순서대로 배치하기 위한 Pivot Table
    pivot_df = month_genre_counts.pivot(index='genre', columns='open_month', values='movie_count').fillna(0)
    month_columns = [f"{m}월" for m in pivot_df.columns]
    
    fig8 = px.imshow(
        pivot_df.values,
        labels=dict(x="개봉월", y="장르", color="개봉 편수"),
        x=month_columns,
        y=pivot_df.index,
        color_continuous_scale="Blues",
        text_auto=True
    )
    
    fig8.update_traces(
        hovertemplate="<b>개봉월:</b> %{x}<br><b>장르:</b> %{y}<br><b>개봉 영화 수:</b> %{z}편<extra></extra>"
    )
    
    fig8.update_layout(
        xaxis_title="개봉월",
        yaxis_title="장르",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig8, use_container_width=True)
    
    # 그래프 8 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info(
            "• **계절성 및 시즌별 선호 장르**: 여름/겨울 성수기(7~8월, 12~1월)나 명절 시즌(추석/설날)에 액션, 애니메이션, 코미디 등 특정 장르가 집중적으로 개봉하는 경향을 확인할 수 있습니다.\n\n"
            "• **월별 장르 집중도**: 특정 월에 특정 장르 영화가 몰리는 현상이나, 연중 꾸준히 개봉하는 장르와 특정 시기에만 등장하는 장르의 차이를 비교할 수 있습니다."
        )

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
