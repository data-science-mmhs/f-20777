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
    
    # 장르 전처리: 세로막대 기호(|)로 분리된 경우 첫 번째 장르만 추출
    if 'genre' in df.columns:
        df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if x and x != 'nan' else '기타')
        
    return df

try:
    df = load_data()
    
    # 메인 섹션: 장르별 영화 편수 도넛 그래프
    st.subheader("1. 장르별 영화 편수 분포")
    
    # 장르별 빈도 계산
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '영화 편수']
    
    # Plotly 도넛 그래프 생성
    fig = px.pie(
        genre_counts, 
        values='영화 편수', 
        names='장르', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 툴팁 및 레이아웃 설정 (마우스 호버 시 편수 및 비율 표시)
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
    )
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend_title_text='장르'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 그래프 해석 구역
    st.divider()
    with st.container():
        st.markdown("💡 **이 그래프로 알 수 있는 것**")
        st.info("박스오피스 상위권 영화 중 특정 주요 장르가 차지하는 비중과 전체적인 장르 다양성 분포를 한눈에 확인할 수 있습니다.")
        
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
